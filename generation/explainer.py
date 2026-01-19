from ctransformers import AutoModelForCausalLM

MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"
MODEL_DIR="models/mistral"
MODEL_FILE="Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"

llm = AutoModelForCausalLM.from_pretrained(MODEL_DIR,model_file=MODEL_FILE,model_type="mistral",context_length=2048,threads=8)

def chunk_selector(chunks:list[str],keywords:list[str],max_chunk_lim:int=3)->list[str]:
    #check each chunk's contribution(density->contri/chunk len) for the keywords and take the top scores
    if len(chunks)<=max_chunk_lim:
        return chunks
    scored_chunks=[(i,chunk_kw_score(chunk,keywords)) for i,chunk in enumerate(chunks)]
    #sorting based on scores
    scored_chunks.sort(key=lambda x:x[1],reverse=True)
    #if no chunk contributes at all pick the first chunks
    if max(score for _, score in scored_chunks) == 0:
        return chunks[:max_chunk_lim]
    #then sort based on the index orders
    selected_chunks_ind=sorted(i for i,_ in scored_chunks[:max_chunk_lim])
    return [chunks[i] for i in selected_chunks_ind]


def chunk_kw_score(chunk:str,keywords:list[str])->float:
    words=chunk.lower().split()
    kw_set=set(kw.lower() for kw in keywords)
    return sum(1 for word in words if word in kw_set)/max(len(words), 1)

def difficulty_chunk_limit(difficulty: str)->int:
    return {
        "easy":2,
        "medium":4,
        "hard":6
    }.get(difficulty,4)

def build_prompt_for_topic(chunks:list[str],keywords:list[str],difficulty:str)->str:
    #Context Budgeting
    max_context_chunks=difficulty_chunk_limit(difficulty)
    selected_chunks=chunk_selector(chunks,keywords,max_context_chunks)
    context="\n".join(selected_chunks)
    kw_string=", ".join(keywords)
    prompt = f"""<s>[INST]
You are a study assistant. The user may have an exam or an assignment.
Explain concepts clearly and concisely. Use structure when helpful.

Difficulty level: {difficulty}

Key concepts:
{kw_string}

Context:
{context}

Task:
Explain the topic clearly.
Adjust depth, tone, and assumptions based on the difficulty level.
[/INST]
"""

    return prompt

def generate_explanation(prompt:str,difficulty:str,max_new_tokens:int=256)->str:
    if difficulty == "easy":
        temperature = 0.8
    elif difficulty == "hard":
        temperature = 0.3
    else:
        temperature=0.6
    output=llm(prompt,max_new_tokens=max_new_tokens,temperature=temperature,top_p=0.9,stop=["### END"])

    text= str(output)
    return text.strip()


def explain_all_topics(topic_chunks: dict[int, list[str]],topic_keywords: dict[int, list[str]],topic_difficulty: dict[int, dict])->dict[int,dict]:
    explanations={}
    for label,chunks in topic_chunks.items():
        keywords=topic_keywords.get(label,[])
        difficulty=topic_difficulty.get(label,{}).get("difficulty", "medium")

        prompt=build_prompt_for_topic(chunks,keywords,difficulty)
        explanation=generate_explanation(prompt,difficulty)
        explanations[label]={
            "difficulty":difficulty,
            "keywords":keywords,
            "explanation":explanation
        }
    return explanations