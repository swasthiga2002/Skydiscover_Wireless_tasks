---
layout: page
title: Architecture
permalink: /architecture/
---

# Architecture

This page describes how SkyDiscover's **EvoX** search algorithm works — the same generic solution loop is shared by every search algorithm SkyDiscover supports, but EvoX adds a second, outer loop that evolves the search strategy itself.

## Two-Level Co-Evolution

EvoX runs two nested evolutionary processes at once:

- An **inner loop** that evolves candidate *solutions* to the target problem (e.g. a channel estimator), using whatever sampling/selection logic is currently installed in the program database.
- An **outer loop** that evolves the *search strategy itself* — the Python code deciding how solutions are sampled and combined — whenever progress on the inner loop stalls.

Solutions evolve inside the current database's logic, while that logic evolves across "switches." This is the literal meaning of co-evolution: both levels adapt, and each shapes what the other can discover next.

## The Solution Loop

Every iteration follows the same generic cycle, reused unchanged by every search algorithm in SkyDiscover: **sample a parent (and context programs) → build a prompt → the LLM generates a candidate → evaluate it → add it back to the database.** For EvoX, the database driving `sample()` starts as a default evolved-program database and is replaced over the course of a run by the meta-evolution process described below.

## Meta-Evolution of the Search Strategy

When the best score stagnates (improvement below a small threshold) for a run of iterations — by default about 10% of the total iteration budget — EvoX triggers a strategy switch:

1. It scores the just-used search algorithm based on how much improvement it achieved, weighted by how long it had to work.
2. It asks an LLM to generate an entirely new database class implementing the sampling/selection logic — effectively a new search algorithm, written in Python.
3. The new database is validated before being trusted.
4. All existing solution programs and their prompt history are migrated into the new database, which is hot-swapped in as the active search strategy.

If the newly generated database throws an error at runtime, EvoX falls back to the previous database and keeps any new solutions found in the meantime. The database of past search-strategy attempts is itself evolved across switches, so the meta-evolution process learns from which strategies worked.

## Explore vs Exploit

There's no single global explore/exploit knob — the tradeoff is decided *inside whatever sampling code the LLM currently has installed*. At the start of a run, EvoX generates two problem-specific labels — one for "explore" (try a fundamentally different approach) and one for "exploit" (refine within the current approach) — and it's up to each generated database's `sample()` method to decide, per iteration, which label to attach to the parent it selects (typically based on how long the run has been stagnating). That label then surfaces directly in the next prompt as guidance attached to the current solution.

## Prompt Context

Each iteration's prompt is assembled from several pieces:

- **Metrics & focus areas** — the parent's current score, a per-metric breakdown, and heuristics about whether the score is trending up or down.
- **Previous attempts** — a handful of recent programs with what changed, their metrics, and whether each was an improvement, a regression, or a no-op.
- **Other context programs** — other strong/elite programs from the database, shown with their metrics and full code, plus recent failed attempts (with the LLM's response or a traceback) so the model can avoid repeating mistakes.
- **Current program** — the parent's code, its score breakdown, and any evaluator feedback (`artifacts`) it returned.
- **Task/response-format instructions** — whether to reply with a diff, a full rewrite, or a from-scratch solution.

At the meta-evolution level, EvoX additionally injects a summary of the population's current state and a batch summary of prior search strategies and how well they scored, so the LLM proposing new search strategies can see what's already been tried.

## Checkpointing & Resuming

Every run periodically checkpoints the full program database — all candidate programs, their prompt history, and the current best program — to a `checkpoints/checkpoint_<iteration>/` directory, alongside a `best_program` file and `best_program_info.json` with its metrics. Checkpointing happens on a configurable interval and always at the end of a run.

Resuming is CLI/API-only (there's no config-file equivalent): pass `--checkpoint <path>` to `skydiscover-run`, and the run restores the database and continues from the next iteration after the checkpoint. Completed runs can also be replayed visually with `skydiscover-viewer /path/to/checkpoints/checkpoint_100`.
