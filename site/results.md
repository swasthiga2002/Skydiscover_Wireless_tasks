---
layout: page
title: Results
permalink: /results/
---

# Results

**Head-to-head comparison: AI Telco Engineer vs. EvoX/SkyDiscover on the same channel-estimation benchmark, under matched settings (same physical-layer config, same single-job/single-idea/single-worker mode, same model family, same 10-generation/iteration budget).**

## Channel-Estimation Benchmark

Both frameworks target the same task: implement `mimo_detector(y, no)` for a 4×16 MIMO OFDM uplink (3GPP UMi channel, 5G NR LDPC, QPSK), minimizing the **Normalized Validation Error**:

```
NVE = mean over SNR points of  BLER_candidate / BLER_perfect-CSI
```

Lower is better. Only the channel-estimation stage is mutable — the LMMSE equalizer and APP demapper are fixed scaffold in both frameworks. Physical-layer parameters (antenna counts, FFT size, subcarrier spacing, carrier frequency, batch size, Monte-Carlo iterations) are identical between the two setups — SkyDiscover's evaluator was explicitly built to match the AI Telco Engineer task. One methodology difference remains: SkyDiscover averages NVE over 7 SNR points (-9 to -2 dB, 1 dB step); AI Telco Engineer averages over 4 (-9 to -2 dB, 2 dB step).

## Run Summary

| Framework | Runs compared | Model | Median best NVE | Range |
|---|---|---|---|---|
| **EvoX / SkyDiscover** | `evox_testrun1`–`4` | gpt-5.5 (solution) + gpt-5 / gpt-5-mini (search-strategy meta-evolution) | **16.6** | 9.98 – 19.94 |
| **AI Telco Engineer** | `workspace6_testrun1`–`5` | gpt-5.5 (agent + manager)* | **47.78** | 23.31 – 78.68 |

\* model not independently confirmed from logs for the AI Telco Engineer runs (no per-run model trace found), inferred from the project's other same-week runs.

`evox_testrun5` is excluded pending a clean re-run (its folder was reused across two independent invocations, so its current on-disk best doesn't reliably represent a single run — see Methodology Notes below).

### Best NVE per run

| Run # | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| 1 | 13.22 | 78.68 |
| 2 | 11.86 | 28.12 |
| 3 | 19.94 | 74.91 |
| 4 | 9.98 | 47.78 |
| 5 | *pending re-run* | 23.31 |
| **Median** | **16.6** | **47.78** |
| **Best** | **9.98** | **23.31** |
| **Worst** | **19.94** | **78.68** |

### NVE per generation — AI Telco Engineer

![AI Telco Engineer: NVE per generation, 5 runs](/assets/images/ai_telco_nve_per_generation.png)

Generation 0 is **not** a fixed baseline — AI Telco Engineer has no seed-injection mechanism, so gen0 is always the manager LLM's own first idea, which varies wildly run to run (from 34 to 6912+ NVE). Gaps in the lines are generations that failed outright (`NVE = inf`) — every one of the 5 runs hit at least one hard failure.

| Gen | testrun1 | testrun2 | testrun3 | testrun4 | testrun5 |
|---|---|---|---|---|---|
| 0 | — | 34.49 | 6912.60 | 64.62 | 481.13 |
| 1 | 242.44 | 34.74 | 87.40 | 62.37 | 60.83 |
| 2 | 78.68 | 39.77 | 76.42 | 2420.44 | 9291.07 |
| 3 | 78.68 | — | 74.91 | 58.51 | — |
| 4 | 9291.07 | — | — | — | 60.35 |
| 5 | 87.48 | — | — | 49.53 | 23.83 |
| 6 | 78.68 | — | 74.91 | 47.85 | 23.99 |
| 7 | 78.68 | 29.88 | 74.91 | — | 23.31 |
| 8 | 82.15 | 28.12 | 79.57 | 47.78 | 23.31 |
| 9 | 78.73 | 29.00 | 74.91 | — | 23.31 |

*— = generation failed (`NVE = inf`)*

### NVE per iteration — EvoX / SkyDiscover

![EvoX/SkyDiscover: NVE per iteration, 4 runs](/assets/images/evox_nve_per_iteration.png)

Iteration 0 **is** a fixed baseline — the literal LS-only seed program, executed verbatim every run, always scoring NVE = 101.69. All four runs converge from the same starting point, which is what makes them directly comparable. (`testrun5` will be added once its clean re-run completes.)

| Iter | testrun1 | testrun2 | testrun3 | testrun4 | testrun5 |
|---|---|---|---|---|---|
| 0 | 101.69 | 101.69 | 101.69 | 101.69 | *pending* |
| 1 | 58.46 | 222.85 | 69.44 | 45.36 | *pending* |
| 2 | 57.82 | 104.62 | 80.99 | 17.07 | *pending* |
| 3 | 19.70 | 28.79 | 56.32 | 23.22 | *pending* |
| 4 | 20.74 | 27.04 | 145.32 | 17.31 | *pending* |
| 5 | 13.49 | 29.22 | 58.20 | 9.99 | *pending* |
| 6 | 16.56 | 27.95 | 56.20 | 10.51 | *pending* |
| 7 | 13.22 | 18.74 | 21.68 | 10.33 | *pending* |
| 8 | 22.22 | 12.18 | 19.94 | 11.11 | *pending* |
| 9 | 16.39 | 11.86 | 21.47 | 10.33 | *pending* |
| 10 | 17.30 | 14.14 | 20.98 | 10.58 | *pending* |

## Best Algorithm — Side by Side

| | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| Run | `evox_testrun4`, iteration 5 | `workspace6_testrun5`, gen07 |
| NVE | **9.985** | 23.3115 |
| Approach | LS seed → delay-domain Wiener PDP shrinkage → RX-antenna spatial covariance eigenshrinkage → 5-tap time smoothing → residual-based error-variance calibration | LS seed → two parallel denoising branches (fixed-taper vs. PDP-adaptive-window Wiener filters) → 5 hand-tuned hyperparameter variants → pilot-residual cross-validation selects the best variant per call → pilot-consistency blending → error-variance calibration |
| Code size | ~55 lines | ~250 lines |

Notably, the more complex solution did *not* win — AI Telco Engineer's best program builds and cross-validates 5 candidate estimators per call, while SkyDiscover's best program is a single, direct pipeline with no runtime branching, and still scores less than half the NVE.

<details>
<summary><strong>SkyDiscover best (evox_testrun4, iteration 5) — click to expand</strong></summary>

```python
from sionna.phy.ofdm import LSChannelEstimator, LMMSEEqualizer
from sionna.phy.mapping import Demapper
from link_config import RG, SM, NUM_BITS_PER_SYMBOL

_lmmse_equ = LMMSEEqualizer(RG, SM)
_demapper = Demapper("app", "qam", NUM_BITS_PER_SYMBOL)

import torch

_ls_est = LSChannelEstimator(RG, interpolation_type="lin_time_avg")


def estimate_channel(y, no):
    """LS seed with delay-domain Wiener denoising, RX-spatial eigenshrinkage, and time smoothing."""
    h0, e0 = _ls_est(y, no)
    f = h0.shape[-1]
    t = h0.shape[-2]
    ra = h0.shape[2]

    taps = torch.fft.ifft(h0, dim=-1)
    p = taps.abs().square().mean(dim=(1, 2, 4, 5), keepdim=True)
    nv = e0.mean(dim=(1, 2, 4, 5, 6), keepdim=True) / f
    g = (p - nv).clamp_min(0.0) / (p + 1e-9)

    l = max(4, f // 6)
    m = (torch.arange(f, device=h0.device) < l).to(h0.real.dtype)
    m = m.reshape((1,) * (h0.ndim - 1) + (f,))
    gd = g * m
    hd = torch.fft.fft(taps * gd.to(h0.dtype), dim=-1)

    n = t * f
    mat = hd.permute(0, 1, 3, 4, 2, 5, 6).contiguous().reshape(-1, ra, n)
    cov = (mat @ mat.conj().transpose(-2, -1)) / float(n)
    lam, u = torch.linalg.eigh(cov)

    em = e0.permute(0, 1, 3, 4, 2, 5, 6).contiguous().reshape(-1, ra, n).mean(dim=(-2, -1))
    sig = 0.20 * em.unsqueeze(-1)
    sw = (lam - sig).clamp_min(0.0) / (lam + 1e-9)

    c = u.conj().transpose(-2, -1) @ mat
    mw = u @ (c * sw.unsqueeze(-1).to(h0.dtype))

    q = em / (mat.abs().square().mean(dim=(-2, -1)) + 1e-9)
    a = (2.0 * q).clamp(0.15, 0.75).reshape(-1, 1, 1).to(h0.dtype)
    mat = mat + a * (mw - mat)

    hs = mat.reshape(h0.shape[0], h0.shape[1], h0.shape[3], h0.shape[4], ra, t, f)
    hs = hs.permute(0, 1, 4, 2, 3, 5, 6).contiguous()

    hp = torch.cat([hs[..., :1, :], hs[..., :1, :], hs, hs[..., -1:, :], hs[..., -1:, :]], dim=-2)
    ht = (hp[..., :-4, :] + 4.0 * hp[..., 1:-3, :] + 6.0 * hp[..., 2:-2, :]
          + 4.0 * hp[..., 3:-1, :] + hp[..., 4:, :]) / 16.0
    h = 0.10 * h0 + 0.90 * ht

    red = (gd * gd).mean(dim=-1, keepdim=True)
    leak = (h0 - h).abs().square().real
    e = e0 * (0.10 + 0.90 * red) + 0.025 * leak + 1e-7
    return h.to(torch.complex64), e.to(torch.float32)


def mimo_detector(y, no):
    h_hat, err_var = estimate_channel(y, no)
    x_hat, no_eff = _lmmse_equ(y, h_hat, err_var, no)
    llr = _demapper(x_hat, no_eff)
    return llr
```

Full file: `EvoX_testruns_ChannelEstimation/evox_testrun4/best/best_program.py`

</details>

<details>
<summary><strong>AI Telco Engineer best (workspace6_testrun5, gen07) — click to expand</strong></summary>

~250 lines — two-branch denoiser (`_branch_a`: fixed-taper Wiener; `_branch_b`: PDP-adaptive-window Wiener), 5 hand-tuned hyperparameter variants (`c0`–`c4`) evaluated per call via pilot-residual cross-validation (`_pilot_residual_norm`/`_pilot_residual_abs`), soft blending between branches (`_make_candidate`), a strict fallback to the LS baseline if every candidate is less pilot-consistent than raw LS, and post-hoc error-variance calibration against observed pilot residuals.

Full file: `the-ai-telco-engineer/tasks/channel_estimation/workspace_6/workspace6_testrun5/gen07-0007/solution.py`

</details>

## Methodology Notes

- **`evox_testrun5` and `evox_testrun6` folder reuse.** Both had multiple independent full runs written into the same output directory. Since checkpoints and `best/` are overwritten by filename collision (not versioned), only the *last* invocation's result survives on disk — earlier runs' scores are only recoverable from timestamped log files, not from their code. `evox_testrun6` additionally changed a variable (guide LLM: gpt-5-mini → gpt-5.5) rather than being a clean repeat, so it's excluded from this comparison entirely.
- **No fixed baseline on the AI Telco Engineer side.** Unlike SkyDiscover's `initial_program_path`, AI Telco Engineer has no seed-injection config — generation 0 is always the manager LLM's own first idea. The commonly-cited "LS baseline ≈ 94" figure appears verbatim in both frameworks' prompt text but has no traceable computation behind it in either repo, and doesn't match SkyDiscover's own measured baseline (101.69).
- **No held-out re-validation on the AI Telco Engineer side.** SkyDiscover re-evaluates its best program once more on fresh random draws before reporting a final score (the `test_nve` column, if shown). AI Telco Engineer's leaderboard "best NVE" is never re-validated — so its numbers may be somewhat optimistic in the same way SkyDiscover's un-validated in-run numbers are.
- **SNR grid density differs** (7 points/1dB step for SkyDiscover vs. 4 points/2dB step for AI Telco Engineer, same -9 to -2 dB range) — noted above, not yet reconciled.
