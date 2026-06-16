from embeddings import bert_embedder
from preprocessing import cleaner,chunker
from understanding import topic_classifier,keyword_extractor,difficulty_estimator
from generation import explainer
from evaluation import metrics,logger
from evaluation.benchmark import PipelineTimer
import textstat
import time

async def run(input_text:str,llm_client,timer:PipelineTimer,start_time:float)->dict:
    #1: preprocessing: clean and chunk
    with timer.measure("preprocessing"):
        prepro_text=cleaner.clean_text(input_text)
        chunks=chunker.chunk_text(prepro_text)
    #2. embed the chunks
    with timer.measure("embedding"):
        chunks_embeddings=bert_embedder.embed_text(chunks)
    #3. label and grouping
    with timer.measure("clustering"):
        emb_labels, silhouette = (topic_classifier.topic_classifer(chunks_embeddings))
    with timer.measure("grouping"):
        topic_chunks=keyword_extractor.group_by_labels(emb_labels,chunks)

    #4. keywords extraction and difficulty estimate
    with timer.measure("keyword extraction"):
        topic_keywords=keyword_extractor.keyword_extractor(emb_labels,chunks,top_k=5)
    with timer.measure("difficulty estimation"):
        difficulty=difficulty_estimator.difficulty_estimator(topic_chunks,topic_keywords)
    #5. generate output
    with timer.measure("output genration"):
        explainer.reset_token_stats()
        op=await explainer.explain_all_topics(topic_chunks,topic_keywords,difficulty,llm_client)
        
    #6. evaluation metrics
    end_time=time.perf_counter()
    total_pipeline=end_time-start_time
    evaluation=metrics.compute_metrics(op)
    input_flesch = textstat.flesch_reading_ease(input_text)
    combined_op_text = "\n\n".join(topic["explanation"] for topic in op.values())
    output_flesch = textstat.flesch_reading_ease(combined_op_text)
    logger.log_run(input_text,op,evaluation,silhouette,input_flesch,output_flesch,timer.results,total_pipeline,explainer.TOKEN_STATS)
    return op



