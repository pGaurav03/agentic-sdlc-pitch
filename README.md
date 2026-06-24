# Agentic SDLC — LambdaTest

> **Plain-English requirements go in. Executed, traced, and verdicted test results come out. No human writes a single test.**

A fully autonomous Software Development Lifecycle pipeline powered by **KaneAI**, **HyperExecute**, and the **LambdaTest MCP Server** — integrated into GitHub Actions.

---

## How it works

```
You write requirements in plain English
              ↓
    ┌─────────────────────┐
    │  Stage 1 · KaneAI   │  AI agent verifies every acceptance criterion
    │  Verification       │  against the live site using real browsers
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 2 · Scenario │  Syncs scenarios.json — new / updated /
    │  Sync               │  active / deprecated (full audit trail)
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 3 · Test Gen │  Auto-generates Playwright Python tests
    │                     │  from Kane-exported code + curated bodies
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 4 · Select   │  Incremental: only new/updated scenarios
    │                     │  Full run: all active scenarios
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 5 · HyperEx  │  5 parallel VMs × 4 browsers = 28 sessions
    │  ecute              │  Chrome · Firefox · Safari · Android
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 6 · MCP      │  Fetches results via LambdaTest MCP Server
    │  Results            │  → HE REST API → Automation API (fallback)
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Stage 7 · Verdict  │  Traceability matrix + GREEN/YELLOW/RED
    │                     │  release recommendation → GitHub Summary
    └─────────────────────┘
```

---

## LambdaTest products in this pipeline

| Stage | Product | Role |
|-------|---------|------|
| 1 | **KaneAI** | AI agent that runs `kane-cli` to verify each acceptance criterion on real browsers — exports Playwright code |
| 5 | **HyperExecute** | Distributes 7 tests × 4 browsers across 5 parallel VMs — 5-10× faster than sequential CI |
| 6 | **LambdaTest MCP Server** | AI-native result fetching — no polling boilerplate, works with any MCP-compatible AI assistant |
| All | **Automation Dashboard** | Video, network HAR, console logs for every session |

---

## Business value by stakeholder

| Stakeholder | What they see |
|-------------|---------------|
| **QA Lead** | Every requirement traced to a verified functional + multi-browser regression result |
| **Engineering** | Tests auto-regenerate when requirements change — zero manual test maintenance |
| **Release Manager** | Deterministic GREEN / YELLOW / RED verdict with per-criterion evidence |
| **Executives** | One GitHub Actions page shows the complete end-to-end QA story |

---

## Repo structure

```
.github/workflows/agentic-sdlc.yml   ← GitHub Actions (2 jobs: verify + orchestrate)
hyperexecute.yaml                     ← HyperExecute: autosplit, 5 VMs, 4 browsers
requirements/
  cart.txt                            ← AC-001..003  Shopping cart features
  search.txt                          ← AC-004..007  Search & browse features
  analyzed_requirements.json          ← Pre-seeded for demo / cache warm
scenarios/scenarios.json              ← Auto-managed lifecycle tracker
ci/
  analyze_requirements.py             ← Stage 1: kane-cli orchestration
  agent.py                            ← Stages 2-7: full orchestrator
  normalize_artifacts.py              ← Maps HE results → scenarios
  build_traceability.py               ← Req → Scenario → TC → Result matrix
  release_recommendation.py           ← GREEN / YELLOW / RED verdict
  write_github_summary.py             ← GitHub Step Summary (rich markdown)
  coverage_analysis.py                ← Coverage metrics (advisory)
  quality_gates.py                    ← Pass rate threshold checks (advisory)
  pipeline_metrics.py                 ← Pipeline KPIs JSON
  stage_utils.py                      ← Print helpers
tests/playwright/
  conftest.py                         ← LambdaTest CDP fixture + local fallback
  test_scenarios.py                   ← Auto-generated (do not edit manually)
```

---

## Setup

### 1. GitHub Secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Where to get it |
|--------|----------------|
| `LT_USERNAME` | https://accounts.lambdatest.com/security |
| `LT_ACCESS_KEY` | https://accounts.lambdatest.com/security |
| `KANE_PROJECT_ID` | KaneAI → your project → Settings |
| `KANE_FOLDER_ID` | KaneAI → your folder → Settings |

### 2. Push to GitHub

```bash
cd agentic-sdlc-pitch
git init
git add .
git commit -m "feat: agentic SDLC pitch pipeline"
git branch -M main
git remote add origin https://github.com/<your-org>/agentic-sdlc-pitch.git
git push -u origin main
```

---

## Running the pipeline

| Mode | How to trigger | Time |
|------|---------------|------|
| **Demo (instant)** | Actions → Run workflow → ✅ check DEMO MODE | ~30 sec |
| **Full live run** | Push any change under `requirements/` | ~5-8 min |
| **Cached run** | Re-run without changing requirements | ~2-3 min (Kane skipped) |

### Local dry-run

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Stage 1 (demo mode — no kane-cli needed)
.venv/bin/python ci/analyze_requirements.py --demo-mode

# Stages 2-7
FULL_RUN=true .venv/bin/python ci/agent.py
```

---

## Adding your own requirements

Edit any `requirements/*.txt` file — one `AC-NNN: <criterion>` per line:

```
Feature: Checkout

AC-008: User can enter shipping address and proceed to payment.
AC-009: User sees an order confirmation page after successful payment.
```

Push the change — the pipeline automatically:
1. Detects new ACs via hash-based cache key
2. Runs KaneAI to verify them on the live site
3. Generates new Playwright tests (SC-008, TC-008 etc.)
4. Runs them on HyperExecute
5. Outputs updated traceability matrix + verdict

---

## Pitch talking points

- **"Requirements are the only manual input"** — everything downstream is AI-generated and AI-executed
- **KaneAI is the only tool** that verifies requirements against the live site *before* generating tests
- **HyperExecute is the only CI platform** with native autosplit across browsers at 5× speed
- **LambdaTest MCP Server** means any AI coding assistant (Claude Code, GitHub Copilot) can query test results natively — no API boilerplate
- **Full immutable traceability** — every failure traces back to a specific acceptance criterion via SC-NNN → TC-NNN → requirement ID
