#!/usr/bin/env python3
"""Advisory: collect pipeline execution metrics and write summary JSON."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def main() -> None:
    api = json.loads(Path("reports/api_details.json").read_text()) \
        if Path("reports/api_details.json").exists() else {}
    matrix = json.loads(Path("reports/traceability_matrix.json").read_text()) \
        if Path("reports/traceability_matrix.json").exists() else []
    requirements = json.loads(Path("requirements/analyzed_requirements.json").read_text()) \
        if Path("requirements/analyzed_requirements.json").exists() else []
    passed = sum(1 for r in matrix if r.get("result") == "passed")
    total  = len(matrix)
    metrics = {
        "run_number":       os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "requirements":     len(requirements),
        "scenarios":        total,
        "passed":           passed,
        "failed":           total - passed,
        "pass_rate":        round(passed / total * 100, 1) if total > 0 else 0,
        "he_job_id":        api.get("he_summary", {}).get("job_id", ""),
    }
    Path("reports").mkdir(exist_ok=True)
    Path("reports/pipeline_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] pass_rate={metrics['pass_rate']}%  requirements={metrics['requirements']}  scenarios={metrics['scenarios']}")

if __name__ == "__main__":
    main()
