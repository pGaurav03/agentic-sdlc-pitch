# Demo Script — Agentic SDLC Pitch

> Run time: ~8 min live | ~90 sec with DEMO MODE
> Audience: CTO, VP Eng, QA Lead

---

## Before the call (5 min setup)

1. Open these tabs in advance:
   - GitHub Actions page for this repo
   - LambdaTest HyperExecute Dashboard: https://hyperexecute.lambdatest.com/
   - LambdaTest Automation Dashboard: https://automation.lambdatest.com/
   - KaneAI: https://app.lambdatest.com/kane-ai

2. Have the repo's `requirements/cart.txt` open in your editor

---

## The hook (30 sec)

> *"What if your QA pipeline wrote its own tests, ran them across 4 browsers in parallel,
> and told you whether to ship — automatically — every time a developer pushed code?"*

Show the `requirements/cart.txt` file:

```
AC-001: User can add a product to the cart from the product detail page
        and see the cart count update immediately.
```

> *"This is the only thing a human writes. Everything else — tests, execution, traceability,
> release verdict — is automated."*

---

## Trigger the pipeline (live or demo mode)

### Option A — DEMO MODE (safest, <90 sec)
1. Go to **Actions → Agentic SDLC — LambdaTest Pitch Pipeline**
2. Click **Run workflow**
3. Check ✅ **DEMO MODE**
4. Click **Run workflow**

### Option B — Full live run (~8 min)
1. Edit `requirements/cart.txt` — add one new AC line:
   ```
   AC-008: User sees a success message after adding a product to the cart.
   ```
2. Commit + push
3. Watch the pipeline trigger automatically

---

## Walk through each stage (while it runs)

### Stage 1 — KaneAI Verification
> *"KaneAI is running as an AI agent inside a real Chrome browser on LambdaTest.
> It's navigating the live site, verifying each acceptance criterion is actually
> observable — not just syntactically valid. No other tool does this."*

Point to the step logs showing: `AC-001 → passed`

### Stage 2 — Scenario Sync
> *"Every acceptance criterion gets a stable immutable ID — SC-001, SC-002.
> It tracks lifecycle: new, updated, active, deprecated. Full audit trail."*

### Stage 3 — Test Generation
> *"The pipeline just wrote 7 Playwright tests. Zero human authoring.
> These are real executable tests, not templates — they come from Kane's
> exported browser automation code."*

Show `tests/playwright/test_scenarios.py` (auto-generated).

### Stage 4 — Test Selection
> *"Incremental by default — only runs tests for new or changed requirements.
> Add one AC, run one test. Full run available on demand."*

### Stage 5 — HyperExecute
> *"28 parallel sessions — 7 tests × 4 browsers — running simultaneously
> on 5 cloud VMs. Sequential CI would take 20+ minutes. This takes 2."*

Switch to **HyperExecute Dashboard** — show the live job grid.

### Stage 6 — MCP Result Fetch
> *"The LambdaTest MCP Server means any AI assistant — Claude Code,
> GitHub Copilot — can query these results natively. No API boilerplate.
> This is how AI-native DevOps works."*

### Stage 7 — Verdict
> *"GREEN means ship. YELLOW means review. RED means block.
> Every verdict links back to a specific acceptance criterion and user story."*

Show the GitHub Step Summary with the full traceability table.

---

## The close

> *"Your team wrote one line of plain English.
> The platform verified it on a real browser, wrote the test, ran it across
> Chrome + Firefox + Safari + Android, fetched the results via AI-native API,
> and told you whether to ship — in under 10 minutes.
> That's Agentic SDLC."*

**Ask:** *"What's the biggest bottleneck in your current QA cycle?"*

---

## Objection handling

| Objection | Response |
|-----------|----------|
| "We already have Cypress/Playwright tests" | "Great — HyperExecute runs those 5-10× faster today, zero migration. KaneAI + the agentic layer is what you add on top." |
| "KaneAI looks expensive" | "Compare it to 1 QA engineer-month of test writing. This pipeline eliminates that entirely for every sprint." |
| "What if Kane misses something?" | "Stage 3 always generates a test even if Kane flags a criterion as uncertain — you get coverage regardless." |
| "We can't share our app URL" | "Lambda Tunnel — private/localhost apps work exactly the same way via our tunnel." |
