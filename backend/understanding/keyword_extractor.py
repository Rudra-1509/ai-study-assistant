from collections import defaultdict,Counter
from nltk.corpus import stopwords
import re
def group_by_labels(labels:list[int],chunks:list[str])->dict[int,list[str]]:
    if len(chunks)!=len(labels):
        raise ValueError("Chunks and labels must be of same length.")
    my_dict=defaultdict(list)
    for label,chunk in zip(labels,chunks):
        my_dict[label].append(chunk)
    return my_dict


def group_items_by_labels(labels: list[int], items: list) -> dict[int, list]:
    """
    [NEW] Generic version of group_by_labels - groups ANY parallel list by
    cluster label, not just chunk strings.

    Why this exists: to score sections with embeddings we need
    `topic_chunk_embeddings: dict[label -> list[embedding]]` that lines up
    1:1 with the existing `topic_chunks: dict[label -> list[chunk]]`
    produced by group_by_labels(). Since `chunk_embeddings` (from
    bert_embedder.embed_text(chunks)) is already index-aligned with
    `chunks`, calling this with the SAME `labels` list guarantees the
    resulting per-topic embedding groups line up with the per-topic chunk
    groups - no separate re-derivation of alignment is needed.

    Usage (in the pipeline driver, alongside the existing call):
        topic_chunks = group_by_labels(labels, chunks)
        topic_chunk_embeddings = group_items_by_labels(labels, chunk_embeddings)
    """
    if len(items) != len(labels):
        raise ValueError("Items and labels must be of same length.")
    my_dict = defaultdict(list)
    for label, item in zip(labels, items):
        my_dict[label].append(item)
    return my_dict


def extract(my_dict:dict[int,list[str]],top_k:int=5)->dict[int,list[str]]:
    if not my_dict:
        raise ValueError("Chunks have not been grouped properly")
    final_dict=defaultdict(list)
    stop_words = set(stopwords.words("english"))
    for label,chunks in my_dict.items():
        text=" ".join(chunks).lower()
        text=re.sub(r"[^a-z\s]",' ',text)
        words=text.split()
        words=[word for word in words if word not in stop_words and len(word)>2]
        word_counts=Counter(words)
        top_words=[word for word,_ in word_counts.most_common(top_k)]
        final_dict[label]=top_words
    return final_dict
def keyword_extractor(labels:list[int],chunks:list[str],top_k:int=5)->dict[int,list[str]]:
    grouped_dict=group_by_labels(labels,chunks)
    final_dict=extract(grouped_dict,top_k)
    return final_dict