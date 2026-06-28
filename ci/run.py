#!/usr/bin/env python3
"""
Agentic SDLC — Master Pipeline Orchestrator

Drop any requirements document into requirements/ and run this script.
Everything executes autonomously end-to-end:

  Step 1: Analyze requirements   — Claude extracts ACs from any doc format
  Step 2: Generate objectives    — Claude writes kane-cli objective strings per AC
  Step 3: Flow 1 — KaneAI       — kane-cli → code export → HyperExecute → RCA → traceability
  Step 4: Flow 2 — TM API       — reuses Flow 1 kane sessions → TM test cases → HyperExecute → RCA → traceability

Usage:
    ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py              # both flows
    ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py --flow 1     # Flow 1 only
    ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py --flow 2     # Flow 2 only
    ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py --from-step 3 --flow 1  # skip Claude steps

Environment variables:
    ANTHROPIC_API_KEY   Required for Steps 1, 2, and AI RCA summarization
    LT_ACCESS_KEY       Required for Steps 3, 4 (HyperExecute + LT APIs)
    LT_USERNAME         Optional (default: gagandeepb)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CI_DIR       = Path(__file__).parent
PROJECT_ROOT = CI_DIR.parent


# ── Helpers ──────────────────────────────────────────────────────────────────

def _banner(title: str):
    w = 72
    print("\n" + "=" * w)
    print(f"  {title}")
    print("=" * w)


def _run_step(label: str, cmd: list, *, env: dict = None, cwd: Path = None) -> bool:
    """Run a subprocess step, stream output, return True on success."""
    _banner(label)
    print(f"  $ {' '.join(cmd)}\n")

    merged_env = {**os.environ, **(env or {})}
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd or PROJECT_ROOT),
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        print(line, end="", flush=True)
    proc.wait()

    if proc.returncode != 0:
        print(f"\n  [run] FAILED (exit {proc.returncode}): {label}", file=sys.stderr)
        return False

    print(f"\n  [run] OK: {label}")
    return True


def _check_env():
    missing = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.environ.get("LT_ACCESS_KEY"):
        missing.append("LT_ACCESS_KEY")
    if missing:
        print(f"[run] ERROR: Missing required environment variables: {', '.join(missing)}")
        print("  Set them and re-run:")
        for v in missing:
            print(f"    export {v}=<value>")
        sys.exit(1)


# ── Steps ─────────────────────────────────────────────────────────────────────

STEPS = [
    {
        "num":   1,
        "label": "Step 1 — Analyze requirements (Claude extracts ACs)",
        "cmd":   [sys.executable, "-u", "ci/analyze_requirements.py"],
        "needs": ["ANTHROPIC_API_KEY"],
    },
    {
        "num":   2,
        "label": "Step 2 — Generate kane-cli objectives (Claude)",
        "cmd":   [sys.executable, "-u", "ci/generate_objectives.py"],
        "needs": ["ANTHROPIC_API_KEY"],
    },
    {
        "num":   3,
        "label": "Step 3 — Flow 1: KaneAI → Code Export → HyperExecute → RCA",
        "cmd":   [sys.executable, "-u", "ci/flow1_pipeline.py"],
        "needs": ["LT_ACCESS_KEY"],
        "flow":  1,
    },
    {
        "num":   4,
        "label": "Step 4 — Flow 2: KaneAI → TM API → HyperExecute → RCA",
        "cmd":   [sys.executable, "-u", "ci/flow2_pipeline.py"],
        "needs": ["LT_ACCESS_KEY"],
        "flow":  2,
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agentic SDLC master pipeline")
    parser.add_argument("--from-step", type=int, default=1, metavar="N",
                        help="Start from step N (1-4). Default: 1")
    parser.add_argument("--flow", type=int, choices=[1, 2], metavar="N",
                        help="Run only Flow 1 or Flow 2 (still runs steps 1+2 unless --from-step=3)")
    parser.add_argument("--only-step", type=int, metavar="N",
                        help="Run only step N")
    args = parser.parse_args()

    _check_env()

    flow_label = f" (Flow {args.flow} only)" if args.flow else ""
    _banner("AGENTIC SDLC — FULL AUTONOMOUS PIPELINE")
    print("  Requirements → ACs → Objectives → KaneAI → HyperExecute → Traceability")
    print(f"  Starting from step {args.from_step}{flow_label}")

    t_start = time.time()
    failed_steps = []

    for step in STEPS:
        n = step["num"]

        if args.only_step and n != args.only_step:
            continue
        if not args.only_step and n < args.from_step:
            print(f"  [run] Skipping Step {n} (--from-step={args.from_step})")
            continue
        if args.flow and step.get("flow") and step["flow"] != args.flow:
            print(f"  [run] Skipping Step {n} (--flow={args.flow})")
            continue

        ok = _run_step(step["label"], step["cmd"])
        if not ok:
            failed_steps.append(n)
            print(f"\n  [run] Step {n} failed. Continuing to next step...")
            # Continue even on failure — partial results are still useful
            # (self-heal will fix failed SCs on the next full run)

    elapsed = round(time.time() - t_start)
    _banner("PIPELINE COMPLETE")

    if failed_steps:
        print(f"  Steps with errors: {failed_steps}")
        print("  Partial results saved — run again to self-heal failed scenarios")
    else:
        print("  All steps completed successfully!")

    print(f"  Elapsed: {elapsed}s")
    print()
    print("  View results:")
    print(f"    Matrix:  {PROJECT_ROOT}/reports/traceability_matrix.md")
    print(f"    Demo:    python3 ci/demo.py")
    print()

    sys.exit(1 if failed_steps else 0)


if __name__ == "__main__":
    main()
