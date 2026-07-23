---
layout: page
title: Getting Started
permalink: /getting-started/
---

# Getting Started

## Installation

SkyDiscover requires **Python >= 3.10** (channel-estimation specifically needs Python >= 3.11, since it depends on Sionna 2.x) and is installed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
export OPENAI_API_KEY="<your-key>"
```

The base install has no ML/simulation dependencies. Benchmarks that need extra packages are opt-in via extras:

```bash
uv sync --extra math                 # math benchmarks (SciPy, JAX, PyWavelets, ...)
uv sync --extra external             # OpenEvolve / GEPA / ShinkaEvolve backends
uv sync --extra channel-estimation   # MIMO channel estimation (Sionna; needs Python >=3.11)
```

Extras can be combined, e.g. `uv sync --extra external --extra math`. API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.) are picked up automatically from the environment or a repo-root `.env` file.

## Running a Discovery

The console entrypoint is `skydiscover-run`:

```bash
uv run skydiscover-run [INITIAL_PROGRAM] EVALUATOR [options]
```

`INITIAL_PROGRAM` is optional — omit it to let the LLM generate a solution from scratch. `EVALUATOR` can be a plain Python file with an `evaluate(program_path)` function, a directory with a `Dockerfile` + `evaluate.sh` for containerized evaluation, or a [Harbor](https://harborframework.com/)-format task directory.

```bash
# Circle-packing math benchmark, using EvoX
uv run skydiscover-run benchmarks/math/circle_packing/initial_program.py \
  benchmarks/math/circle_packing/evaluator.py \
  --config benchmarks/math/circle_packing/config.yaml \
  --search evox \
  --iterations 100
```

Key flags: `-c/--config` (YAML config), `-i/--iterations`, `-m/--model` (any [LiteLLM](https://docs.litellm.ai/)-compatible model, e.g. `gpt-5`, `anthropic/claude-sonnet-4-6`), `-s/--search` (`evox`, `adaevolve`, `topk`, `beam_search`, `best_of_n`, `openevolve_native`, `gepa_native`, and external backends), `-o/--output`, `--agentic` (lets the LLM read repo files), and `--checkpoint` (see below). There's also a Python API — `skydiscover.run_discovery(...)` and the `discover_solution(...)` convenience wrapper for inline strings and callables.

## Config Overview

Pass a YAML config with `-c`. The major sections:

```yaml
max_iterations: 100
checkpoint_interval: 10

llm:
  models: [{ name: "gpt-5.4", weight: 1.0 }]   # weighted pool for solution generation
  # evaluator_models / guide_models default to `models` if unset

search:
  type: "evox"              # or "adaevolve", "topk", "beam_search", "best_of_n", ...
  num_context_programs: 4    # example programs shown to the LLM each iteration
  switch_interval: null      # EvoX: iterations of stagnation before a strategy switch

evaluator:
  timeout: 1200
  max_retries: 3

prompt:
  system_message: |
    <problem-specific instructions for the LLM>

monitor:
  enabled: true              # live dashboard, prints its URL at run start
```

There is no `initial_program_path` config field — the starting program is always passed as a CLI positional argument (or API parameter), not a config key. See [configs/](https://github.com/swasthiga2002/Skydiscover_Wireless_tasks/tree/main/configs) for full annotated templates.

## Resuming from a Checkpoint

Every run writes a checkpoint every `checkpoint_interval` iterations (and at the end of the run) to `checkpoints/checkpoint_<iteration>/`, containing the full program database plus a `best_program` file and its metrics. To resume:

```bash
uv run skydiscover-run initial_program.py evaluator.py \
  --checkpoint /path/to/checkpoints/checkpoint_50
```

The run restores the saved database and continues from the iteration after the checkpoint. There's no config-file equivalent for this — it's CLI/API-only. To replay a completed run visually instead of resuming it, use `uv run skydiscover-viewer /path/to/checkpoints/checkpoint_100`.
