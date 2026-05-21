import re

from llm.factory import get_llm_client
from typing import List, Dict

llm_client = get_llm_client()
# =========================
# Utility & Scoring
# =========================

def chunk_kw_score(chunk: str, keywords: list[str]) -> float:
    if not isinstance(chunk, str) or not chunk.strip():
        return 0.0
    words = chunk.lower().split()
    kw_set = set(kw.lower() for kw in keywords)
    return sum(1 for w in words if w in kw_set) / max(len(words), 1)


def chunk_selector(
    chunks: list[str],
    keywords: list[str],
    max_chunk_lim: int,
) -> list[str]:
    chunks = [c for c in chunks if isinstance(c, str) and c.strip()]
    if len(chunks) <= max_chunk_lim:
        return chunks

    scored = [(i, chunk_kw_score(c, keywords)) for i, c in enumerate(chunks)]
    scored.sort(key=lambda x: x[1], reverse=True)

    if max(score for _, score in scored) == 0:
        return chunks[:max_chunk_lim]

    selected_idx = sorted(i for i, _ in scored[:max_chunk_lim])
    return [chunks[i] for i in selected_idx]


def difficulty_chunk_limit(difficulty: str) -> int:
    return {"easy": 3, "medium": 5, "hard": 10}.get(difficulty, 5)


def normalize_text(text: str) -> str:
    return (
        text.replace("..", ".")
        .replace(" .", ".")
        .replace(" ,", ",")
        .strip()
    )


def ends_cleanly(text: str) -> bool:
    return text.rstrip().endswith((".", "!", "?"))


# =========================
# PHASE 1 — STRUCTURE
# =========================


def normalize_header_text(text: str) -> str:
    return re.sub(r"^#+\s*", "", text).strip().lower()


def strip_header_echo(body: str, header: str) -> str:
    """
    Removes cases where the model repeats the section title
    as plain text or a markdown heading at the start of the section.
    """
    lines = body.strip().splitlines()

    if not lines:
        return body

    header_text = normalize_header_text(header)

    # Remove repeated header lines at the start of the body,
    # whether they appear as plain text or with markdown heading syntax.
    while lines and normalize_header_text(lines[0]) == header_text:
        lines = lines[1:]

    return "\n".join(lines).strip()


def generate_section_outline(
    chunks: list[str],
    keywords: list[str],
    difficulty: str,
) -> list[str]:

    context = "\n".join(
        chunk_selector(chunks, keywords, difficulty_chunk_limit(difficulty))
    )
    kw_string = ", ".join(keywords)

    prompt = f"""
<s>[INST]
You are an expert study-content planner.

TASK:
Generate ONLY Markdown section headers for a study guide.

RULES:
- Output ONLY headers.
- Each line MUST start with "## ".
- NO explanations.
- NO blank lines.
- NO title.
- Headers must be logically ordered.
- Include a final header exactly: "## Conclusion".
- NEVER repeat headers.

Topic difficulty: {difficulty}
Relevant keywords: {kw_string}

REFERENCE CONTEXT (source material or user query):
{context}

[/INST]
"""

    raw = str(llm_client.generate(prompt, max_tokens=300)).strip()

    headers = [
        line.strip()
        for line in raw.splitlines()
        if line.strip().startswith("## ")
    ]

    # Hard safety
    if not headers or headers[-1] != "## Conclusion":
        headers.append("## Conclusion")

    # Dedup
    seen = set()
    final_headers = []
    for h in headers:
        if h not in seen:
            final_headers.append(h)
            seen.add(h)

    return final_headers


# =========================
# PHASE 2 — SECTION FILL
# =========================

def min_words_for_difficulty(difficulty: str) -> int:
    return {
        "easy": 80,
        "medium": 115,
        "hard": 200,
    }.get(difficulty, 115)


def max_tokens_for_section(difficulty: str) -> int:
    return {
        "easy": 120,
        "medium": 175,
        "hard": 300,
    }.get(difficulty, 175)


def generate_section_content(
    header: str,
    outline: list[str],
    context: str,
    difficulty: str,
) -> str:

    max_tokens = max_tokens_for_section(difficulty)
    min_words = min_words_for_difficulty(difficulty)

    prompt = f"""
<s>[INST]
You are an expert AI Study Assistant writing ONE section of a study guide.

CURRENT SECTION:
{header}

FULL OUTLINE (LOCKED — DO NOT CHANGE):
{chr(10).join(outline)}

STRICT RULES:
- Write content ONLY for {header}. DO NOT write other headers.
- DO NOT preview next sections.
- DO NOT summarize the entire topic unless it's the Conclusion.
- Maintain difficulty: {difficulty}. Use simple words if the topic is complex.
- **Formatting is required**: heavily use bullet points (`-`), bold text, and markdown tables if they make the material easier for a student to quickly read and understand.
- If REFERENCE CONTEXT is large, summarize the key points clearly.
- If REFERENCE CONTEXT is minimal or short (e.g. a topic name), rely on your general knowledge to provide a comprehensive, point-wise explanation in simple words.
- End cleanly with punctuation.

REFERENCE CONTEXT:
{context}

OUTPUT:
- Start immediately with content.
- No meta commentary.

[/INST]
"""

    text = str(llm_client.generate(prompt, max_tokens=max_tokens)).strip()

    continuations = 0
    while (
        continuations < 3
        and (not ends_cleanly(text) or len(text.split()) < min_words)
    ):
        cont_prompt = f"""
<s>[INST]
Continue the SAME section.

RULES:
- Do NOT add headers.
- Do NOT restart.
- Continue from last sentence.
- End cleanly.

TEXT SO FAR:
{text}

[/INST]
"""
        cont = str(
            llm_client.generate(cont_prompt, max_tokens=int(max_tokens * 0.5))
        ).strip()

        if not cont or cont in text:
            break

        text += " " + cont
        continuations += 1

    text = strip_header_echo(text, header)
    return normalize_text(text)



# =========================
# PHASE 3 — ASSEMBLY
# =========================

def generate_explanation_for_topic(
    chunks: list[str],
    keywords: list[str],
    difficulty: str,
) -> str:

    selected_chunks = chunk_selector(
        chunks, keywords, difficulty_chunk_limit(difficulty)
    )
    context = "\n".join(selected_chunks)
    
    outline = generate_section_outline(chunks, keywords, difficulty)
    outline = cap_outline_by_difficulty(outline, difficulty)


    sections = []
    for header in outline:
        body = generate_section_content(
            header=header,
            outline=outline,
            context=context,
            difficulty=difficulty,
        )
        sections.append(f"{header}\n{body}")

    return "\n\n".join(sections)

def cap_outline_by_difficulty(
    outline: list[str],
    difficulty: str,
) -> list[str]:
    """
    Caps total number of headers INCLUDING Conclusion.
    """
    limits = {
        "easy": 5,
        "medium": 6,
        "hard": 8,
    }

    max_headers = limits.get(difficulty, 6)

    if len(outline) <= max_headers:
        return outline

    # Always preserve Conclusion
    body = [h for h in outline if h != "## Conclusion"]

    # Leave space for Conclusion
    body = body[: max_headers - 1]

    return body + ["## Conclusion"]


# =========================
# MULTI-TOPIC DRIVER
# =========================

def explain_all_topics(
    topic_chunks: Dict[int, list[str]],
    topic_keywords: Dict[int, list[str]],
    topic_difficulty: Dict[int, dict],
) -> Dict[int, dict]:

    explanations = {}

    for label, chunks in topic_chunks.items():
        keywords = topic_keywords.get(label, [])
        difficulty = topic_difficulty.get(label, {}).get("difficulty", "medium")

        explanation = generate_explanation_for_topic(
            chunks=chunks,
            keywords=keywords,
            difficulty=difficulty,
        )

        explanations[label] = {
            "difficulty": difficulty,
            "keywords": keywords,
            "explanation": explanation,
        }

    return explanations 
