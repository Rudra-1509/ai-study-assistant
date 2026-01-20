def difficulty_estimator(topic_chunks:dict[int,list[str]],topic_keywords:dict[int,list[str]])->dict[int,dict]:
    if not topic_chunks or not topic_keywords:
        raise ValueError("Chunks and keywords must not be empty")
    difficulty_by_topic={}
    #total_score=f1+f2+f3
    
    for label,chunks in topic_chunks.items():
        #feature 1: Keyword complexity-> get avgKeywordLength per topic and divide it by 10
        keywords=topic_keywords.get(label,[])
        if keywords:
            avg_keyword_len=sum(len(kw) for kw in keywords)/len(keywords)
        else:
            avg_keyword_len=0
        f1_score=avg_keyword_len/10

        #feature 2: Cognitive load-> get avg chunk length(total words) and divide it by 100
        total_words=sum(len(chunk.split()) for chunk in chunks)
        avg_chunk_len=total_words/max(len(chunks),1)
        f2_score=avg_chunk_len/100

        #feature 3: Topic breadth-> get total number of chunks in a topic and divide it by 5
        total_chunks=max(len(chunks),1)
        f3_score=total_chunks/5

        total_score=f1_score+f2_score+f3_score
        if total_score<1.5:
            difficulty='easy'
        elif total_score<3:
            difficulty='medium'
        else:
            difficulty='hard'
        
        difficulty_by_topic[label]={
            "difficulty":difficulty,
            "score":round(total_score,3)
        }
        
    return difficulty_by_topic


        
