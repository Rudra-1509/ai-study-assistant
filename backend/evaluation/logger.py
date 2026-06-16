import json
from datetime import datetime, timezone

LOG_FILE = "run_logs.jsonl"

def log_run(
    input_text: str,
    explanations: dict,
    metrics: dict,
    silhouette:float,
    input_flesch:float,
    output_flesch:float,
    timings: dict,
    total_pipeline: float,
    token_stats: dict
) -> None:
    improvement = output_flesch - input_flesch
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_length_chars": len(input_text),
        "num_topics": len(explanations),
        "metrics_summary": metrics.get("summary", {}),
        "silhouette_score":silhouette,
        "input_flesch":input_flesch,
        "output_flesch":output_flesch,
        "readbility_improvement":improvement,
        "token_usage": {
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        },
        "timings": timings,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Console output
    print("\n========== RUN SUMMARY ==========")
    print(f"Input Length : {len(input_text)} chars")
    print(f"Topics Found : {len(explanations)}")

    print("\nMetrics:")
    for key, value in metrics.get("summary", {}).items():
        print(f"  {key}: {value}")
    if silhouette is not None:
        print(f"  silhouette_score: {silhouette:.3f}")
    else:
        print(f"  silhouette_score: N/A")

    print("\nReadability:")
    print(f"  input_flesch: {input_flesch:.2f}")
    print(f"  output_flesch: {output_flesch:.2f}")
    if(improvement>=0):
        print(f"  readability_improvement: +{improvement:.2f}")
    else:
        print(f"  readability_improvement: {improvement:.2f}")
        
    print("\nToken Usage:")
    print(f"  prompt_tokens: {token_stats['prompt_tokens']}")
    print(f"  completion_tokens: {token_stats['completion_tokens']}")
    print(f"  total_tokens: {token_stats['total_tokens']}")  
        
    print("\nTimings:")
    for stage, duration in timings.items():
        print(f"  {stage}: {duration:.3f}s")

    print(f"\nTotal Pipeline: {total_pipeline:.3f}s")

    print("=================================\n")