#!/usr/bin/env python3
"""Advisory: compute requirement-to-test coverage metrics."""
import json
from pathlib import Path

def main() -> None:
    requirements = json.loads(Path("requirements/analyzed_requirements.json").read_text()) \
        if Path("requirements/analyzed_requirements.json").exists() else []
    matrix = json.loads(Path("reports/traceability_matrix.json").read_text()) \
        if Path("reports/traceability_matrix.json").exists() else []
    covered = sum(1 for r in matrix if r.get("result") not in ("not_run", ""))
    total = len(requirements)
    coverage = round(covered / total * 100, 1) if total > 0 else 0
    print(f"[coverage] {covered}/{total} requirements covered ({coverage}%)")

if __name__ == "__main__":
    main()
