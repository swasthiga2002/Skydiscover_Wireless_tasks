---
layout: page
title: Home
permalink: /
---

# SkyDiscover

A flexible, adaptive framework for AI-driven scientific and algorithmic discovery.

## Key Features

- **Two adaptive search algorithms** — [AdaEvolve](https://arxiv.org/abs/2602.20133), which adjusts optimization parameters based on observed progress, and [EvoX](https://arxiv.org/abs/2602.23413), which evolves the search strategy itself using LLMs on the fly. See [Architecture](/architecture/) for how EvoX's two-level co-evolution works.
- **Three evaluator formats** — a plain Python `evaluate(program_path)` function, a Dockerized evaluator for custom dependencies, or a [Harbor](https://harborframework.com/)-format task, so existing benchmark suites (AlgoTune, LiveCodeBench, BigCodeBench, and more) work out of the box.
- **Optional starting solution** — mark a mutable region with `EVOLVE-BLOCK` markers, or omit the initial program entirely and let the LLM generate one from scratch.
- **Checkpointing & resuming** — every run periodically checkpoints its full program database and can be resumed from any checkpoint directory, or replayed in a live monitor dashboard.
- **Any LLM backend** — any [LiteLLM](https://docs.litellm.ai/)-compatible model, with weighted multi-model pools for solution generation and search-strategy meta-evolution.

## Quick Links

- [Architecture](/architecture/)
- [Results](/results/)
- [Getting Started](/getting-started/)
- [GitHub repo](https://github.com/swasthiga2002/Skydiscover_Wireless_tasks)
