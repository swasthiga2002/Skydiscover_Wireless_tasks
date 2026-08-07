---
layout: page
title: Architecture
permalink: /architecture/
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
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="current">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a>
</div>

# Architecture

This page describes how SkyDiscover's **EvoX** search algorithm works: the same generic solution loop is shared by every search algorithm SkyDiscover supports, but EvoX adds a second, outer loop that evolves the search strategy itself.

## Two-Level Co-Evolution

EvoX runs two nested evolutionary processes at once:

- An **inner loop** that evolves candidate *solutions* to the target problem (e.g. a channel estimator), using whatever sampling/selection logic is currently installed in the program database.
- An **outer loop** that evolves the *search strategy itself* (the Python code deciding how solutions are sampled and combined) whenever progress on the inner loop stalls.

Solutions evolve inside the current database's logic, while that logic evolves across "switches." This is the literal meaning of co-evolution: both levels adapt, and each shapes what the other can discover next.

## The Solution Loop

Every iteration follows the same generic cycle, reused unchanged by every search algorithm in SkyDiscover: **sample a parent (and context programs) → build a prompt → the LLM generates a candidate → evaluate it → add it back to the database.** For EvoX, the database driving `sample()` starts as a default evolved-program database and is replaced over the course of a run by the meta-evolution process described below.

## Meta-Evolution of the Search Strategy

When the best score stagnates (improvement below a small threshold) for a run of iterations (by default about 10% of the total iteration budget), EvoX triggers a strategy switch:

1. It scores the just-used search algorithm based on how much improvement it achieved, weighted by how long it had to work.
2. It asks an LLM to generate an entirely new database class implementing the sampling/selection logic, effectively a new search algorithm written in Python.
3. The new database is validated before being trusted.
4. All existing solution programs and their prompt history are migrated into the new database, which is hot-swapped in as the active search strategy.

If the newly generated database throws an error at runtime, EvoX falls back to the previous database and keeps any new solutions found in the meantime. The database of past search-strategy attempts is itself evolved across switches, so the meta-evolution process learns from which strategies worked.

## Prompt Context

Each iteration's prompt is assembled from several pieces:

- **Metrics & focus areas**: the parent's current score, a per-metric breakdown, and heuristics about whether the score is trending up or down.
- **Previous attempts**: a handful of recent programs with what changed, their metrics, and whether each was an improvement, a regression, or a no-op.
- **Other context programs**: other strong/elite programs from the database, shown with their metrics and full code, plus recent failed attempts (with the LLM's response or a traceback) so the model can avoid repeating mistakes.
- **Current program**: the parent's code, its score breakdown, and any evaluator feedback it returned.
- **Explore/exploit label**: a per-iteration "explore" or "exploit" tag attached to the parent program, chosen by whatever sampling code is currently installed (there's no single global knob), typically based on how long the run has been stagnating.
- **Task/response-format instructions**: whether to reply with a diff, a full rewrite, or a from-scratch solution.

At the meta-evolution level, EvoX additionally injects a summary of the population's current state and a batch summary of prior search strategies and how well they scored, so the LLM proposing new search strategies can see what's already been tried.

## LLM Calls

EvoX makes several distinct kinds of LLM calls:

| # | LLM call | Fires when | Output |
|---|---|---|---|
| 1 | Generate a candidate solution | Every solution iteration | New candidate program (code) |
| 2 | Summarize population / problem / past strategies (3 parallel calls) | Every time the meta-evolution level builds a prompt | Summarized text, folded into the prompt for call 3 |
| 3 | Write a new search strategy | Only when solution progress stalls | A full new `EvolvedProgramDatabase` Python file |
| 4 | Write explore/refine guidance | Once, before iteration 1 | Diverge/refine guidance text |
| 5 *(optional)* | LLM-as-judge | Every evaluation, only if enabled | A judged score |
