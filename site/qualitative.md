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
  .post-header { display: none; }
</style>
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/architecture/' | relative_url }}" class="">Architecture</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="current">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a>
</div>

# Qualitative Results

**The actual algorithms.** For NVE numbers and run statistics only, see [Quantitative](/quantitative/).

## Best Algorithm -- Side by Side

| | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| Run | Run 4, iteration 5 | Run 2 |
| NVE | **9.985\*** | 14.7047 |
| Approach | LS seed → delay-domain Wiener PDP shrinkage → RX-antenna spatial covariance eigenshrinkage → 5-tap time smoothing → residual-based error-variance calibration | LS seed → pilot-only empirical-Bayes GP/Wiener estimator with a bank of candidate delay-Doppler correlation kernels (multiple frequency/Doppler profiles), soft-selected per link/receive-chain by a GP-marginal-likelihood-style score, blended with the LS estimate → one decision-directed refinement pass using high-confidence data REs as weighted virtual pilots → error-variance calibration |
| Code size | ~55 lines | ~407 lines |

The gap between the two frameworks' best runs narrows substantially once AI Telco Engineer's results are corrected to use current, post-fix data (see the [Quantitative](/quantitative/) page): 9.985* vs. 14.70, not the much wider margin implied by an earlier draft of this comparison that used stale, pre-fix data. EvoX's winning solution is still the simpler, more direct pipeline -- no runtime branching or candidate selection -- while AI Telco Engineer's winner explicitly builds and scores several candidate covariance kernels per call before committing to one.

\* This value was reproduced using the 4-point SNR method, as used by AI Telco Engineer. Since NVE is a Monte Carlo estimate, this was measured across 10 reseeded evaluations; the average was 11.77.

<div class="code-compare">
<style>
  .code-compare {
    --cc-ink: #1e2b3c; --cc-ink-soft: #5b6b80; --cc-panel: #ffffff; --cc-line: #d3dce6;
    display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 20px 0 28px;
    font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    .code-compare { --cc-ink: #e7edf5; --cc-ink-soft: #9db0c4; --cc-panel: #141f2d; --cc-line: #263344; }
  }
  @media (max-width: 720px) { .code-compare { grid-template-columns: 1fr; } }
  .code-compare .cc-panel { border: 1px solid var(--cc-line); background: var(--cc-panel); padding: 12px 14px; border-radius: 4px; min-width: 0; }
  .code-compare .cc-title { margin: 0 0 10px; font-size: 13px; font-weight: 700; color: var(--cc-ink); }
  .code-compare .cc-panel pre { margin: 0; overflow-x: auto; font-size: 12px; }
  .code-compare .cc-desc { font-size: 13px; line-height: 1.55; color: var(--cc-ink-soft); margin: 0; }
</style>

<div class="cc-panel" markdown="1">
<p class="cc-title">SkyDiscover best (Run 4, iteration 5)</p>

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

</div>
<div class="cc-panel">
<p class="cc-title">AI Telco Engineer best (Run 2, ~407 lines)</p>
<p class="cc-desc">This solution precomputes pilot masks and indices, along with a bank of candidate delay-Doppler correlation kernels spanning several delay profiles (exponential, uniform, and truncated-exponential) and several Doppler profiles derived from the carrier frequency. For each receive chain, it fits every candidate kernel against the pilot observations with a batched Cholesky solve, scores each fit with a blended leave-one-out and marginal negative-log-likelihood criterion, and soft-mixes the top three candidates with the raw least-squares estimate using a softmax over their scores. It then runs one decision-directed refinement pass: equalize and demap with that initial estimate, convert the resulting soft bit values into QAM means and variances, treat a confidence-gated subset of data symbols as extra pilots, and refit the same kernel-based estimate before a final equalization and demapping pass.</p>
<pre><code>precompute pilot_mask, pilot_indices
K_BANK = build_kernel_bank(delay_profiles, doppler_profiles(carrier_frequency))

for each receive_chain:
    for kernel in K_BANK:
        estimate[kernel] = cholesky_solve(kernel, pilots)
        score[kernel]    = blended_loo_nll(estimate[kernel], pilots)
    weights = softmax(top_3(score))
    h_hat   = mix(weights, estimate[top_3], ls_estimate)

x_hat, llr  = equalize_and_demap(h_hat)
soft_pilots = confidence_gate(qam_soft_values(llr))
h_hat       = refit(K_BANK, pilots + soft_pilots)

return equalize_and_demap(h_hat)</code></pre>
</div>
</div>
