#!/usr/bin/env python3
"""Advisory: evaluate quality gates (pass rate, untested requirements)."""
import json
from pathlib import Path

PASS_RATE_THRESHOLD = 80.0

def main() -> None:
    matrix = json.loads(Path("reports/traceability_matrix.json").read_text()) \
        if Path("reports/traceability_matrix.json").exists() else []
    total  = len(matrix)
    passed = sum(1 for r in matrix if r.get("result") == "passed")
    rate   = round(passed / total * 100, 1) if total > 0 else 0
    untested = sum(1 for r in matrix if r.get("result") in ("not_run", ""))
    gates = {
        "pass_rate_gate":    "PASS" if rate >= PASS_RATE_THRESHOLD else "WARN",
        "coverage_gate":     "PASS" if untested == 0 else "WARN",
        "pass_rate":         f"{rate}%",
        "untested":          untested,
    }
    Path("reports/quality_gates.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    print(f"[quality_gates] pass_rate={rate}%  untested={untested}  gates={gates['pass_rate_gate']}/{gates['coverage_gate']}")

if __name__ == "__main__":
    main()
