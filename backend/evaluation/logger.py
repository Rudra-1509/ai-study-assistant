import json
import os
from datetime import datetime, timezone

LOG_FILE = "backend/run_logs.jsonl"

def log_run(input_text: str, explanations: dict, metrics: dict) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_length_chars": len(input_text),
        "num_topics": len(explanations),
        "metrics_summary": metrics.get("summary", {}),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
