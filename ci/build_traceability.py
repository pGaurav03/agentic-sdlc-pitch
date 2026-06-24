#!/usr/bin/env python3
"""Build requirements → scenarios → test cases → results traceability matrix."""
import json
from pathlib import Path

def main() -> None:
    requirements = json.loads(Path("requirements/analyzed_requirements.json").read_text()) \
        if Path("requirements/analyzed_requirements.json").exists() else []
    scenarios = json.loads(Path("scenarios/scenarios.json").read_text()) \
        if Path("scenarios/scenarios.json").exists() else []
    normalized = json.loads(Path("reports/normalized_results.json").read_text()) \
        if Path("reports/normalized_results.json").exists() else []

    results_by_sc = {r["scenario_id"]: r for r in normalized}
    sc_by_req = {s["requirement_id"]: s for s in scenarios}

    rows = []
    passed = failed = untested = 0
    for req in requirements:
        sc = sc_by_req.get(req["id"], {})
        sc_id = sc.get("id", "—")
        tc_id = sc.get("test_case_id", "—")
        kane  = req.get("kane_status", "—")
        result = results_by_sc.get(sc_id, {})
        test_result = result.get("status", "not_run")
        link = result.get("session_link", "")
        overall = "✅" if test_result == "passed" else ("❌" if test_result == "failed" else "⏭")
        if test_result == "passed":   passed += 1
        elif test_result == "failed": failed += 1
        else:                          untested += 1
        rows.append({
            "req_id": req["id"], "criterion": req["description"][:80],
            "sc_id": sc_id, "tc_id": tc_id,
            "kane": kane, "result": test_result, "link": link, "overall": overall,
        })

    total = len(rows)
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    # Markdown report
    lines = ["# Traceability Matrix\n",
             f"| Req | Acceptance Criterion | Scenario | TC | KaneAI | Result | Overall |",
             f"| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        link_md = f"[{r['result']}]({r['link']})" if r["link"] else r["result"]
        lines.append(f"| {r['req_id']} | {r['criterion']} | {r['sc_id']} | {r['tc_id']} | {r['kane']} | {link_md} | {r['overall']} |")

    lines += ["",
              f"## Summary",
              f"- Requirements: {total}",
              f"- Passed: {passed}  Failed: {failed}  Untested: {untested}",
              f"- Pass rate: {pass_rate}%"]

    Path("reports").mkdir(exist_ok=True)
    Path("reports/traceability_matrix.md").write_text("\n".join(lines), encoding="utf-8")
    Path("reports/traceability_matrix.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[traceability] {total} rows — {passed} passed ({pass_rate}%)")

if __name__ == "__main__":
    main()
