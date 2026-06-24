#!/usr/bin/env python3
"""
Stage 1 — KaneAI Verification.
Parses requirements/*.txt, builds acceptance criteria, runs kane-cli
to verify each criterion against the live site, writes analyzed_requirements.json.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TARGET_URL = os.environ.get("TARGET_URL", "https://ecommerce-playground.lambdatest.io/")
RUN_NUMBER = os.environ.get("GITHUB_RUN_NUMBER", "local")

# Pre-seeded demo results for DEMO_MODE — no live Kane calls needed
_DEMO_RESULTS = [
    {"id": "AC-001", "description": "User can add a product to the cart from the product detail page and see the cart count update immediately.", "kane_status": "passed", "kane_one_liner": "Add to cart updates counter instantly", "kane_steps": ["Navigate to product page", "Click Add to Cart", "Assert cart count increments"], "kane_summary": "Cart count updates on product add"},
    {"id": "AC-002", "description": "User can open the cart dropdown and see all added items with their names and prices.", "kane_status": "passed", "kane_one_liner": "Cart dropdown shows item names and prices", "kane_steps": ["Add product to cart", "Click cart icon", "Assert items listed with names and prices"], "kane_summary": "Cart dropdown renders item details"},
    {"id": "AC-003", "description": "User can remove an item from the cart and the cart total updates correctly.", "kane_status": "passed", "kane_one_liner": "Remove item recalculates cart total", "kane_steps": ["Add item to cart", "Open cart", "Click remove", "Assert total updates"], "kane_summary": "Item removal triggers total recalculation"},
    {"id": "AC-004", "description": "User can search for a product by name and see relevant results on the search results page.", "kane_status": "passed", "kane_one_liner": "Search returns relevant product results", "kane_steps": ["Type product name in search bar", "Press Enter", "Assert result tiles visible"], "kane_summary": "Search yields matching products"},
    {"id": "AC-005", "description": "User can browse the product catalog and see product tiles with names and prices.", "kane_status": "passed", "kane_one_liner": "Catalog displays product tiles with pricing", "kane_steps": ["Open category page", "Assert product tiles with names and prices visible"], "kane_summary": "Product catalog renders tiles"},
    {"id": "AC-006", "description": "User can click a product tile to open the product detail page showing name, image, and price.", "kane_status": "passed", "kane_one_liner": "Product tile opens detail page with name, image, price", "kane_steps": ["Click product tile", "Assert detail page shows name, image, price"], "kane_summary": "Product detail page renders fully"},
    {"id": "AC-007", "description": "User can apply a category filter to narrow down the displayed products.", "kane_status": "passed", "kane_one_liner": "Category filter narrows product list", "kane_steps": ["Open category", "Click filter", "Assert product count changes"], "kane_summary": "Filter narrows product listing"},
]


def extract_acceptance_criteria(text: str) -> list[str]:
    """Extract AC lines from a requirements text file."""
    criteria = []
    for line in text.splitlines():
        line = line.strip()
        if re.match(r"AC-\d+:", line):
            criteria.append(line)
    return criteria


def parse_all_requirements() -> list[dict]:
    """Parse all *.txt files in requirements/ and return structured AC list."""
    results = []
    req_files = sorted(Path("requirements").glob("*.txt"))
    for req_file in req_files:
        text = req_file.read_text(encoding="utf-8")
        for ac_line in extract_acceptance_criteria(text):
            m = re.match(r"(AC-\d+):\s*(.+)", ac_line)
            if m:
                results.append({"id": m.group(1), "description": m.group(2).strip()})
    return results


def run_kane_verification(ac: dict) -> dict:
    """Run kane-cli for one acceptance criterion and return result dict."""
    objective = (
        f"Verify on {TARGET_URL}: {ac['description']} "
        f"Return PASS if observable, FAIL otherwise."
    )
    print(f"  [kane] {ac['id']}: {objective[:80]}...")
    try:
        result = subprocess.run(
            ["kane-cli", "run", objective, "--output", "json"],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr
        # Parse NDJSON output from kane-cli
        status = "failed"
        one_liner = ""
        steps = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                etype = event.get("type", "")
                if etype == "final_state":
                    data = event.get("data", {})
                    status = "passed" if data.get("success") else "failed"
                    one_liner = data.get("summary", "")[:80]
                    steps = data.get("steps", [])
            except json.JSONDecodeError:
                if "passed" in line.lower() or "success" in line.lower():
                    status = "passed"
        return {**ac, "kane_status": status, "kane_one_liner": one_liner, "kane_steps": steps, "kane_summary": one_liner}
    except subprocess.TimeoutExpired:
        print(f"  [kane] TIMEOUT for {ac['id']}")
        return {**ac, "kane_status": "failed", "kane_one_liner": "Timeout", "kane_steps": [], "kane_summary": "Timeout"}
    except FileNotFoundError:
        print(f"  [kane] kane-cli not found — marking {ac['id']} as failed")
        return {**ac, "kane_status": "failed", "kane_one_liner": "kane-cli not installed", "kane_steps": [], "kane_summary": ""}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo-mode", action="store_true", help="Use pre-seeded results")
    parser.add_argument("--requirements", default="requirements", help="Requirements directory")
    args = parser.parse_args()

    Path("requirements").mkdir(exist_ok=True)
    out_path = Path("requirements/analyzed_requirements.json")

    if args.demo_mode:
        print("[analyze] DEMO MODE — writing pre-seeded Kane results")
        out_path.write_text(json.dumps(_DEMO_RESULTS, indent=2), encoding="utf-8")
        print(f"[analyze] wrote {len(_DEMO_RESULTS)} requirements")
        return

    all_acs = parse_all_requirements()
    if not all_acs:
        print("ERROR: no acceptance criteria found in requirements/*.txt", file=sys.stderr)
        sys.exit(1)

    print(f"[analyze] {len(all_acs)} acceptance criteria found — running KaneAI verification")
    results = []
    for ac in all_acs:
        result = run_kane_verification(ac)
        results.append(result)
        print(f"  {result['id']} → {result['kane_status']}")

    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    passed = sum(1 for r in results if r["kane_status"] == "passed")
    print(f"\n[analyze] complete: {passed}/{len(results)} passed → {out_path}")


if __name__ == "__main__":
    main()
