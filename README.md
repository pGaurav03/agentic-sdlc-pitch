# Agentic SDLC — LambdaTest

> Requirements go in. **KaneAI authors the tests.** HyperExecute runs them. Traced results come out. Zero human test writing.

---

## KaneAI is the test author

Every test in this pipeline is authored by **KaneAI** — LambdaTest's AI agent for browser test creation.

You give KaneAI a plain-English objective like:

> *"Go to automationexercise.com, search for 'jeans', and verify relevant products appear"*

KaneAI opens a real browser, figures out the UI, executes the steps, and either **exports production-ready Playwright code** (Flow 1) or **saves the test directly into Test Manager** (Flow 2).

No selectors. No scripts. No page objects. KaneAI handles all of it.

---

## Pipeline stages — step by step

### Stage 1 — Requirement Analysis _(Claude)_
**Input:** Any `.txt` or `.md` file in `requirements/` — free text, user stories, bullet points, anything
**What happens:** Claude reads all files and extracts structured Acceptance Criteria
**Output:** `requirements/analyzed_requirements.json`
```json
[{ "id": "AC-001", "description": "User can add a product to cart and see count update",
   "kane_steps": ["Navigate to product", "Click Add to Cart", "Assert cart count increments"],
   "kane_one_liner": "Add to cart updates counter instantly" }]
```

---

### Stage 2 — Objective Generation _(Claude)_
**Input:** `analyzed_requirements.json`
**What happens:** Claude writes a precise, grounded kane-cli objective string for each AC — including the exact URL, UI actions, and assertion
**Output:** `ci/objectives.json`
```json
[{ "id": "SC-001", "ac_id": "AC-001",
   "objective": "Go to https://automationexercise.com/, search for 'Blue Top', click Add to Cart on the first result, and verify the cart count increases" }]
```

---

### Stage 3 — KaneAI Test Authoring _(kane-cli, Phase 1)_
**Input:** `ci/objectives.json` — one objective per SC
**What happens:** `kane-cli` runs each objective on a **real browser** using AI vision — no selectors, no pre-written scripts. KaneAI figures out the UI autonomously.

- **Flow 1:** KaneAI exports Playwright Python code → saved to `~/.testmuai/kaneai/sessions/<id>/code-export/test.py`
- **Flow 2:** KaneAI saves the test directly into LambdaTest Test Manager → returns a `testcase_id`

**Output:** Session dirs with code exports (Flow 1) / TM test case IDs (Flow 2)
**If a SC fails:** Failure detail saved to `ci/run_history.json` → Claude rewrites the objective on the next run (self-heal)

---

### Stage 4 — Test Preparation _(Phase 2)_

**Flow 1:** Transforms KaneAI's async code export → synchronous LT CDP Playwright test → writes to `tests/playwright/kane/SC-XXX/test.py`

**Flow 2:** Creates a Test Manager test run, sets environment (Win10 / Firefox), links all KaneAI test cases

---

### Stage 5 — Parallel Execution _(HyperExecute, Phase 3)_
**Input:** Test files (Flow 1) / TM test run (Flow 2)
**What happens:** HyperExecute distributes tests across parallel VMs — all KaneAI-authored tests run simultaneously
**Output:** HE job ID + job link → saved to `ci/he_jobs.json`

---

### Stage 6 — AI Root Cause Analysis _(LambdaTest AI)_
**Input:** HE job ID
**What happens:**
1. `POST /insights/api/v3/public/rca/generate` — triggers LT AI RCA for all failed sessions in the job
2. Wait 30s for async generation
3. `GET /automation/api/v1/sessions/{id}/rca` — fetch RCA per failed session
4. Claude Haiku summarises into 3 bullets: _what failed / why / how to fix_

**Output:** `ci/rca_results.json` — SC-id → RCA text + session link

---

### Stage 7 — Traceability Matrix
**Input:** All pipeline data files (`objectives.json`, `run_history.json`, `tm_test_cases.json`, `he_jobs.json`, `rca_results.json`)
**What happens:** Builds a live matrix linking every result back to its origin
**Output:**
- `reports/traceability_matrix.md` — full markdown table (appears in GitHub Step Summary)
- `reports/demo_cache.json` — cached results for instant demo replay

```
Requirement → AC → KaneAI Objective → SC → HE Test → Result → AI RCA
```

---

## Edge cases handled

| Situation | How it's handled |
|-----------|-----------------|
| kane-cli SC times out | Marked `failed` in `run_history.json`; Claude rewrites objective on next run |
| All SCs fail Phase 1 | Pipeline logs error and aborts before HE — no empty job submitted |
| Code export missing for an SC | That SC is skipped in Phase 2; others still run on HE |
| HE job ID not captured | RCA and traceability steps are skipped gracefully; results still saved |
| RCA not ready in 30s | Traceability shows `—` for RCA; next run appends to existing results |
| `analyzed_requirements.json` missing at `from_step=2` | `generate_objectives.py` exits with a clear error message |
| `objectives.json` missing at `from_step=3` | `flow1_pipeline.py` falls back to hardcoded SC-001..SC-006 objectives |
| Two pushes in quick succession | `concurrency` group in `flow1.yml` cancels the older run, keeps only the latest |
| Flow 2 triggered on push | Flow 2 has **no push trigger** — manual only, prevents parallel kane-cli collisions |
| Demo cache missing | `ci/demo.py` prints a clear message: _"Run a pipeline first"_ |

---

## GitHub Actions

| Workflow | Trigger | Time |
|----------|---------|------|
| **Flow 1** (`flow1.yml`) | Push to `requirements/` or `ci/`, or manual | ~15–20 min |
| **Flow 1 Demo** (`flow1-demo.yml`) | Auto after Flow 1 completes, or manual | ~30 sec |
| **Flow 2** (`flow2.yml`) | **Manual only** (no push trigger — prevents collision with Flow 1) | ~15–20 min |
| **Flow 2 Demo** (`flow2-demo.yml`) | Auto after Flow 2 completes, or manual | ~30 sec |

### `from_step` options (manual dispatch)

| Value | Skips | Use when |
|-------|-------|----------|
| `1` (default) | Nothing | New or changed requirements |
| `2` | Stage 1 (requirement analysis) | Requirements unchanged, re-generate objectives only |
| `3` | Stages 1 + 2 (both Claude steps) | Objectives already exist, just re-run the pipeline |

---

## Setup

### 1. Add secrets

**Settings → Secrets and variables → Actions**

| Secret | Where to find it |
|--------|-----------------|
| `LT_USERNAME` | https://accounts.lambdatest.com/security |
| `LT_ACCESS_KEY` | https://accounts.lambdatest.com/security |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `KANE_PROJECT_ID` | KaneAI → Project → Settings |
| `KANE_FOLDER_ID` | KaneAI → Folder → Settings |

### 2. Push to trigger Flow 1

```bash
git push origin main
```

Flow 2 runs manually: **Actions → Flow 2 — KaneAI TM API → Run workflow**

---

## Running locally

```bash
pip install -r requirements.txt

# Full run — both flows
ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py

# One flow only
ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py --flow 1
ANTHROPIC_API_KEY=<key> LT_ACCESS_KEY=<key> python3 ci/run.py --flow 2

# Skip Claude stages, re-run pipeline only
LT_ACCESS_KEY=<key> python3 ci/run.py --from-step 3 --flow 1

# Show results from last run (instant — no re-run)
python3 ci/demo.py

# Show results + open HyperExecute dashboard in browser
python3 ci/demo.py --open
```

---

## Adding requirements

Drop any `.txt` or `.md` file into `requirements/`. No format required:

```
# requirements/checkout.md

Users should be able to add items to cart and see the count update.
On the cart page, item names and prices must be visible.
Removing an item should clear it from the cart immediately.
```

Push → Flow 1 triggers → Claude reads it → KaneAI authors new tests → HyperExecute runs them → traceability matrix updates.

---

## What makes this different

- **KaneAI authors every test** — no human writes selectors, scripts, or page objects; KaneAI uses AI vision to interact with the real UI
- **KaneAI is the only tool** that verifies requirements against a live site *and* generates production-ready tests from that verification
- **Two KaneAI output paths** — Flow 1 gets Playwright code export; Flow 2 gets Test Manager test cases — same AI author, two execution strategies
- **Self-healing** — when a KaneAI test fails, Claude rewrites the objective and KaneAI re-authors it on the next run
- **Full traceability** — every HyperExecute result links back to the KaneAI test, the objective, and the original acceptance criterion
- **AI root cause analysis** — LambdaTest AI explains each failure in 3 bullets: what failed, why, how to fix it
- **Demo in 30 seconds** — the demo workflow shows real results from the last KaneAI run without re-running anything
