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
<a href="{{ '/' | relative_url }}" class="current">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a>
</div>

## Objective

Recently, Aoudia et al. [\[1\]](#ref-1) introduced the AI Telco Engineer, an agentic framework that autonomously discovers solutions to an OFDM channel estimation problem. Inspired by that work, we explore whether more recent LLMs and a newer agentic search algorithm (EvoX [\[2\]](#ref-2), which evolves its own search strategy via LLMs as the run progresses, run here inside the SkyDiscover framework [\[3\]](#ref-3)) can produce better solutions to the OFDM channel estimation problem considered in [\[1\]](#ref-1), under matched settings on the same benchmark.

## Findings

With GPT-5.5 and EvoX, the Normalized Validation Error (NVE) improved from the approximately 30 reported in [\[1\]](#ref-1) to 9.98*. Running AI Telco Engineer with GPT-5.5 improved the NVE to 14.70.

\* This value was reproduced using the 4-point SNR method, as used by AI Telco Engineer. Since NVE is a Monte Carlo estimate, this was measured across 10 reseeded evaluations; the average was 11.77.

See [Quantitative](/quantitative/) for the head-to-head numbers and [Qualitative](/qualitative/) for the actual algorithms.

## SkyDiscover

SkyDiscover [\[3\]](#ref-3) is a modular framework for AI-driven algorithmic discovery: you supply a scoring function and, optionally, a starting program, and an LLM iteratively proposes, evaluates, and refines candidate solutions until the iteration budget runs out. It provides a unified interface across 200+ optimization benchmarks and multiple pluggable search algorithms, including AdaEvolve, EvoX, OpenEvolve, GEPA, and ShinkaEvolve. Every run checkpoints its full program database, supporting resume-from-checkpoint and replay in a live monitor dashboard.

## AI Telco Engineer

AI Telco Engineer deploys a swarm of parallel LLM agents, each in its own isolated containerized workspace, to autonomously design and optimize wireless algorithms such as channel estimation. It runs an idea-driven loop: an orchestrator LLM proposes N distinct algorithmic ideas each generation, distributes M agents across those ideas, then reviews all summaries and metrics to propose new ideas for the next generation. Progress is tracked on a live leaderboard, but there's no seed-injection or checkpoint-resume mechanism: every generation-0 idea comes fresh from the orchestrator with no fixed starting point.

## EvoX Algorithm

EvoX [\[2\]](#ref-2) is a self-evolving search algorithm, run here as one of the pluggable search algorithms supported by SkyDiscover [\[3\]](#ref-3): it runs two nested loops, an inner loop that evolves candidate channel estimators, and an outer loop that rewrites the sampling/selection strategy itself whenever progress stalls. Roughly every 10% of the iteration budget without improvement, EvoX scores the current search strategy, has an LLM author a brand-new one, validates it, and migrates the whole population into it (see [Architecture](/architecture/) for the full mechanism). Because the strategy adapts to what's actually working on this specific task, we expect EvoX to reach lower NVE more reliably than AI Telco Engineer's fixed loop, and the [Quantitative](/quantitative/) page bears this out: lowest NVE of 9.98* for EvoX vs. 14.70 for AI Telco Engineer.

## References

<span id="ref-1"></span>[1] F. A. Aoudia, J. Hoydis, S. Cammerer, L. Maggi, G. Marti, and A. Keller, "The AI Telco Engineer: Toward Autonomous Discovery of Wireless Communications Algorithms," *arXiv preprint* arXiv:2604.19803, 2026. [arXiv:2604.19803](https://arxiv.org/abs/2604.19803)

<span id="ref-2"></span>[2] S. Liu, S. Agarwal, M. Maheswaran, M. Cemri, Z. Li, Q. Mang, A. Naren, E. Boneh, A. Cheng, M. Z. Pan, et al., "EvoX: Meta-Evolution for Automated Discovery," *arXiv preprint* arXiv:2602.23413, 2026. [arXiv:2602.23413](https://arxiv.org/abs/2602.23413)

<span id="ref-3"></span>[3] S. Liu, M. Cemri, S. Agarwal, A. Krentsel, A. Naren, Q. Mang, Z. Li, A. Gupta, M. Maheswaran, A. Cheng, et al., "SkyDiscover: A Flexible, Adaptive Framework for AI-Driven Scientific and Algorithmic Discovery," in *Proceedings of the ACM Conference on AI and Agentic Systems*, 2026, pp. 1223–1227.

## Authors

Dr. Krishna Narayanan and Swasthiga Rengasamy (MS student, Electrical Engineering)

Texas A&M University, Department of Electrical and Computer Engineering, Information Science and Learning Systems group
