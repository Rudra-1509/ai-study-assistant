import re
import asyncio
from typing import List, Dict

# =========================
# GLOBAL CONCURRENCY CONTROL
# =========================

LLM_SEMAPHORE = None


def init_semaphore(limit=4):
    global LLM_SEMAPHORE
    LLM_SEMAPHORE = asyncio.Semaphore(limit)


async def safe_llm_generate(llm_client, prompt: str, max_tokens: int):
    if LLM_SEMAPHORE is None:
        raise RuntimeError("Semaphore not initialized")

    async with LLM_SEMAPHORE:
        return await llm_client.generate(prompt, max_tokens=max_tokens)


# =========================
# UTILITIES
# =========================

def chunk_kw_score(chunk: str, keywords: list[str]) -> float:
    if not isinstance(chunk, str) or not chunk.strip():
        return 0.0

    words = chunk.lower().split()
    kw_set = set(k.lower() for k in keywords)

    return sum(1 for w in words if w in kw_set) / max(len(words), 1)


def chunk_selector(chunks, keywords, limit):
    chunks = [c for c in chunks if isinstance(c, str) and c.strip()]

    if len(chunks) <= limit:
        return chunks

    scored = [(i, chunk_kw_score(c, keywords)) for i, c in enumerate(chunks)]
    scored.sort(key=lambda x: x[1], reverse=True)

    if scored and scored[0][1] == 0:
        return chunks[:limit]

    selected = sorted(i for i, _ in scored[:limit])
    return [chunks[i] for i in selected]


def difficulty_chunk_limit(difficulty: str) -> int:
    return {"easy": 2, "medium": 3, "hard": 4}.get(difficulty, 3)


def normalize_text(text: str) -> str:
    return (
        text.replace("..", ".")
        .replace(" .", ".")
        .replace(" ,", ",")
        .replace("\r", "")
        .strip()
    )


def ends_cleanly(text: str) -> bool:
    return text.rstrip().endswith((".", "!", "?"))

def remove_duplicate_conclusions(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    seen_conclusion = False

    for line in lines:
        if line.strip().lower().startswith("conclusion"):
            if seen_conclusion:
                continue
            seen_conclusion = True

        cleaned.append(line)

    return "\n".join(cleaned)


# =========================
# OUTLINE
# =========================

def normalize_header_text(text: str) -> str:
    return re.sub(r"^#+\s*", "", text).strip().lower()


async def generate_section_outline(chunks, keywords, difficulty, llm_client):

    context = "\n".join(
        chunk_selector(chunks, keywords, difficulty_chunk_limit(difficulty))[:2]
    )

    prompt = f"""
<s>[INST]
Generate a clean study guide outline.

RULES:
- 2 to 4 headers ONLY
- MUST include "## Conclusion"
- NO explanations, NO paragraphs

Output format:
## Header
## Header
## Conclusion

Difficulty: {difficulty}
Keywords: {", ".join(keywords)}

Context:
{context}

[/INST]
"""

    raw = await safe_llm_generate(llm_client, prompt, 250)

    headers = [
        line.strip()
        for line in raw.splitlines()
        if line.strip().startswith("## ")
    ]

    # ensure conclusion
    if not any("conclusion" in h.lower() for h in headers):
        headers.append("## Conclusion")

    # dedupe
    seen = set()
    cleaned = []
    for h in headers:
        if h not in seen:
            cleaned.append(h)
            seen.add(h)

    return cleaned[:4]


# =========================
# SECTION GENERATION
# =========================

def min_words_for_difficulty(difficulty: str) -> int:
    return {"easy": 60, "medium": 90, "hard": 120}.get(difficulty, 90)


def max_tokens_for_section(difficulty: str) -> int:
    return {"easy": 120, "medium": 160, "hard": 220}.get(difficulty, 160)


def safe_trim_to_sentences(text: str, max_words: int = 160):
    """
    prevents mid-sentence cuts
    """
    sentences = re.split(r"(?<=[.!?]) +", text.strip())

    out = []
    count = 0

    for s in sentences:
        w = len(s.split())
        if count + w > max_words:
            break
        out.append(s)
        count += w

    return " ".join(out)


async def generate_section_content(
    header,
    outline,
    context,
    difficulty,
    llm_client
):

    max_tokens = max_tokens_for_section(difficulty)

    prompt = f"""
<s>[INST]
You are a strict markdown generator.

RULES:
- Output ONLY content for the section
- NO meta text ("Here is", "This section...")
- NO repeating header
- Start directly with paragraph or bullets
- Use clean markdown only
- ONLY ONE section may contain "Conclusion"
- If header is not "Conclusion", DO NOT mention it anywhere

SECTION:
{header}
RULES:
- ONLY ONE section may contain "Conclusion"
- If this is NOT "Conclusion", DO NOT mention conclusion anywhere

OUTLINE:
{chr(10).join(outline)}

CONTEXT:
{context}

[/INST]
"""

    text = await safe_llm_generate(llm_client, prompt, max_tokens)

    text = safe_trim_to_sentences(text, 160)
    text = normalize_text(text)

    return text


# =========================
# ASSEMBLY
# =========================

def cap_outline_by_difficulty(outline, difficulty):
    limits = {"easy": 2, "medium": 3, "hard": 4}
    max_headers = limits.get(difficulty, 3)

    if len(outline) <= max_headers:
        return outline

    body = [h for h in outline if "conclusion" not in h.lower()]
    body = body[: max_headers - 1]

    return body + ["## Conclusion"]


async def generate_explanation_for_topic(
    chunks,
    keywords,
    difficulty,
    llm_client
):

    selected = chunk_selector(
        chunks,
        keywords,
        difficulty_chunk_limit(difficulty)
    )

    context = "\n".join(selected[:3])

    outline = await generate_section_outline(
        chunks, keywords, difficulty, llm_client
    )

    outline = cap_outline_by_difficulty(outline, difficulty)

    sections = await asyncio.gather(*[
        generate_section_content(
            h, outline, context, difficulty, llm_client
        )
        for h in outline
    ])

    result = "\n\n".join(sections)

    result = "\n\n".join(sections)

    result = remove_duplicate_conclusions(result)

    # always ensure exactly one conclusion
    if "Conclusion" not in result:
        result += "\n\n## Conclusion\nKey takeaway: This topic connects all core ideas discussed above."
    return result

# =========================
# MULTI TOPIC DRIVER
# =========================

async def run_single_topic(label, chunks, keywords, difficulty, llm_client):
    explanation = await generate_explanation_for_topic(
        chunks, keywords, difficulty, llm_client
    )

    return label, {
        "difficulty": difficulty,
        "keywords": keywords,
        "explanation": explanation
    }


async def explain_all_topics(
    topic_chunks: Dict[int, list[str]],
    topic_keywords: Dict[int, list[str]],
    topic_difficulty: Dict[int, dict],
    llm_client
):

    tasks = []

    for label, chunks in topic_chunks.items():
        tasks.append(
            run_single_topic(
                label,
                chunks,
                topic_keywords.get(label, []),
                topic_difficulty.get(label, {}).get("difficulty", "medium"),
                llm_client
            )
        )

    results = await asyncio.gather(*tasks)

    return dict(results)