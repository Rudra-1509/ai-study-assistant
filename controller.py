from ingestion import text_loader,pdf_loader,img_loader
from preprocessing import cleaner,chunker
from embeddings import bert_embedder
from understanding import topic_classifier,keyword_extractor,difficulty_estimator
from generation import explainer
from evaluation import metrics,logger
from llm.local import DEFAULT_MODEL_FILE

def run(ip:str,option:int=1)->dict:
    #1: take input text
    if option==1:
        input_text=text_loader.load_text(ip)
    elif option==2:
        input_text=pdf_loader.load_pdf(ip)
    elif option==3:
        input_text=img_loader.load_img(ip)
    else:
        raise ValueError("Invalid Option")
    #2: preprocessing: clean and chunk
    prepro_text=cleaner.clean_text(input_text)
    chunks=chunker.chunk_text(prepro_text)
    #3. embed the chunks
    chunks_embeddings=bert_embedder.embed_text(chunks)
    #4. label and grouping
    emb_labels=topic_classifier.topic_classifer(chunks_embeddings)
    topic_chunks=keyword_extractor.group_by_labels(emb_labels,chunks)
    #5. keywords extraction and difficulty estimate
    topic_keywords=keyword_extractor.keyword_extractor(emb_labels,chunks,top_k=5)
    difficulty=difficulty_estimator.difficulty_estimator(topic_chunks,topic_keywords)
    #6. generate output
    op=explainer.explain_all_topics(topic_chunks,topic_keywords,difficulty)
    #evaluation metrics
    evaluation=metrics.compute_metrics(op)
    logger.log_run(input_text,op,evaluation,DEFAULT_MODEL_FILE)
    return op



