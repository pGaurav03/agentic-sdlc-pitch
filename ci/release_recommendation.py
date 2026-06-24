#!/usr/bin/env python3
"""Generate QA release verdict based on pass rate thresholds."""
import json
from pathlib import Path

def main() -> None:
    matrix = json.loads(Path("reports/traceability_matrix.json").read_text()) \
        if Path("reports/traceability_matrix.json").exists() else []
    total  = len(matrix)
    passed = sum(1 for r in matrix if r.get("result") == "passed")
    failed = sum(1 for r in matrix if r.get("result") == "failed")
    rate   = round(passed / total * 100, 1) if total > 0 else 0.0

    if total == 0 or rate == 0:
        verdict, rec = "⚠️ YELLOW", "No test results available — manual review required."
    elif rate >= 80:
        verdict, rec = "✅ GREEN", f"Approve release — {passed}/{total} tests passed ({rate}%)."
    elif rate >= 60:
        verdict, rec = "⚠️ YELLOW", f"Conditional release — {failed} test(s) failed. Review before proceeding."
    else:
        verdict, rec = "❌ RED", f"Block release — pass rate {rate}% is below threshold ({failed} failures)."

    failing = "\n".join(f"- {r['sc_id']}: {r['criterion'][:60]}" for r in matrix if r.get("result") == "failed") or "- None"
    content = f"""# QA Release Recommendation
**Verdict:** {verdict}

## Summary
- Requirements covered: {total}/{total}
- Pass rate: {rate}% ({passed} passed, {failed} failed)

## Failing Scenarios
{failing}

## Recommendation
{rec}
"""
    Path("reports").mkdir(exist_ok=True)
    Path("reports/release_recommendation.md").write_text(content, encoding="utf-8")
    print(f"[verdict] {verdict}  pass_rate={rate}%")

if __name__ == "__main__":
    main()
