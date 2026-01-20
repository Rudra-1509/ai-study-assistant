def keyword_coverage(explanation:str, keywords:list[str])->float:
    if not keywords or not explanation:
        return 0.0
    explanation_words=set(explanation.lower().split())
    keywords=set(keywords)
    covered=sum(1 for word in keywords if word in explanation_words)
    return round(covered/len(keywords),3)

def expected_length_range(difficulty: str) -> tuple[int, int]:
    return {
        "easy": (100, 200),
        "medium": (200, 400),
        "hard": (400, 700)
    }.get(difficulty, (150, 350))

def compute_metrics(explanations:dict[int,dict])->dict:
    topic_metrics = {}
    total_words = 0
    total_coverage = 0.0

    for label,data in explanations.items():
        explanation=data["explanation"]
        keywords = data["keywords"]
        difficulty = data["difficulty"]

        word_count=len(explanation.split())
        coverage=keyword_coverage(explanation,keywords)
        low,high=expected_length_range(difficulty)
        is_length_ok=low<=word_count<=high

        topic_metrics[label]={
            "word_count":word_count,
            "keyword_coverage":coverage,
            "is_length_ok_for_difficulty":is_length_ok
        }
        total_words+=word_count
        total_coverage+=coverage
    
    summary={
        "num_topics": len(explanations),
        "avg_word_count": round(total_words / max(len(explanations), 1), 2),
        "avg_keyword_coverage": round(total_coverage / max(len(explanations), 1), 3)
    }

    return{
        "per_topic":topic_metrics,
        "summary":summary
    }