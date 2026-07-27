---
layout: page
title: Home
permalink: /
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
<a href="{{ '/' | relative_url }}" class="current">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/results/' | relative_url }}" class="">Results</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a><span class="sep">/</span><a href="{{ '/getting-started/' | relative_url }}" class="">Getting Started</a>
</div>

# Channel Estimation Task

## Objective

Determine whether SkyDiscover's EvoX — which evolves its own search strategy via LLMs as the run progresses — converges to better MIMO-OFDM channel estimators than AI Telco Engineer's fixed idea-driven multi-agent search, under matched settings on the same benchmark.
Hypothesis: EvoX wins on Normalized Validation Error (NVE) — see [Results](/results/) for the head-to-head numbers.

## SkyDiscover

SkyDiscover is a modular framework for AI-driven algorithmic discovery: you supply a scoring function and, optionally, a starting program, and an LLM iteratively proposes, evaluates, and refines candidate solutions until the iteration budget runs out. It provides a unified interface across 200+ optimization benchmarks and multiple pluggable search algorithms, including its own AdaEvolve and EvoX as well as OpenEvolve, GEPA, and ShinkaEvolve. Every run checkpoints its full program database, supporting resume-from-checkpoint and replay in a live monitor dashboard.

## AI Telco Engineer

AI Telco Engineer deploys a swarm of parallel LLM agents, each in its own isolated containerized workspace, to autonomously design and optimize wireless algorithms such as channel estimation. It runs an idea-driven loop: an orchestrator LLM proposes N distinct algorithmic ideas each generation, distributes M agents across those ideas, then reviews all summaries and metrics to propose new ideas for the next generation. Progress is tracked on a live leaderboard, but there's no seed-injection or checkpoint-resume mechanism — every generation-0 idea comes fresh from the orchestrator with no fixed starting point.

## EvoX Algorithm

EvoX is SkyDiscover's self-evolving search algorithm: it runs two nested loops — an inner loop that evolves candidate channel estimators, and an outer loop that rewrites the sampling/selection strategy itself whenever progress stalls. Roughly every 10% of the iteration budget without improvement, EvoX scores the current search strategy, has an LLM author a brand-new one, validates it, and migrates the whole population into it — see [Architecture](/architecture/) for the full mechanism. Because the strategy adapts to what's actually working on this specific task, we expect EvoX to reach lower NVE more reliably than AI Telco Engineer's fixed loop, and the [Results](/results/) page bears this out: lowest NVE of 9.98 for EvoX vs. 23.31 for AI Telco Engineer.

## Quick Links

- [Architecture](/architecture/)
- [Results](/results/)
- [Evaluation](/evaluation/)
- [Getting Started](/getting-started/)
- [GitHub repo](https://github.com/swasthiga2002/Skydiscover_Wireless_tasks)
