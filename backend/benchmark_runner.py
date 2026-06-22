import argparse
import csv
import time
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
import requests

BASE_URL = "http://127.0.0.1:8000/analyze"

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets"
PDF_DIR = DATASET_DIR / "pdf"
TXT_DIR = DATASET_DIR / "txt"
IMG_DIR = DATASET_DIR / "img"

DEFAULT_CSV = Path(__file__).resolve().parent / "benchmark_results.csv"
DEFAULT_SUMMARY = Path(__file__).resolve().parent / "benchmark_summary.txt"

REQUEST_TIMEOUT = 300

PIPELINE_ORDER = [
    "timing_ingestion",
    "timing_preprocessing",
    "timing_embedding",
    "timing_clustering",
    "timing_grouping",
    "timing_keyword extraction",
    "timing_difficulty estimation",
    "timing_output generation",  
]
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


def safe_mean(values):
    values = [v for v in values if v is not None]
    return mean(values) if values else None


def safe_min(values):
    values = [v for v in values if v is not None]
    return min(values) if values else None


def safe_max(values):
    values = [v for v in values if v is not None]
    return max(values) if values else None


def format_metric(value, decimals=3, suffix=""):
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


def maybe_round(value, digits=4):
    if isinstance(value, float):
        return round(value, digits)
    return value


def format_path_for_output(path: Path, base: Path = BASE_DIR):
    path_obj = Path(path)
    if not path_obj.is_absolute():
        return str(path_obj)
    try:
        return str(path_obj.resolve().relative_to(base.resolve()))
    except Exception:
        return path_obj.name


def benchmark_text(file_path: Path, url: str):
    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    start = time.perf_counter()
    try:
        response = requests.post(
            url,
            data={"input_type": "text", "content": content},
            headers={"x-benchmark": "true"},
            timeout=REQUEST_TIMEOUT,
        )
        error = None
        failure_reason = None
    except requests.Timeout as exc:
        response = None
        error = str(exc)
        failure_reason = "Timeout"
    except requests.RequestException as exc:
        response = None
        error = str(exc)
        failure_reason = "Request Failed"

    latency = time.perf_counter() - start
    return response, latency, error, failure_reason


def benchmark_file(file_path: Path, input_type: str, url: str):
    with file_path.open("rb") as file_obj:
        start = time.perf_counter()
        try:
            response = requests.post(
                url,
                data={"input_type": input_type},
                files={"file": (file_path.name, file_obj, "application/octet-stream")},
                headers={"x-benchmark": "true"},
                timeout=REQUEST_TIMEOUT,
            )
            error = None
            failure_reason = None
        except requests.Timeout as exc:
            response = None
            error = str(exc)
            failure_reason = "Timeout"
        except requests.RequestException as exc:
            response = None
            error = str(exc)
            failure_reason = "Request Failed"

    latency = time.perf_counter() - start
    return response, latency, error, failure_reason


def extract_text_metrics(response):
    if response is None:
        return 0, "", {}

    try:
        data = response.json()
    except ValueError:
        return 0, "", {}

    details = ""
    topics = data.get("topics") if isinstance(data, dict) else None
    benchmark_metrics = data.get("benchmark_metrics") if isinstance(data, dict) else None

    if topics is None and isinstance(data, dict):
        topics = data

    if isinstance(data, dict):
        details = data.get("detail", "")

    collected_text = ""

    if isinstance(topics, dict):
        for topic in topics.values():
            if isinstance(topic, dict):
                collected_text += topic.get("explanation", "") + " "

    return len(collected_text.split()), details, benchmark_metrics or {}


def classify_failure(response, error: str, existing_reason):
    if existing_reason:
        return existing_reason

    if response is None:
        return "Request Failed" if error else None

    if 400 <= response.status_code < 500:
        return "Client Error"

    if 500 <= response.status_code < 600:
        return "Server Error"

    return None


def record_result(
    file_path: Path,
    dataset_type: str,
    input_type: str,
    response,
    latency: float,
    error: str,
    failure_reason,
):
    success = response is not None and response.status_code == 200
    status = response.status_code if response is not None else 0
    words, details, benchmark_metrics = extract_text_metrics(response)

    if error and not details:
        details = error

    failure_reason = classify_failure(response, error, failure_reason)

    row = {
        "file": file_path.name,
        "dataset_type": dataset_type,
        "input_type": input_type,
        "status": status,
        "success": success,
        "latency": round(latency, 4),
        "words": words,
        "details": details,
        "failure_reason": failure_reason or "",
    }

    if benchmark_metrics:
        row["metric_num_topics"] = benchmark_metrics.get("num_topics")

        summary = benchmark_metrics.get("metrics_summary", {})
        for key, value in summary.items():
            row[f"metric_{key}"] = maybe_round(value)

        row["silhouette_score"] = maybe_round(benchmark_metrics.get("silhouette_score"))
        row["input_flesch"] = maybe_round(benchmark_metrics.get("input_flesch"))
        row["output_flesch"] = maybe_round(benchmark_metrics.get("output_flesch"))
        row["readability_improvement"] = maybe_round(benchmark_metrics.get("readability_improvement"))

        tokens = benchmark_metrics.get("token_usage", {})
        row["prompt_tokens"] = maybe_round(tokens.get("prompt_tokens"))
        row["completion_tokens"] = maybe_round(tokens.get("completion_tokens"))
        row["total_tokens"] = maybe_round(tokens.get("total_tokens"))

        row["total_pipeline"] = maybe_round(benchmark_metrics.get("total_pipeline"))

        timings = benchmark_metrics.get("timings", {})
        for stage, duration in timings.items():
            row[f"timing_{stage}"] = maybe_round(duration)

    return row


def collect_files():
    files = []

    if PDF_DIR.exists():
        files.extend((file_path, "PDF", "pdf") for file_path in sorted(PDF_DIR.glob("*.pdf")))

    if IMG_DIR.exists():
        for file_path in sorted(IMG_DIR.iterdir()):
            if file_path.suffix.lower() in IMAGE_EXTENSIONS:
                files.append((file_path, "IMG", "image"))

    if TXT_DIR.exists():
        files.extend((file_path, "TXT", "text") for file_path in sorted(TXT_DIR.glob("*.txt")))

    return files


def run_benchmark(url: str):
    results = []
    files = collect_files()

    if not files:
        raise RuntimeError(f"No dataset files found in {format_path_for_output(DATASET_DIR)}")

    benchmark_start = time.perf_counter()

    print("=" * 70)
    print("AI Study Assistant Benchmark")
    print(f"Target URL : {url}")
    print(f"Dataset dir: {format_path_for_output(DATASET_DIR)}")
    print(f"Files found: {len(files)}")
    print("=" * 70)

    total_files = len(files)

    for idx, (file_path, dataset_type, input_type) in enumerate(files, start=1):
        if input_type == "text":
            response, latency, error, failure_reason = benchmark_text(file_path, url)
        else:
            response, latency, error, failure_reason = benchmark_file(file_path, input_type, url)

        result = record_result(
            file_path=file_path,
            dataset_type=dataset_type,
            input_type=input_type,
            response=response,
            latency=latency,
            error=error,
            failure_reason=failure_reason,
        )
        results.append(result)

        status_label = "PASS" if result["success"] else "FAIL"
        message = result["details"] if result["details"] else error or ""
        topics = result.get("metric_num_topics") or "-"
        tokens = result.get("total_tokens") or "-"
        print(
            f"[{idx}/{total_files}] "
            f"{status_label:5} | "
            f"{dataset_type:3} | "
            f"{result['latency']:.2f}s | "
            f"Topics:{topics:<3} | "
            f"Tokens:{str(tokens):<6} | "
            f"{file_path.name}"
        )

        if not result["success"]:
            reason = result.get("failure_reason", "")
            if message or reason:
                extra = f"{reason}: {message}" if reason and message else (reason or message)
                print(f"         ↳ {extra}")

    benchmark_total_time = time.perf_counter() - benchmark_start
    return results, benchmark_total_time


def write_csv(results, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = sorted(results, key=lambda r: (r["dataset_type"], r["file"].lower()))

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        base_fields = [
            "file",
            "dataset_type",
            "input_type",
            "status",
            "success",
            "latency",
            "words",
            "details",
            "failure_reason",
            "silhouette_score",
            "input_flesch",
            "output_flesch",
            "readability_improvement",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "total_pipeline",
        ]

        extra_fields = sorted(
            {
                key
                for row in results
                for key in row.keys()
                if key not in base_fields
            }
        )

        fieldnames = base_fields + extra_fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            cleaned_row = {
                key: maybe_round(value) for key, value in row.items()
            }
            writer.writerow(cleaned_row)


def sort_timing_keys(timing_keys):
    order_map = {name: idx for idx, name in enumerate(PIPELINE_ORDER)}
    return sorted(
        timing_keys,
        key=lambda key: (order_map.get(key, len(PIPELINE_ORDER)), key)
    )


def write_summary(results, summary_path: Path, benchmark_total_time: float, target_url: str):
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(results)
    passed = sum(1 for row in results if row["success"])
    failed = total - passed

    latencies = [row["latency"] for row in results if row.get("latency") is not None]
    avg_latency = safe_mean(latencies)
    latency_std = stdev(latencies) if len(latencies) > 1 else 0
    med_latency = median(latencies) if latencies else None
    min_latency = safe_min(latencies)
    max_latency = safe_max(latencies)

    pipeline_times = [r.get("total_pipeline") for r in results if r.get("total_pipeline") is not None]
    topic_counts = [r.get("metric_num_topics") for r in results if r.get("metric_num_topics") is not None]
    word_counts = [r.get("words") for r in results if r.get("words") is not None]
    prompt_tokens = [r.get("prompt_tokens") for r in results if r.get("prompt_tokens") is not None]
    completion_tokens = [r.get("completion_tokens") for r in results if r.get("completion_tokens") is not None]
    total_tokens = [r.get("total_tokens") for r in results if r.get("total_tokens") is not None]
    readability = [r.get("readability_improvement") for r in results if r.get("readability_improvement") is not None]
    silhouettes = [r.get("silhouette_score") for r in results if r.get("silhouette_score") is not None]

    fastest_row = min(results, key=lambda r: r["latency"]) if results else None
    slowest_row = max(results, key=lambda r: r["latency"]) if results else None

    failure_counts = {}
    for row in results:
        reason = row.get("failure_reason")
        if reason:
            failure_counts[reason] = failure_counts.get(reason, 0) + 1

    groups = {}
    for row in results:
        groups.setdefault(row["dataset_type"], []).append(row)

    timing_keys = sort_timing_keys(
        {
            key
            for row in results
            for key in row.keys()
            if key.startswith("timing_")
        }
    )

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("AI Study Assistant Benchmark Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Benchmark Date          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target URL              : {target_url}\n")
        f.write(f"Dataset dir             : {format_path_for_output(DATASET_DIR)}\n")
        f.write(f"Files tested            : {total}\n")
        f.write(f"Passed                  : {passed}\n")
        f.write(f"Failed                  : {failed}\n")
        f.write(f"Success rate            : {(passed / total * 100):.2f}%\n" if total else "Success rate            : N/A\n")
        f.write(f"Total benchmark time    : {benchmark_total_time:.3f} sec\n")

        f.write("\nLatency Statistics\n")
        f.write("-" * 60 + "\n")
        f.write(f"Average latency         : {format_metric(avg_latency, suffix=' sec')}\n")
        f.write(f"Latency std dev         : {latency_std:.3f} sec\n")
        f.write(f"Median latency          : {format_metric(med_latency, suffix=' sec')}\n")
        f.write(f"Min latency             : {format_metric(min_latency, suffix=' sec')}\n")
        f.write(f"Max latency             : {format_metric(max_latency, suffix=' sec')}\n")

        f.write("\nAggregate Metric Statistics\n")
        f.write("-" * 60 + "\n")
        f.write(f"Average pipeline time   : {format_metric(safe_mean(pipeline_times), suffix=' sec')}\n")
        f.write(f"Average word count      : {format_metric(safe_mean(word_counts))}\n")
        f.write(f"Average num topics      : {format_metric(safe_mean(topic_counts))}\n")
        f.write(f"Average prompt tokens   : {format_metric(safe_mean(prompt_tokens))}\n")
        f.write(f"Average completion toks : {format_metric(safe_mean(completion_tokens))}\n")
        f.write(f"Average total tokens    : {format_metric(safe_mean(total_tokens))}\n")
        f.write(f"Avg readability improve : {format_metric(safe_mean(readability))}\n")
        f.write(f"Average silhouette      : {format_metric(safe_mean(silhouettes))}\n")

        f.write("\nFastest / Slowest Files\n")
        f.write("-" * 60 + "\n")
        if fastest_row:
            f.write(
                f"Fastest file            : {fastest_row['file']} "
                f"({fastest_row['dataset_type']}, {fastest_row['latency']:.3f} sec)\n"
            )
        else:
            f.write("Fastest file            : N/A\n")

        if slowest_row:
            f.write(
                f"Slowest file            : {slowest_row['file']} "
                f"({slowest_row['dataset_type']}, {slowest_row['latency']:.3f} sec)\n"
            )
        else:
            f.write("Slowest file            : N/A\n")

        f.write("\nBreakdown by Dataset Type\n")
        f.write("-" * 60 + "\n")
        for dataset_type, rows in sorted(groups.items()):
            count = len(rows)
            success = sum(1 for row in rows if row["success"])
            success_pct = (success / count * 100) if count else 0

            lat = [row.get("latency") for row in rows if row.get("latency") is not None]
            pipe = [row.get("total_pipeline") for row in rows if row.get("total_pipeline") is not None]
            toks = [row.get("total_tokens") for row in rows if row.get("total_tokens") is not None]
            read = [row.get("readability_improvement") for row in rows if row.get("readability_improvement") is not None]
            words = [row.get("words") for row in rows if row.get("words") is not None]
            topics = [row.get("metric_num_topics") for row in rows if row.get("metric_num_topics") is not None]

            f.write(f"{dataset_type}\n")
            f.write(f"  Files                 : {count}\n")
            f.write(f"  Success               : {success}/{count} ({success_pct:.2f}%)\n")
            f.write(f"  Avg latency           : {format_metric(safe_mean(lat), suffix=' sec')}\n")
            f.write(f"  Avg pipeline time     : {format_metric(safe_mean(pipe), suffix=' sec')}\n")
            f.write(f"  Avg total tokens      : {format_metric(safe_mean(toks))}\n")
            f.write(f"  Avg readability gain  : {format_metric(safe_mean(read))}\n")
            f.write(f"  Avg word count        : {format_metric(safe_mean(words))}\n")
            f.write(f"  Avg num topics        : {format_metric(safe_mean(topics))}\n")
            f.write("\n")

        if failure_counts:
            f.write("Failure Breakdown\n")
            f.write("-" * 60 + "\n")
            for reason, count in sorted(failure_counts.items()):
                f.write(f"{reason:<24}: {count}\n")
            f.write("\n")

        if timing_keys:
            f.write("Average Pipeline Timings\n")
            f.write("-" * 60 + "\n")
            for key in timing_keys:
                values = [row.get(key) for row in results if row.get(key) is not None]
                if values:
                    f.write(f"{key:<30}{safe_mean(values):.3f} sec\n")

        f.write("\nDetailed results are available in the CSV file.\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run dataset benchmark against the AI Study Assistant backend."
    )
    parser.add_argument("--url", "-u", default=BASE_URL, help="Analysis endpoint URL")
    parser.add_argument(
        "--output-csv",
        "-o",
        default=DEFAULT_CSV,
        type=Path,
        help="Path to write benchmark CSV",
    )
    parser.add_argument(
        "--summary",
        "-s",
        default=DEFAULT_SUMMARY,
        type=Path,
        help="Path to write summary report",
    )
    return parser.parse_args()


def main():
    try:
        args = parse_args()

        results, benchmark_total_time = run_benchmark(args.url)
        write_csv(results, args.output_csv)
        write_summary(results, args.summary, benchmark_total_time, args.url)

        passed = sum(1 for row in results if row["success"])
        total = len(results)
        avg_latency = safe_mean([row["latency"] for row in results if row.get("latency") is not None])
        avg_pipeline = safe_mean([row.get("total_pipeline") for row in results if row.get("total_pipeline") is not None])
        avg_tokens = safe_mean([row.get("total_tokens") for row in results if row.get("total_tokens") is not None])

        print("\n" + "=" * 70)
        print("Benchmark finished")
        print(f"CSV report written to    : {format_path_for_output(args.output_csv)}")
        print(f"Summary report written to: {format_path_for_output(args.summary)}")
        print("-" * 70)
        print(f"Passed            : {passed}/{total}")
        print(f"Average Latency   : {format_metric(avg_latency, suffix=' sec')}")
        print(f"Average Pipeline  : {format_metric(avg_pipeline, suffix=' sec')}")
        print(f"Average Tokens    : {format_metric(avg_tokens)}")

    except KeyboardInterrupt:
        print("\nBenchmark cancelled.")


if __name__ == "__main__":
    main()