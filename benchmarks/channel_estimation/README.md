# MIMO Channel Estimation

Evolve the **channel estimator** of a 4×16 MIMO OFDM uplink detector built with
[Sionna](https://nvlabs.github.io/sionna/) (3GPP UMi channel, 5G NR LDPC, QPSK).
Only the code inside the `EVOLVE-BLOCK` markers is changed — the LMMSE equalizer
and APP demapper are fixed. Ported from `the-ai-telco-engineer`.

## Quick Start

```bash
uv run skydiscover-run \
  benchmarks/channel_estimation/initial_program.py \
  benchmarks/channel_estimation/evaluator.py \
  -c benchmarks/channel_estimation/config.yaml \
  --search evox --iterations 100
```

## Setup

### 1. Install the extra (requires Python ≥ 3.11)

```bash
uv sync --extra channel-estimation
```

This pulls `sionna` (and PyTorch). Sionna 2.x requires Python ≥ 3.11; the
dependency is gated with a marker (`sionna>=2.0.0; python_version >= '3.11'`) so
resolution still succeeds on the project's 3.10 split.

### 2. API key

The run uses the LLM configured under `llm:` in
[`config.yaml`](config.yaml). If no `api_key` is set there, the framework falls
back to the **`OPENAI_API_KEY`** environment variable. To use a different key for
this benchmark only, set `api_key` in the config — it supports `${VAR}`
expansion, so you can point it at any environment variable:

```yaml
llm:
  api_base: "https://api.openai.com/v1"
  api_key: "${MY_PROJECT_OPENAI_KEY}"   # ${VAR} is expanded from the environment
  models:
    - name: "gpt-5.5"
      weight: 1.0
      api_key: "${MY_PROJECT_OPENAI_KEY}"   # set it on the model too (see note)
```

> **Note:** set the key on the **model entry**, not just the top-level `llm.api_key`.
> Per-model env resolution runs first, so a top-level-only key is overridden by the
> `OPENAI_API_KEY` fallback.

### 3. GPU (strongly recommended)

Each evaluation runs a full Monte-Carlo BLER simulation. On CPU this takes
~10–20 min per candidate; on a GPU it is several times faster. Sionna
automatically targets `cuda:0` when CUDA is available — no code change needed.

The default PyTorch wheel on Windows is **CPU-only**, so install a CUDA build
explicitly into your environment:

```bash
# Pick the build matching your driver (cu128 = CUDA 12.8). `auto` detects the GPU.
uv pip install torch --torch-backend=cu128     # or --torch-backend=auto
```

Verify:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
# e.g. 2.11.0+cu128 True
```

> Laptop GPUs with limited VRAM (e.g. 4 GB) can run the default `BATCH_SIZE=10`,
> but lower it in [`evaluator.py`](evaluator.py) if you hit out-of-memory.

## Scoring

The objective is the **Normalized Validation Error (NVE)** — the mean ratio of
the candidate's BLER to the perfect-CSI BLER across SNRs:

```
NVE            = mean over SNR of  BLER_candidate / BLER_perfect-CSI
combined_score = 1.0 / NVE          # higher is better; failures -> 0.0
```

The LS baseline scores `NVE ≈ 94` (`combined_score ≈ 0.011`); a good estimator
should do substantially better. Don't just replicate Sionna's built-in LS/LMMSE
estimators — improve interpolation across time/frequency, denoise (DFT/subspace),
and exploit the pilot structure and noise statistics.

## Files

```
channel_estimation/
├── initial_program.py   # starting estimator (the EVOLVE-BLOCK target)
├── evaluator.py         # MIMO sim + NVE scoring (mimo_detector -> combined_score)
├── config.yaml          # LLM + search + prompt config
├── link_config.py       # system params (RG, SM, antenna counts, ...) — import, never hardcode
├── bler_perfect_csi.py  # generates the perfect-CSI BLER baseline
└── bler_perf_csi.pkl    # cached perfect-CSI BLER reference
```

## Windows + cloud-synced folders (Dropbox / OneDrive)

If the repo lives inside a cloud-synced folder (Dropbox, OneDrive), the sync
client fights `uv` over the virtualenv. Symptoms and fixes:

| Symptom | Cause | Fix |
|---|---|---|
| `failed to hardlink ... (os error 396)` | cloud-filtered files can't be hardlinked | `UV_LINK_MODE=copy` |
| `failed to remove ... being used by another process` mid-install | sync client / Defender scanning new files | `UV_LINK_MODE=copy`; retry; mark the venv cloud-ignored |
| Slow installs, repeated locks | gigabytes of venv churn being synced | **put the venv outside the synced folder** (below) |

**Recommended:** keep the virtualenv out of the synced folder entirely via
`UV_PROJECT_ENVIRONMENT` (set these as persistent per-machine environment
variables — on Windows, `setx NAME value`, then open a new terminal):

| Variable | Example value | Purpose |
|---|---|---|
| `UV_PROJECT_ENVIRONMENT` | `C:\Users\<you>\.venvs\skydiscover` | venv outside the synced folder |
| `UV_LINK_MODE` | `copy` | avoid cloud-sync hardlink errors |
| `UV_NO_SYNC` | `1` | stop `uv run` from auto-syncing (see note) |

> **Why `UV_NO_SYNC=1`?** The committed `uv.lock` pins the **CPU** torch wheel
> (so collaborators/CI stay CPU-default). A normal `uv run`/`uv sync` would
> re-install that CPU wheel and silently undo your local CUDA build.
> `UV_NO_SYNC=1` makes `uv run` use the environment as-is. After any intentional
> `uv sync` (e.g. when dependencies change), re-run the CUDA `uv pip install`
> from step 3 to restore the GPU build.

> **Deleting a venv in a cloud folder:** deeply-nested files (e.g. JupyterLab
> assets) can exceed Windows' 260-char path limit and defeat `Remove-Item`. Use
> the robocopy empty-mirror trick:
> `robocopy <empty_dir> <venv_dir> /MIR` then remove both directories.
