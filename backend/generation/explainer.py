import os
import re
import asyncio
from difflib import SequenceMatcher
from typing import Dict

from embeddings.embedding_utils import cosine_similarity, embed_header_safe

# =========================
# GLOBAL CONCURRENCY CONTROL
# =========================

LLM_SEMAPHORE = None
TOKEN_STATS = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
}

def init_semaphore(limit=4):
    global LLM_SEMAPHORE
    LLM_SEMAPHORE = asyncio.Semaphore(limit)


async def safe_llm_generate(llm_client, prompt: str, max_tokens: int):
    if LLM_SEMAPHORE is None:
        raise RuntimeError("Semaphore not initialized")
    async with LLM_SEMAPHORE:
        result= await llm_client.generate(prompt, max_tokens=max_tokens)
        TOKEN_STATS["prompt_tokens"] += result["usage"]["prompt_tokens"]
        TOKEN_STATS["completion_tokens"] += result["usage"]["completion_tokens"]
        TOKEN_STATS["total_tokens"] += result["usage"]["total_tokens"]

        return result["text"]


# =========================
# UTILITIES
# =========================

def reset_token_stats():
    TOKEN_STATS["prompt_tokens"] = 0
    TOKEN_STATS["completion_tokens"] = 0
    TOKEN_STATS["total_tokens"] = 0

def chunk_kw_score(chunk: str, keywords: list[str]) -> float:
    if not chunk.strip():
        return 0.0

    text = chunk.lower()
    words = set(re.findall(r"\w+", text))
    score = 0.0

    for kw in keywords:
        kw = kw.lower().strip()
        if not kw:
            continue

        phrase_count = text.count(kw)
        score += phrase_count * 20

        kw_words = re.findall(r"\w+", kw)
        if kw_words:
            matched = sum(1 for w in kw_words if w in words)
            coverage = matched / len(kw_words)
            score += coverage * 10
            if coverage == 1:
                score += 5

    score += min(len(words) / 100, 3)
    return score


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


def outline_pool_limit(difficulty: str) -> int:
    """Chunks visible to the outline generator. Larger = better-informed headers."""
    return {"easy": 2, "medium": 3, "hard": 8}.get(difficulty, 3)


def max_body_sections_for_difficulty(difficulty: str) -> int:
    """Hard ceiling on body section count. Decoupled from pool size."""
    return {"easy": 2, "medium": 3, "hard": 4}.get(difficulty, 3)


def context_limit_for_difficulty(difficulty: str) -> int:
    """Chunks pulled per section for content generation."""
    return {"easy": 1, "medium": 2, "hard": 4}.get(difficulty, 2)


def reuse_penalty_for_difficulty(difficulty: str) -> int:
    """
    [CHANGE 3] Score penalty applied to a chunk already claimed by an earlier header.
    Harder topics have a stronger penalty to force section diversity across a
    larger pool. Previous fixed value was -10, which was too weak.
    """
    return {"easy": 10, "medium": 30, "hard": 50}.get(difficulty, 30)


def normalize_text(text: str) -> str:
    text = re.sub(r"\[\d+\]", "", text)
    return (
        text.replace("..", ".")
        .replace(" .", ".")
        .replace(" ,", ",")
        .replace("\r", "")
        .strip()
    )


def remove_header_echo(header: str, content: str) -> str:
    header_text = re.sub(r"^#+\s*", "", header).strip()
    content = content.strip()

    if content.lower().startswith(header_text.lower()):
        content = content[len(header_text):].strip()
        if content.startswith(":"):
            content = content[1:].strip()

    return content


def clean_conclusion(text: str) -> str:
    outer_patterns = [
        r"^in conclusion[,:\s]*",
        r"^to conclude[,:\s]*",
        r"^overall[,:\s]*",
        r"^in summary[,:\s]*",
        r"^to summarize[,:\s]*",
        r"^this topic highlights[,:\s]*",
        r"^this topic focuses on[,:\s]*",
        r"^as we conclude\b[^,]*,\s*",
        r"^as we reflect\b[^,]*,\s*",
        r"^as we look\b[^,]*,\s*",
        r"^as we can see[,:\s]*",
    ]
    secondary_patterns = [
        r"^it is (clear|evident|apparent|important)\b[^,]*,?\s*(that\s+)?",
        r"^it is essential to (recall|note|remember|highlight)\b[^,]*,?\s*(that\s+)?",
        r"^it('s| is) (worth noting|important to note)\b[^,]*,?\s*(that\s+)?",
    ]

    for _ in range(2):
        for pattern in outer_patterns + secondary_patterns:
            text = re.sub(pattern, "", text, flags=re.I)
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]

    return text.strip()


def strip_header_prefix(header: str) -> str:
    return re.sub(r"^#+\s*", "", header).strip()


# =========================
# PAIR-SAFE POST-PROCESSING  [CHANGE 5]
# =========================
# All three functions now accept and return list[tuple[str, str]] so that
# headers and contents are always moved together. The previous versions
# operated on a bare list[str] for contents, which caused misalignment
# whenever an entry was removed (dedupe/filter) because the caller used
# body_headers[:len(section_contents)] to re-align — a fragile assumption.

def dedup_facts_across_sections(
    pairs: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """
    Sentence-level deduplication across sections.
    First section to mention a fact keeps it; later sections lose it.
    Operates on pairs so the header travels with its content.
    """
    seen_keys: set[str] = set()
    result: list[tuple[str, str]] = []

    for header, content in pairs:
        sentences = re.split(r"(?<=[.!?]) +", content.strip())
        kept: list[str] = []

        for sentence in sentences:
            key = " ".join(sentence.lower().split())[:80]
            if key and key not in seen_keys:
                seen_keys.add(key)
                kept.append(sentence)

        result.append((header, " ".join(kept).strip()))

    return result


def dedupe_similar_sections(
    pairs: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """
    Removes sections whose first 40 content words match an earlier section.
    Operates on pairs.
    """
    seen: set[str] = set()
    result: list[tuple[str, str]] = []

    for header, content in pairs:
        key = " ".join(content.lower().split()[:40])
        if key not in seen:
            seen.add(key)
            result.append((header, content))

    return result


def filter_sparse_sections(
    pairs: list[tuple[str, str]],
    min_words: int = 20,
) -> list[tuple[str, str]]:
    """
    Drops sections whose content falls below min_words after deduplication.
    Operates on pairs.
    """
    return [
        (header, content)
        for header, content in pairs
        if len(content.split()) >= min_words
    ]


def dedupe_chunks(
    chunks: list[str],
    embeddings: list[list[float]] | None = None,
) -> tuple[list[str], list[list[float]] | None]:
    """
    Removes duplicate chunks (by first-300-char key) - same rule as before.

    [CHANGE] Now optionally accepts the parallel `embeddings` list (one
    embedding per chunk, same order as `chunks`) and keeps it aligned with
    the deduped chunks. This matters because generate_explanation_for_topic
    dedupes chunks BEFORE scoring sections, and we must never let the
    embeddings list drift out of sync with the chunks list it describes.

    Pass embeddings=None (default) to use exactly as before, when no
    embeddings are available for this call.
    """
    if embeddings is not None and len(embeddings) != len(chunks):
        raise ValueError(
            "chunks and embeddings must be the same length and in the same order."
        )

    seen = set()
    out_chunks: list[str] = []
    out_embeddings: list[list[float]] | None = [] if embeddings is not None else None

    for i, chunk in enumerate(chunks):
        key = chunk[:300].lower().strip()
        if key not in seen:
            seen.add(key)
            out_chunks.append(chunk)
            if out_embeddings is not None:
                out_embeddings.append(embeddings[i])

    return out_chunks, out_embeddings


# =========================
# HEADER DEDUPLICATION
# =========================

def header_similarity(h1: str, h2: str) -> float:
    return SequenceMatcher(
        None,
        strip_header_prefix(h1).lower(),
        strip_header_prefix(h2).lower(),
    ).ratio()


def remove_overlapping_headers(
    headers: list[str],
    threshold: float = 0.75,
) -> list[str]:
    conclusion = [h for h in headers if "conclusion" in h.lower()]
    body = [h for h in headers if "conclusion" not in h.lower()]

    kept: list[str] = []
    for candidate in body:
        already_covered = any(
            header_similarity(candidate, kept_h) > threshold
            for kept_h in kept
        )
        if not already_covered:
            kept.append(candidate)

    return kept + (conclusion[:1] if conclusion else ["## Conclusion"])


# =========================
# OUTLINE
# =========================

def normalize_header_text(text: str) -> str:
    return strip_header_prefix(text).lower()


async def generate_section_outline(
    chunks: list[str],
    keywords: list[str],
    difficulty: str,
    llm_client,
) -> list[str]:
    context = "\n".join(
        chunk_selector(chunks, keywords, outline_pool_limit(difficulty))
    )

    prompt = f"""
<s>[INST]

Create a study guide outline.

Rules:
- Use ONLY information present in the context.
- Generate 2-4 section headers.
- Each header must be MUTUALLY EXCLUSIVE from all others.
- Before writing each header, verify it does not overlap any header already written.
- If two headers could contain the same fact, merge them into one header instead.
- No two headers may share a primary subject, entity, or time period.
- Do not create two headers that discuss the same information.
- Prefer concrete and specific headers over broad categories.
- If the topic contains chronology, use chronological stages.
- If the topic contains categories, use category-based sections.
- If the topic contains processes, use process stages.
- Do not invent information not found in the context.

Examples of overlapping pairs that must be MERGED (do not generate both):
- Career Path + Transfer History           → merge into: Career and Transfers
- Records + Statistics                     → merge into: Career Statistics and Records
- Achievements + Accolades                 → merge into: Achievements and Honours
- Early Life + Childhood                   → merge into: Early Life and Background
- Tactics + Playing Style                  → merge into: Playing Style and Tactics
- Research + Studies                       → merge into: Research and Key Studies
- Features + Capabilities                  → merge into: Features and Capabilities

Avoid generic headers such as:
## Overview
## Background
## General Information
## Summary
## Introduction

Prefer headers that directly reflect the content, such as:
## Causes and Contributing Factors
## Key Components and Architecture
## Development Process
## Applications and Use Cases
## Challenges and Limitations
## Historical Evolution
## Experimental Results
## Early Life and Family
## Professional Career
## International Achievements

Requirements:
- Every header must represent a distinct subtopic with zero overlap.
- Headers should maximize coverage of the context.
- Headers should be useful for revision and study.
- Return ONLY markdown headers.

Output format:

## Header
## Header
## Header
## Conclusion

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

    if not any("conclusion" in h.lower() for h in headers):
        headers.append("## Conclusion")

    seen: set[str] = set()
    deduped: list[str] = []
    for h in headers:
        normalized = normalize_header_text(h)
        if normalized not in seen:
            deduped.append(h)
            seen.add(normalized)

    return deduped


# =========================
# CONTEXT SELECTION
# =========================

# [CHANGE] SEMANTIC_HINTS (the hardcoded header-keyword -> bonus-word
# dictionary) has been REMOVED. It only ever generalized to concepts a
# developer had manually anticipated (e.g. it knew "achievements" implied
# "ballon"/"trophy" for football biographies, but had nothing for a physics
# or biology topic). It's replaced below by embedding-based semantic
# similarity in get_section_context(), which works for any topic because it
# doesn't rely on anyone enumerating synonyms in advance.

# Hybrid scoring weights - configurable constants rather than magic numbers
# scattered through get_section_context(). Override via env vars if a
# deployment wants to lean more/less on semantic vs. exact-word matching.
SEMANTIC_WEIGHT = float(os.getenv("SECTION_SEMANTIC_WEIGHT", "25"))
LEXICAL_WEIGHT = float(os.getenv("SECTION_LEXICAL_WEIGHT", "1.0"))
KEYWORD_WEIGHT = float(os.getenv("SECTION_KEYWORD_WEIGHT", "1.0"))


async def get_header_embedding_for_scoring(header: str) -> list[float] | None:
    """
    Requirement: embed each section header exactly ONCE (not once per
    chunk). Called a single time per header in generate_explanation_for_topic,
    before the per-chunk scoring loop in get_section_context runs.

    Strips the markdown '## ' prefix first so we embed natural-language
    text ("Career and Transfers"), not markdown syntax.
    """
    return await embed_header_safe(strip_header_prefix(header))


def get_section_context(
    header: str,
    chunks: list[str],
    chunk_embeddings: list[list[float]] | None = None,
    header_embedding: list[float] | None = None,
    keywords: list[str] | None = None,
    limit: int = 1,
    used_chunk_ids: set[int] | None = None,
    reuse_penalty: int = 30,              # [CHANGE 3] parameterised, scaled by difficulty
) -> tuple[str, list[int]]:
    """
    Scores every chunk against this header using a hybrid of:

      1. Lexical score: unique word overlap + exact-phrase bonus (+20) +
         per-word frequency across the chunk. Weighted by LEXICAL_WEIGHT.
      2. Keyword score: keyword frequency bonus (+5 per occurrence).
         Weighted by KEYWORD_WEIGHT.
      3. Semantic score [REPLACES SEMANTIC_HINTS]: cosine similarity
         between the header's embedding and this chunk's embedding.
         Weighted by SEMANTIC_WEIGHT. This is what lets a chunk like
         "He signed a four-year contract and made his debut" rank highly
         for a header like "Career and Transfers" even though it shares
         no literal words with the header - the old hardcoded dictionary
         could only do this for topics someone had anticipated in advance;
         embeddings generalize to any topic.
      4. Reuse penalty for chunks already assigned to an earlier header
         (unchanged, still subtracted after weighting).

    Graceful degradation: if header_embedding is None (the header failed
    to embed upstream) or chunk_embeddings wasn't provided/doesn't line up
    with chunks, the semantic term is simply skipped (contributes 0) and
    scoring falls back to lexical + keyword only. This function never
    raises because of a missing/failed embedding.

    Returns (context_string, list_of_selected_chunk_indices).
    """
    if used_chunk_ids is None:
        used_chunk_ids = set()

    header_lower = header.lower()
    header_words = set(re.findall(r"\w+", header_lower))

    have_embeddings = (
        header_embedding is not None
        and chunk_embeddings is not None
        and len(chunk_embeddings) == len(chunks)
    )

    scored: list[tuple[float, int, str]] = []

    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        chunk_words = set(re.findall(r"\w+", chunk_lower))

        # 1. Lexical score: unique word overlap + exact phrase + frequency
        lexical_score: float = len(header_words & chunk_words)
        if header_lower in chunk_lower:
            lexical_score += 20
        for word in header_words:
            lexical_score += chunk_lower.count(word)

        # 2. Keyword score
        keyword_score: float = 0.0
        if keywords:
            for kw in keywords:
                kw_lower = kw.lower().strip()
                if kw_lower:
                    keyword_score += chunk_lower.count(kw_lower) * 5

        # 3. Semantic score (embedding-based, replaces SEMANTIC_HINTS)
        semantic_score = 0.0
        if have_embeddings:
            semantic_score = cosine_similarity(header_embedding, chunk_embeddings[i])

        score = (
            LEXICAL_WEIGHT * lexical_score
            + KEYWORD_WEIGHT * keyword_score
            + SEMANTIC_WEIGHT * semantic_score
        )

        # 4. Reuse penalty
        if i in used_chunk_ids:
            score -= reuse_penalty

        scored.append((score, i, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]
    selected_ids = [i for _, i, _ in top]
    context = "\n".join(chunk for _, _, chunk in top)

    return context, selected_ids


# =========================
# SECTION GENERATION
# =========================

def max_tokens_for_section(difficulty: str) -> int:
    return {"easy": 120, "medium": 160, "hard": 220}.get(difficulty, 160)


def safe_trim_to_sentences(text: str, max_words: int = 160) -> str:
    sentences = re.split(r"(?<=[.!?]) +", text.strip())
    out: list[str] = []
    count = 0

    for s in sentences:
        w = len(s.split())
        if count + w > max_words:
            break
        out.append(s)
        count += w

    return " ".join(out)


def _build_exclusion_block(other_headers: list[str] | None) -> str:
    if not other_headers:
        return ""
    items = "\n".join(f"- {strip_header_prefix(h)}" for h in other_headers)
    return (
        f"\nThis section does NOT cover:\n{items}\n"
        f"If a fact fits better under those sections, omit it here.\n"
    )


def _build_previous_block(previous_sections: list[str] | None) -> str:
    if not previous_sections:
        return ""
    recent = "\n---\n".join(previous_sections[-2:])
    return (
        f"\nAlready covered in previous sections:\n{recent}\n"
        f"Do not repeat any facts already stated above.\n"
    )


async def generate_section_content(
    header: str,
    context: str,
    difficulty: str,
    llm_client,
    other_headers: list[str] | None = None,
    previous_sections: list[str] | None = None,
) -> str:
    max_tokens = max_tokens_for_section(difficulty)
    exclusion_block = _build_exclusion_block(other_headers)
    previous_block = _build_previous_block(previous_sections)

    prompt = f"""
<s>[INST]

Write ONE study-guide section.

This section covers:
{header}
{exclusion_block}{previous_block}
Rules:
- Only write facts that are EXPLICITLY STATED in the context below.
- Do NOT infer, extrapolate, assume, or add background knowledge.
- Do NOT generalise beyond what the context directly states.
- If the context does not contain enough information for this section, write only what is available. Do not pad with assumptions.
- Use only facts directly relevant to this section.
- Do not repeat facts from other sections.
- Do not mention future sections.
- Do not summarize the whole topic.
- Do not write a conclusion.
- 2-3 concise paragraphs.
- No markdown headers.
- No introductory phrases.
- If a fact appears more suitable for another section, do not include it here.

Context:
{context}

[/INST]
"""

    text = await safe_llm_generate(llm_client, prompt, max_tokens)
    text = safe_trim_to_sentences(text, 160)
    text = normalize_text(text)
    text = remove_header_echo(header, text)
    return text


async def generate_conclusion(
    section_contents: list[str],
    section_headers: list[str],
    keywords: list[str],
    llm_client,
) -> str:
    section_labels = "\n".join(
        f"- {strip_header_prefix(h)}" for h in section_headers
    )
    section_summaries = "\n\n".join(
        f"{strip_header_prefix(h)}:\n{c}"
        for h, c in zip(section_headers, section_contents)
    )

    prompt = f"""
<s>[INST]

Write a study-guide conclusion.

RULES:
- Exactly 2 sentences.
- You MUST reference the theme of each section listed below by name:
{section_labels}
- Summarize the most important idea from each section.
- Mention at least 2 keywords naturally.
- Focus on revision value.
- No markdown.
- No bullet points.
- Do NOT open with any of these phrases:
  "In conclusion", "In summary", "Overall", "To conclude", "To summarize",
  "As we conclude", "As we reflect", "It is evident that", "It is clear that",
  "It is important to note", "It is essential to recall".

Keywords:
{", ".join(keywords)}

Sections:
{section_summaries}

[/INST]
"""

    text = await safe_llm_generate(llm_client, prompt, 120)
    return normalize_text(safe_trim_to_sentences(text, 60))


# =========================
# ASSEMBLY
# =========================

def cap_outline_by_difficulty(
    outline: list[str],
    difficulty: str,
    chunk_count: int,
) -> list[str]:
    section_limit = max_body_sections_for_difficulty(difficulty)
    max_body = min(chunk_count, section_limit)

    body = [h for h in outline if "conclusion" not in h.lower()]
    body = body[:max_body]

    return body + ["## Conclusion"]


# Fallback used in two places — defined once to guarantee consistency.
_CONCLUSION_FALLBACK = (
    "Reviewing the key ideas presented above "
    "helps build a clear understanding of the topic "
    "and its most important concepts."
)


async def generate_explanation_for_topic(
    chunks: list[str],
    keywords: list[str],
    difficulty: str,
    llm_client,
    chunk_embeddings: list[list[float]] | None = None,
    sequential: bool = True,   # [CHANGE 4] default flipped to True
) -> str:

    # ── Step 1: dedupe full pool (embeddings kept aligned if provided) ──────
    all_chunks, all_chunk_embeddings = dedupe_chunks(chunks, chunk_embeddings)

    # ── Step 2: outline → similarity-dedupe → chunk-cap ──────────────────────
    # Outline generation stays purely lexical (chunk_selector) - it doesn't
    # need embeddings, only the per-section chunk selection below does.
    outline = await generate_section_outline(all_chunks, keywords, difficulty, llm_client)
    outline = remove_overlapping_headers(outline)
    outline = cap_outline_by_difficulty(outline, difficulty, len(all_chunks))

    body_headers = [h for h in outline if "conclusion" not in h.lower()]

    # ── Step 3: per-header chunk selection (hybrid: lexical+keyword+semantic) ─
    context_limit = context_limit_for_difficulty(difficulty)
    reuse_penalty = reuse_penalty_for_difficulty(difficulty)   # [CHANGE 3]
    used_chunk_ids: set[int] = set()
    header_contexts: dict[str, str] = {}

    for header in body_headers:
        # One embedding per header (never per chunk) - falls back to None
        # (and therefore lexical/keyword-only scoring) on any failure.
        header_embedding = await get_header_embedding_for_scoring(header)

        context, selected_ids = get_section_context(
            header,
            all_chunks,
            chunk_embeddings=all_chunk_embeddings,
            header_embedding=header_embedding,
            keywords=keywords,
            limit=context_limit,
            used_chunk_ids=used_chunk_ids,
            reuse_penalty=reuse_penalty,               # [CHANGE 3]
        )
        header_contexts[header] = context
        used_chunk_ids.update(selected_ids)

    # ── Step 4: section generation ────────────────────────────────────────────
    section_contents: list[str] = []

    if sequential:
        for header in body_headers:
            other_headers = [h for h in body_headers if h != header]
            content = await generate_section_content(
                header,
                header_contexts[header],
                difficulty,
                llm_client,
                other_headers=other_headers,
                previous_sections=section_contents.copy(),
            )
            section_contents.append(content)
    else:
        tasks = [
            generate_section_content(
                header,
                header_contexts[header],
                difficulty,
                llm_client,
                other_headers=[h for h in body_headers if h != header],
                previous_sections=None,
            )
            for header in body_headers
        ]
        section_contents = list(await asyncio.gather(*tasks))

    # ── Step 5: pair-safe post-processing ─────────────────────────────────────
    # [CHANGE 5] Zip immediately; every subsequent operation works on pairs
    # so removals never create a header/content offset.
    pairs: list[tuple[str, str]] = list(zip(body_headers, section_contents))
    pairs = dedup_facts_across_sections(pairs)
    pairs = dedupe_similar_sections(pairs)
    pairs = filter_sparse_sections(pairs, min_words=20)

    if pairs:
        aligned_headers, aligned_contents = zip(*pairs)
        aligned_headers = list(aligned_headers)
        aligned_contents = list(aligned_contents)
    else:
        aligned_headers, aligned_contents = [], []

    formatted_sections = [
        f"{header}\n{content}"
        for header, content in zip(aligned_headers, aligned_contents)
    ]

    # ── Step 6: conclusion from actual written sections ───────────────────────
    if aligned_headers and aligned_contents:
        conclusion = await generate_conclusion(
            aligned_contents,
            aligned_headers,
            keywords,
            llm_client,
        )
        conclusion = clean_conclusion(conclusion)
    else:
        conclusion = _CONCLUSION_FALLBACK

    # [CHANGE 1] Keyword-free fallback — no more "early, life form the core..."
    if len(conclusion.split()) < 10:
        conclusion = _CONCLUSION_FALLBACK

    if not formatted_sections:
        return f"## Conclusion\n{conclusion}"

    return "\n\n".join(formatted_sections) + f"\n\n## Conclusion\n{conclusion}"


# =========================
# MULTI-TOPIC DRIVER
# =========================

async def run_single_topic(
    label: int,
    chunks: list[str],
    keywords: list[str],
    difficulty: str,
    llm_client,
    chunk_embeddings: list[list[float]] | None = None,
    sequential: bool = True,   # [CHANGE 4]
):
    explanation = await generate_explanation_for_topic(
        chunks,
        keywords,
        difficulty,
        llm_client,
        chunk_embeddings=chunk_embeddings,
        sequential=sequential,
    )

    return label, {
        "difficulty": difficulty,
        "keywords": keywords,
        "explanation": explanation,
    }


async def explain_all_topics(
    topic_chunks: Dict[int, list[str]],
    topic_keywords: Dict[int, list[str]],
    topic_difficulty: Dict[int, dict],
    llm_client,
    topic_chunk_embeddings: Dict[int, list[list[float]]] | None = None,
    sequential: bool = True,   # [CHANGE 4]
) -> dict:
    tasks = [
        run_single_topic(
            label,
            chunks,
            topic_keywords.get(label, []),
            topic_difficulty.get(label, {}).get("difficulty", "medium"),
            llm_client,
            chunk_embeddings=(topic_chunk_embeddings or {}).get(label),
            sequential=sequential,
        )
        for label, chunks in topic_chunks.items()
    ]

    return dict(await asyncio.gather(*tasks))