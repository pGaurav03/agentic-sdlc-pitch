#!/usr/bin/env python3
"""Normalise HyperExecute + Kane artifacts into reports/normalized_results.json."""
import json
from pathlib import Path

def main() -> None:
    api = json.loads(Path("reports/api_details.json").read_text()) if Path("reports/api_details.json").exists() else {}
    he_tasks = api.get("he_tasks", [])
    scenarios = json.loads(Path("scenarios/scenarios.json").read_text()) if Path("scenarios/scenarios.json").exists() else []
    sc_by_fn = {s.get("function_name", ""): s for s in scenarios}

    normalized = []
    for t in he_tasks:
        fn = t.get("name", "")
        sc = sc_by_fn.get(fn, {})
        normalized.append({
            "scenario_id":    sc.get("id", ""),
            "requirement_id": sc.get("requirement_id", ""),
            "test_case_id":   sc.get("test_case_id", ""),
            "function_name":  fn,
            "status":         t.get("status", "unknown"),
            "session_link":   t.get("session_link", ""),
        })

    Path("reports").mkdir(exist_ok=True)
    Path("reports/normalized_results.json").write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    print(f"[normalize] {len(normalized)} result(s) written")

if __name__ == "__main__":
    main()
