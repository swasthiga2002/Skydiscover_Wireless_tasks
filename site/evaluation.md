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
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="current">Evaluation</a>
</div>

# Evaluation

Each candidate channel estimator is evaluated by plugging it into a fixed downstream receiver pipeline and running a Monte Carlo block-error-rate (BLER) simulation: at each SNR test point, many random draws of channel realizations, noise, and transmitted bits are simulated until enough block errors have been observed to give a statistically stable BLER estimate. The same simulation is also run with perfect channel state information (CSI) as a baseline, and the candidate's BLER is divided by the perfect-CSI BLER at each SNR point to get a per-point normalized error. That ratio, averaged across SNR points, is the NVE reported throughout this site; this page instead covers how many times each framework calls that evaluation tool, and how many LLM calls it spends getting there.

## Summary

| | AI Telco Engineer (50 generations) | EvoX / SkyDiscover (50 iterations, 5 runs) |
|---|---|---|
| Evaluation calls per iteration | 1-3 (avg 1.2) | always 1 |
| LLM calls per iteration | 4-28 (avg 8.8) | 1-6 (avg 3.6) |
| Sionna doc retrievals per iteration | 0-7 (avg 2.1) | 0 (context is pre-assembled into the prompt, no retrieval tool) |

- **Evaluation grid density differs between frameworks.** SkyDiscover's NVE is averaged over 7 SNR points (-9 to -2 dB, 1 dB step); AI Telco Engineer averages over 4 (-9 to -2 dB, 2 dB step) -- see [Quantitative](/quantitative/) for how this affects the reported best-NVE comparison.

## Eval Retry Loop

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
      <div class="ed-box llm"><span class="ed-tag">LLM call</span>Generate a candidate solution: exactly 1 call, everything needed is already in the prompt</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Evaluate the candidate</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Success?</div>
      <div class="ed-branch">Yes → add to database, iteration done<br>No → append the exact error, retry (up to 3 total)</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box store"><span class="ed-tag">Storage</span>All 3 fail? Discard: no candidate added this iteration</div>
    </div>
  </div>
  <div>
    <p class="ed-col-title">AI Telco Engineer</p>
    <div class="ed-flow">
      <div class="ed-box llm"><span class="ed-tag">LLM call(s)</span>Research + write draft.py, an open-ended agentic loop: docs lookup, file reads, exploratory code, as many LLM turns as it wants</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Evaluate draft.py</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box"><span class="ed-tag">Logic</span>Success?</div>
      <div class="ed-branch">Yes → copy draft.py → solution.py, stop<br>No → fix draft.py using the exact error, retry (up to 3 total)</div>
      <div class="ed-arrow">▼</div>
      <div class="ed-box store"><span class="ed-tag">Storage</span>All 3 fail? Leave solution.py unset: post-run eval scores draft.py as-is</div>
    </div>
  </div>
</div>

</div>


## Full Data

<div class="calls-table">
<style>
  .calls-table {
    --ct-ink: #1e2b3c; --ct-ink-soft: #5b6b80; --ct-panel: #ffffff; --ct-line: #d3dce6; --ct-bg: #f6f8fb;
    margin: 20px 0 28px; font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; font-size: 13.5px;
  }
  @media (prefers-color-scheme: dark) {
    .calls-table { --ct-ink: #e7edf5; --ct-ink-soft: #9db0c4; --ct-panel: #141f2d; --ct-line: #263344; --ct-bg: #0e1620; }
  }
  .calls-table table { width: 100%; border-collapse: collapse; }
  .calls-table th, .calls-table td { border: 1px solid var(--ct-line); padding: 8px 12px; text-align: center; }
  .calls-table thead tr:first-child th { background: var(--ct-bg); font-size: 15px; font-weight: 700; color: var(--ct-ink); }
  .calls-table thead tr:last-child th { color: var(--ct-ink-soft); font-weight: 600; font-size: 12.5px; }
  .calls-table tbody td { color: var(--ct-ink); }
  .calls-table tbody th { color: var(--ct-ink); text-align: left; }
</style>
<table>
  <thead>
    <tr>
      <th rowspan="2">Run</th>
      <th colspan="3">AI Telco Engineer</th>
      <th colspan="2">EvoX / SkyDiscover</th>
    </tr>
    <tr>
      <th>Eval calls</th>
      <th>LLM calls</th>
      <th>Sionna retrievals</th>
      <th>Eval calls</th>
      <th>LLM calls</th>
    </tr>
  </thead>
  <tbody>
    <tr><th>1</th><td>12</td><td>79</td><td>17</td><td>10</td><td>34</td></tr>
    <tr><th>2</th><td>15</td><td>80</td><td>16</td><td>10</td><td>30</td></tr>
    <tr><th>3</th><td>10</td><td>87</td><td>26</td><td>10</td><td>38</td></tr>
    <tr><th>4</th><td>11</td><td>104</td><td>28</td><td>10</td><td>35</td></tr>
    <tr><th>5</th><td>13</td><td>88</td><td>20</td><td>10</td><td>42</td></tr>
  </tbody>
</table>
</div>
