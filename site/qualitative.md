---
layout: page
title: Qualitative
permalink: /qualitative/
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
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="current">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a><span class="sep">/</span><a href="{{ '/getting-started/' | relative_url }}" class="">Getting Started</a>
</div>

# Qualitative Results

**The actual algorithms.** For NVE numbers and run statistics only, see [Quantitative](/quantitative/).

## Best Algorithm -- Side by Side

| | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| Run | `evox_testrun4`, iteration 5 | `workspace7_testrun2`, gen04-0004 (tied with gen06, gen08) |
| NVE | **9.985** | 14.7047 |
| Approach | LS seed → delay-domain Wiener PDP shrinkage → RX-antenna spatial covariance eigenshrinkage → 5-tap time smoothing → residual-based error-variance calibration | LS seed → pilot-only empirical-Bayes GP/Wiener estimator with a bank of candidate delay-Doppler correlation kernels (multiple frequency/Doppler profiles), soft-selected per link/receive-chain by a GP-marginal-likelihood-style score, blended with the LS estimate → one decision-directed refinement pass using high-confidence data REs as weighted virtual pilots → error-variance calibration |
| Code size | ~55 lines | ~407 lines |

The gap between the two frameworks' best runs narrows substantially once AI Telco Engineer's data is corrected to the `workspace_7` batch (see Methodology Notes on the [Quantitative](/quantitative/) page): 9.985 vs. 14.70, not the much wider margin implied by the earlier `workspace_6` batch. EvoX's winning solution is still the simpler, more direct pipeline -- no runtime branching or candidate selection -- while AI Telco Engineer's winner explicitly builds and scores several candidate covariance kernels per call before committing to one.

<details>
<summary><strong>SkyDiscover best (evox_testrun4, iteration 5) -- click to expand</strong></summary>

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
<summary><strong>AI Telco Engineer best (workspace7_testrun2, gen04-0004) -- click to expand</strong></summary>

~407 lines -- precomputes pilot masks/indices and a bank of candidate delay-Doppler correlation kernels (`_K_BANK`: several exponential/uniform/truncated-exponential delay profiles × several Doppler profiles derived from `CARRIER_FREQUENCY`), per receive-chain/stream solves a batched Cholesky system against each candidate kernel (`_eb_gp_estimate`), scores candidates with a blended leave-one-out/marginal negative-log-likelihood, soft-mixes the top-3 candidates with the raw LS estimate by a softmax over that score, then runs one decision-directed refinement pass (`_dd_refine`): equalizes and demaps with the initial estimate, converts LLRs to soft QAM means/variances, treats a capped, confidence-gated subset of data REs as additional weighted virtual pilots, and refits the same kernel-based estimate before final equalization/demapping.

Full file: `the-ai-telco-engineer/tasks/channel_estimation/workspace_7/workspace7_testrun2/gen04-0004/draft.py`

</details>

## Initial Hypothesis vs. Best NVE -- AI Telco Engineer

Each run is assigned a distinct starting approach by the manager LLM before generation 0 begins.

| Run | Initial hypothesis | Best NVE |
|---|---|---|
| 1 | Adaptive delay-Doppler sparse denoising -- LS pilot estimate, IFFT to delay taps with noise-floor Wiener shrinkage, FFT to Doppler domain with a second adaptive shrinkage pass, inverse transform back. | 76.75 |
| 2 | Two-stage sparse delay-Doppler Bayesian estimator -- fit a compact 2D Fourier (delay+Doppler) basis to pilot LS via ridge regression, then one decision-directed refinement using high-confidence data REs as virtual pilots. | **14.70** |
| 3 | Fixed-iteration Bayesian decision-directed delay-domain estimator -- LS + delay-domain shrinkage/Doppler smoothing, then 1-2 unrolled decision-directed refinement passes treating confident data REs as extra pilots. | 94.38 |
| 4 | Transform-domain sparse Bayesian/Wiener estimator -- LS pilots, delay-domain tap selection/shrinkage, Doppler ridge-regression basis fit, one EM-style decision-directed refinement. | 58.72 |
| 5 | Parametric 2D delay-Doppler shrinkage estimator -- LS pilots, delay-domain tap selection via energy threshold, per-tap Doppler polynomial/DCT fit via ridge regression, transform back to frequency. | 90.21 |

Notably, the run whose best NVE (14.70) beat every other run by a wide margin (next-best is 58.72) started from a hypothesis that isn't obviously more sophisticated than the others -- all 5 hypotheses independently converge on the same family (delay-Doppler transform-domain denoising off an LS pilot estimate, plus some form of decision-directed refinement). What the 407-line winning implementation actually does differently is explored empirically at generation time (the candidate-kernel bank + per-link soft-selection), not prescribed by the initial hypothesis text.

## Initial Hypothesis vs. Best NVE -- EvoX / SkyDiscover

EvoX has no per-run hypothesis assignment -- every run starts from the identical fixed LS baseline (`initial_program_path`), and the LLM is free to propose its own first direction at iteration 1 without a prescribed approach.

| Run | Initial hypothesis | Best NVE |
|---|---|---|
| 1 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 13.22 |
| 2 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 11.86 |
| 3 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 19.94 |
| 4 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 9.98 |
| 5 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | *pending re-run* |

## Methodology Notes

- **AI Telco Engineer data source: `workspace_7`, not `workspace_6`.** See the [Quantitative](/quantitative/) page's Methodology Notes for why -- in short, `workspace_7` is the correct/current batch (run after the eval-loop retry fix), and an earlier draft of this comparison mistakenly used an older `workspace_6` batch.
- **Zero hard failures in `workspace_7`.** Every one of the 5 runs' 10 generations returned a real score. This is a qualitative difference from the pre-fix behavior, not just a quantitative one -- see [Evaluation](/evaluation/) for the retry-loop mechanism responsible.
- **All 5 AI Telco hypotheses converge on the same algorithmic family** (delay-Doppler transform-domain denoising + decision-directed refinement), assigned independently by the manager LLM without seeing each other. EvoX has no equivalent diversity mechanism at the hypothesis level -- its exploration happens entirely through the search-strategy meta-evolution described on the [Architecture](/architecture/) page.
