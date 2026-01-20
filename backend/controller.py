from backend.preprocessing import cleaner,chunker
from backend.embeddings import bert_embedder
from backend.understanding import topic_classifier,keyword_extractor,difficulty_estimator
from backend.generation import explainer
from backend.evaluation import metrics,logger


def run(input_text:str)->dict:
    #1: preprocessing: clean and chunk
    prepro_text=cleaner.clean_text(input_text)
    chunks=chunker.chunk_text(prepro_text)
    #2. embed the chunks
    chunks_embeddings=bert_embedder.embed_text(chunks)
    #3. label and grouping
    emb_labels=topic_classifier.topic_classifer(chunks_embeddings)
    topic_chunks=keyword_extractor.group_by_labels(emb_labels,chunks)
    #4. keywords extraction and difficulty estimate
    topic_keywords=keyword_extractor.keyword_extractor(emb_labels,chunks,top_k=5)
    difficulty=difficulty_estimator.difficulty_estimator(topic_chunks,topic_keywords)
    #5. generate output
    op=explainer.explain_all_topics(topic_chunks,topic_keywords,difficulty)
    #6. evaluation metrics
    evaluation=metrics.compute_metrics(op)
    logger.log_run(input_text,op,evaluation)
    return op



