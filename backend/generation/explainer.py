from llm.factory import get_llm_client
llm_client=get_llm_client()

def chunk_selector(chunks:list[str],keywords:list[str],max_chunk_lim:int=3)->list[str]:
    if len(chunks)<=max_chunk_lim:
        return chunks
    scored_chunks=[(i,chunk_kw_score(chunk,keywords)) for i,chunk in enumerate(chunks)]
    scored_chunks.sort(key=lambda x:x[1],reverse=True)
    if max(score for _,score in scored_chunks)==0:
        return chunks[:max_chunk_lim]
    selected_chunks_ind=sorted(i for i,_ in scored_chunks[:max_chunk_lim])
    return [chunks[i] for i in selected_chunks_ind]

def chunk_kw_score(chunk:str,keywords:list[str])->float:
    words=chunk.lower().split()
    kw_set=set(kw.lower() for kw in keywords)
    return sum(1 for word in words if word in kw_set)/max(len(words),1)

def difficulty_chunk_limit(difficulty:str)->int:
    return {"easy":3,"medium":5,"hard":10}.get(difficulty,5)

def max_tokens_for_difficulty(difficulty: str) -> int:
    return {"easy": 2000, "medium": 2500, "hard": 3000}.get(difficulty, 2000)


def word_limits_for_difficulty(difficulty: str) -> tuple[int, int]:
    tokens = max_tokens_for_difficulty(difficulty)

    max_words = int(tokens * 0.75)
    min_words = int(max_words * 0.8)

    return min_words, max_words


def build_prompt_for_topic(chunks: list[str], keywords: list[str], difficulty: str) -> str:
    selected_chunks = chunk_selector(chunks, keywords, difficulty_chunk_limit(difficulty))
    min_words, max_words = word_limits_for_difficulty(difficulty)

    context = "\n".join(selected_chunks)
    kw_string = ", ".join(keywords)

    return f"""<s>[INST]
You are an expert study-content generator.

Topic difficulty: {difficulty}
Relevant keywords: {kw_string}

REFERENCE CONTEXT (for grounding only):
{context}

REFERENCE CONTEXT RULES (MANDATORY):
- The reference context is provided ONLY for factual grounding.
- Do NOT copy, quote, summarize, or paraphrase the reference text.
- Do NOT reuse its structure, phrasing, or ordering.
- Generate an ORIGINAL explanation using your own structure and wording.

DIFFICULTY RULES (STRICT):
- EASY: brief, high-level explanation.
- MEDIUM: structured explanation with examples.
- HARD: deep, academic-level explanation with analysis, context, and comparisons.

HARD MODE ENFORCEMENT (MANDATORY IF difficulty = "hard"):
- Write BETWEEN {min_words} AND {max_words} words.
- Do NOT summarize.
- Do NOT stop early.
- Expand every section with depth and factual explanation.

CONTENT STRUCTURE:
- Begin directly with a section header (e.g., "Background").
- Use descriptive section headers.
- Integrate keywords naturally.
- Ensure logical flow.
- End with a brief concluding paragraph that summarizes the significance of the topic.


OUTPUT RULES (CRITICAL):
- Output ONLY the study content.
- Do NOT include a title, topic name, or topic number.
- Do NOT include introductory filler.
- Do NOT include meta commentary.

[/INST]
"""

def clean_ending(text: str) -> str:
    text = text.strip()
    if not text.endswith((".", "!", "?")):
        text = text.rsplit(".", 1)[0] + "."
    return text


def generate_explanation(prompt:str,difficulty:str)->str:
    output=llm_client.generate(
        prompt,
        max_tokens=max_tokens_for_difficulty(difficulty),
    )
    return clean_ending(str(output).strip())

def explain_all_topics(topic_chunks:dict[int,list[str]],topic_keywords:dict[int,list[str]],topic_difficulty:dict[int,dict])->dict[int,dict]:
    explanations={}
    for label,chunks in topic_chunks.items():
        keywords=topic_keywords.get(label,[])
        difficulty=topic_difficulty.get(label,{}).get("difficulty","medium")
        prompt=build_prompt_for_topic(chunks,keywords,difficulty)
        explanation=generate_explanation(prompt,difficulty)
        explanations[label]={
            "difficulty":difficulty,
            "keywords":keywords,
            "explanation":explanation
        }
    return explanations
