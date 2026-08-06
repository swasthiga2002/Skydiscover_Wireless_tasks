---
layout: page
title: Evaluation
permalink: /evaluation/
---

<div class="topnav">
<style>
  .topnav {
    --tn-ink: #1e2b3c; --tn-ink-soft: #5b6b80; --tn-bg: #f6f8fb; --tn-line: #d3dce6; --tn-accent: #b8611f;
    display: flex; flex-wrap: wrap; gap: 4px 4px; align-items: center;
    margin: 0 0 22px; padding: 8px; border: 1px solid var(--tn-line); background: var(--tn-bg);
    font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; font-size: 13.5px;
  }
  @media (prefers-color-scheme: dark) {
    .topnav { --tn-ink: #e7edf5; --tn-ink-soft: #9db0c4; --tn-bg: #141f2d; --tn-line: #263344; --tn-accent: #eb9a51; }
  }
  .topnav a {
    color: var(--tn-ink-soft); text-decoration: none; padding: 5px 10px; border-radius: 3px;
  }
  .topnav a:hover { color: var(--tn-ink); background: var(--tn-line); }
  .topnav a.current { color: var(--tn-accent); font-weight: 600; }
  .topnav .sep { color: var(--tn-line); }
</style>
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="current">Evaluation</a><span class="sep">/</span><a href="{{ '/getting-started/' | relative_url }}" class="">Getting Started</a>
</div>

# Evaluation

**How many times each framework calls its evaluation tool, and how many LLM calls it spends getting there** — measured directly from real run logs, not from configuration alone. 5 runs x 10 iterations/generations, same channel-estimation benchmark as the [Quantitative](/quantitative/) page.

## Summary

| | AI Telco Engineer (50 generations) | EvoX / SkyDiscover (50 iterations, 5 runs) |
|---|---|---|
| Evaluation calls per iteration | 1-3 (avg 1.2) | always 1 |
| LLM calls per iteration | 4-28 (avg 8.8) | 1-6 (avg 3.6) |
| Sionna doc retrievals per iteration | 0-7 (avg 2.1) | 0 (context is pre-assembled into the prompt, no retrieval tool) |

- **Evaluation grid density differs between frameworks.** SkyDiscover's NVE is averaged over 7 SNR points (-9 to -2 dB, 1 dB step); AI Telco Engineer averages over 4 (-9 to -2 dB, 2 dB step) -- see [Quantitative](/quantitative/) for how this affects the reported best-NVE comparison.

## The Retry Loop, Simplified

Both frameworks now enforce the identical retry contract -- up to 3 evaluation calls, stop immediately on success, corrective retry on failure using the exact error seen.

<div class="eval-diag">
<style>
  .eval-diag {
    --ed-bg: #f6f8fb; --ed-ink: #1e2b3c; --ed-ink-soft: #5b6b80; --ed-ink-faint: #a7b3c2;
    --ed-accent: #b8611f; --ed-accent-soft: #b8611f1c; --ed-store: #227368; --ed-store-soft: #2273681a;
    --ed-panel: #ffffff; --ed-line: #d3dce6;
    display: block; box-sizing: border-box; margin: 22px 0 30px;
    font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; color: var(--ed-ink);
  }
  @media (prefers-color-scheme: dark) {
    .eval-diag {
      --ed-bg: #0e1620; --ed-ink: #e7edf5; --ed-ink-soft: #9db0c4; --ed-ink-faint: #4d6076;
      --ed-accent: #eb9a51; --ed-accent-soft: #eb9a5124; --ed-store: #57d3c1; --ed-store-soft: #57d3c11c;
      --ed-panel: #141f2d; --ed-line: #263344;
    }
  }
  .eval-diag, .eval-diag * { box-sizing: border-box; }
  .eval-diag .ed-cols {
    display: grid; grid-template-columns: 1fr 1fr; gap: 22px;
  }
  @media (max-width: 720px) { .eval-diag .ed-cols { grid-template-columns: 1fr; } }
  .eval-diag .ed-col-title {
    font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ed-ink-soft);
    margin: 0 0 10px; font-family: ui-monospace, "SF Mono", Consolas, monospace;
  }
  .eval-diag .ed-flow { display: flex; flex-direction: column; gap: 0; }
  .eval-diag .ed-box {
    border: 1.5px solid var(--ed-ink-faint); background: var(--ed-panel);
    padding: 9px 12px; font-size: 12.5px; line-height: 1.4;
  }
  .eval-diag .ed-box.llm { border-color: var(--ed-accent); background: linear-gradient(0deg, var(--ed-accent-soft), var(--ed-accent-soft)), var(--ed-panel); }
  .eval-diag .ed-box.store { border-color: var(--ed-store); background: linear-gradient(0deg, var(--ed-store-soft), var(--ed-store-soft)), var(--ed-panel); }
  .eval-diag .ed-box .ed-tag {
    display: block; font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 8.5px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ed-ink-faint); margin-bottom: 2px;
  }
  .eval-diag .ed-box.llm .ed-tag { color: var(--ed-accent); }
  .eval-diag .ed-box.store .ed-tag { color: var(--ed-store); }
  .eval-diag .ed-arrow { align-self: center; color: var(--ed-ink-faint); font-size: 14px; padding: 3px 0; }
  .eval-diag .ed-branch {
    font-size: 11.5px; color: var(--ed-ink-soft); margin: 4px 0 0 2px; padding-left: 10px;
    border-left: 2px solid var(--ed-line);
  }
  .eval-diag .ed-note {
    margin-top: 14px; padding: 10px 14px; border: 1px dashed var(--ed-line);
    background: var(--ed-bg); font-size: 12.5px; color: var(--ed-ink-soft); line-height: 1.5;
  }
</style>

<div class="ed-cols">
  <div>
    <p class="ed-col-title">EvoX / SkyDiscover</p>
    <div class="ed-flow">
      <div class="ed-box"><span class="ed-tag">Logic</span>Sample parent + build prompt</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box llm"><span class="ed-tag">LLM call</span>Generate a candidate solution — exactly 1 call, everything needed is already in the prompt</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Evaluate the candidate</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Success?</div>
      <div class="ed-branch">Yes → add to database, iteration done<br>No → append the exact error, retry (up to 3 total)</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box store"><span class="ed-tag">Storage</span>All 3 fail? Discard — no candidate added this iteration</div>
    </div>
  </div>
  <div>
    <p class="ed-col-title">AI Telco Engineer</p>
    <div class="ed-flow">
      <div class="ed-box llm"><span class="ed-tag">LLM call(s)</span>Research + write draft.py — an open-ended agentic loop: docs lookup, file reads, exploratory code, as many LLM turns as it wants</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Evaluate draft.py</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Success?</div>
      <div class="ed-branch">Yes → copy draft.py → solution.py, stop<br>No → fix draft.py using the exact error, retry (up to 3 total)</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box store"><span class="ed-tag">Storage</span>All 3 fail? Leave solution.py unset — post-run eval scores draft.py as-is</div>
    </div>
  </div>
</div>

<div class="ed-note">Both loops now share the identical retry contract — up to 3 evaluation calls, stop immediately on success, corrective retry on failure using the exact error. The structural difference is what "generate a candidate" costs: EvoX spends exactly 1 LLM call per attempt (all context is pre-assembled into the prompt), while AI Telco Engineer's agent can spend anywhere from 4 to 28+ LLM turns per generation, since it's free to research documentation, read files, and run exploratory code before ever calling evaluate. See the tables below for the actual observed range across 50 runs of each.</div>
</div>


## Full Data

Every number below comes directly from parsing run journals/logs (`journal.log` for AI Telco Engineer, the `skydiscover.search.*` run log + `search/iteration_N/` artifacts for EvoX). "LLM calls" counts distinct model turns (grouped by timestamp for AI Telco Engineer's tool-call batches; each retry attempt for EvoX, since every attempt is exactly one model turn).

### AI Telco Engineer — per generation

**Run 1**

| Gen | Eval calls | LLM calls | Sionna retrievals | Purpose breakdown |
|---|---|---|---|---|
| 0 | 3 | 11 | 4 | List workspace files ×1, Sionna doc retrieval ×2, Read a file ×1, Write draft.py ×1, Evaluate ×3, Edit draft.py (fix) ×2, Save solution.py ×1, Final summary ×1 |
| 1 | 1 | 19 | 6 | List workspace files ×1, Sionna doc retrieval ×5, Run exploratory Python ×10, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 2 | 1 | 6 | 2 | Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 3 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 4 | 1 | 14 | 1 | Sionna doc retrieval ×1, Run exploratory Python ×9, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 5 | 1 | 9 | 4 | List workspace files ×1, Sionna doc retrieval ×4, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 6 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 7 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 8 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 9 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |

**Run 2**

| Gen | Eval calls | LLM calls | Sionna retrievals | Purpose breakdown |
|---|---|---|---|---|
| 0 | 2 | 15 | 5 | List workspace files ×1, Sionna doc retrieval ×2, Run exploratory Python ×6, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 1 | 1 | 12 | 5 | Sionna doc retrieval ×3, Run exploratory Python ×5, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 2 | 1 | 13 | 2 | List workspace files ×2, Sionna doc retrieval ×2, Read a file ×4, Run exploratory Python ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 3 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 4 | 2 | 8 | 4 | Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 5 | 2 | 6 | 0 | Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 6 | 2 | 8 | 0 | Write draft.py ×3, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 7 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 8 | 2 | 6 | 0 | Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 9 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |

**Run 3**

| Gen | Eval calls | LLM calls | Sionna retrievals | Purpose breakdown |
|---|---|---|---|---|
| 0 | 1 | 19 | 7 | List workspace files ×2, Sionna doc retrieval ×5, Read a file ×1, Run exploratory Python ×6, Write draft.py ×1, Evaluate ×1, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 1 | 1 | 20 | 6 | List workspace files ×2, Sionna doc retrieval ×6, Read a file ×1, Run exploratory Python ×7, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 2 | 1 | 5 | 1 | Sionna doc retrieval ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 3 | 1 | 6 | 4 | Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 4 | 1 | 5 | 3 | Sionna doc retrieval ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 5 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 6 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 7 | 1 | 10 | 0 | List workspace files ×2, Read a file ×3, Run exploratory Python ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 8 | 1 | 7 | 2 | List workspace files ×1, Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 9 | 1 | 7 | 3 | List workspace files ×1, Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |

**Run 4**

| Gen | Eval calls | LLM calls | Sionna retrievals | Purpose breakdown |
|---|---|---|---|---|
| 0 | 2 | 21 | 6 | List workspace files ×1, Sionna doc retrieval ×6, Run exploratory Python ×9, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 1 | 1 | 7 | 1 | List workspace files ×1, Sionna doc retrieval ×1, Read a file ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 2 | 1 | 7 | 3 | Sionna doc retrieval ×3, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 3 | 1 | 9 | 5 | List workspace files ×1, Sionna doc retrieval ×4, Run exploratory Python ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 4 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 5 | 1 | 7 | 3 | Sionna doc retrieval ×3, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 6 | 1 | 12 | 2 | List workspace files ×2, Sionna doc retrieval ×2, Read a file ×3, Run exploratory Python ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 7 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 8 | 1 | 5 | 1 | Sionna doc retrieval ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 9 | 1 | 28 | 7 | List workspace files ×3, Sionna doc retrieval ×5, Read a file ×3, Run exploratory Python ×15, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |

**Run 5**

| Gen | Eval calls | LLM calls | Sionna retrievals | Purpose breakdown |
|---|---|---|---|---|
| 0 | 2 | 23 | 4 | List workspace files ×1, Sionna doc retrieval ×4, Run exploratory Python ×7, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×6, Save solution.py ×1, Final summary ×1 |
| 1 | 1 | 6 | 2 | List workspace files ×1, Sionna doc retrieval ×2, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 2 | 2 | 14 | 6 | List workspace files ×1, Sionna doc retrieval ×6, Run exploratory Python ×1, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 3 | 2 | 18 | 4 | List workspace files ×1, Sionna doc retrieval ×4, Run exploratory Python ×7, Write draft.py ×1, Evaluate ×2, Edit draft.py (fix) ×1, Save solution.py ×1, Final summary ×1 |
| 4 | 1 | 5 | 1 | Sionna doc retrieval ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 5 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 6 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 7 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 8 | 1 | 6 | 3 | List workspace files ×1, Sionna doc retrieval ×1, Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |
| 9 | 1 | 4 | 0 | Write draft.py ×1, Evaluate ×1, Save solution.py ×1, Final summary ×1 |

### EvoX / SkyDiscover — per iteration

*All 5 runs shown. Each run also makes 1 one-time LLM call before iteration 1 (write explore/refine guidance), not counted in the rows below.*

**Run 1**

| Iter | Eval calls | LLM calls | Purpose |
|---|---|---|---|
| 1 | 1 | 1 | Generate & evaluate candidate solution |
| 2 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 3 | 1 | 1 | Generate & evaluate candidate solution |
| 4 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 5 | 1 | 1 | Generate & evaluate candidate solution |
| 6 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 7 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 8 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 9 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 10 | 1 | 1 | Generate & evaluate candidate solution |

**Run 2**

| Iter | Eval calls | LLM calls | Purpose |
|---|---|---|---|
| 1 | 1 | 1 | Generate & evaluate candidate solution |
| 2 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 3 | 1 | 1 | Generate & evaluate candidate solution |
| 4 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 5 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 6 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 7 | 1 | 1 | Generate & evaluate candidate solution |
| 8 | 1 | 1 | Generate & evaluate candidate solution |
| 9 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 10 | 1 | 1 | Generate & evaluate candidate solution |

**Run 3**

| Iter | Eval calls | LLM calls | Purpose |
|---|---|---|---|
| 1 | 1 | 1 | Generate & evaluate candidate solution |
| 2 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 3 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 4 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 5 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 6 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 7 | 1 | 1 | Generate & evaluate candidate solution |
| 8 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 9 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 10 | 1 | 1 | Generate & evaluate candidate solution |

**Run 4**

| Iter | Eval calls | LLM calls | Purpose |
|---|---|---|---|
| 1 | 1 | 1 | Generate & evaluate candidate solution |
| 2 | 1 | 1 | Generate & evaluate candidate solution |
| 3 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 4 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 5 | 1 | 1 | Generate & evaluate candidate solution |
| 6 | 1 | 6 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy (2 attempts, 1 failed validation) |
| 7 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 8 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 9 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 10 | 1 | 1 | Generate & evaluate candidate solution |

**Run 5**

| Iter | Eval calls | LLM calls | Purpose |
|---|---|---|---|
| 1 | 1 | 1 | Generate & evaluate candidate solution |
| 2 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 3 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 4 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 5 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 6 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 7 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 8 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 9 | 1 | 5 | Generate & evaluate candidate solution; Stagnation → summarize population/problem/strategies (×3) + write new strategy |
| 10 | 1 | 1 | Generate & evaluate candidate solution |
