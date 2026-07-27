---
layout: page
title: Results
permalink: /results/
---

# Results

**Head-to-head comparison: AI Telco Engineer vs. EvoX/SkyDiscover on the same channel-estimation benchmark, under matched settings (same physical-layer config, same single-job/single-idea/single-worker mode, same model family, same 10-generation/iteration budget).**

This page is split into two parts: [Quantitative](#quantitative) has the numbers only (NVE tables, run stats). [Qualitative](#qualitative) has the actual algorithms -- what each framework's best run came up with, and what each run started from.

## Quantitative

### Channel-Estimation Benchmark

Both frameworks target the same task: implement `mimo_detector(y, no)` for a 4×16 MIMO OFDM uplink (3GPP UMi channel, 5G NR LDPC, QPSK), minimizing the **Normalized Validation Error**:

```
NVE = mean over SNR points of  BLER_candidate / BLER_perfect-CSI
```

Lower is better. Only the channel-estimation stage is mutable -- the LMMSE equalizer and APP demapper are fixed scaffold in both frameworks. Physical-layer parameters (antenna counts, FFT size, subcarrier spacing, carrier frequency, batch size, Monte-Carlo iterations) are identical between the two setups -- SkyDiscover's evaluator was explicitly built to match the AI Telco Engineer task. One methodology difference remains: SkyDiscover averages NVE over 7 SNR points (-9 to -2 dB, 1 dB step); AI Telco Engineer averages over 4 (-9 to -2 dB, 2 dB step).

### Run Summary

| Framework | Runs compared | Model | Median best NVE | Range |
|---|---|---|---|---|
| **EvoX / SkyDiscover** | `evox_testrun1`–`4` | gpt-5.5 (solution) + gpt-5 / gpt-5-mini (search-strategy meta-evolution) | **16.6** | 9.98 – 19.94 |
| **AI Telco Engineer** | `workspace6_testrun1`–`5` | gpt-5.5 (agent + manager)* | **47.78** | 23.31 – 78.68 |

\* model not independently confirmed from logs for the AI Telco Engineer runs (no per-run model trace found), inferred from the project's other same-week runs.

`evox_testrun5` is excluded pending a clean re-run (its folder was reused across two independent invocations, so its current on-disk best doesn't reliably represent a single run -- see Methodology Notes below).

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

### NVE per generation -- AI Telco Engineer

Generation 0 is **not** a fixed baseline -- AI Telco Engineer has no seed-injection mechanism, so gen0 is always the manager LLM's own first idea, which varies wildly run to run (from 34 to 6912+ NVE).

<div class="nve-chart">
<style>
  .nve-chart {
    --nc-ink: #1e2b3c; --nc-ink-soft: #5b6b80; --nc-ink-faint: #a7b3c2;
    --nc-panel: #ffffff; --nc-line: #d3dce6; --nc-grid: #e6ecf3;
    --nc-c1: #2a78d6; --nc-c2: #eb6834; --nc-c3: #1baf7a; --nc-c4: #eda100; --nc-c5: #e87ba4;
    display: block; box-sizing: border-box; margin: 6px 0 14px;
    font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; color: var(--nc-ink);
  }
  @media (prefers-color-scheme: dark) {
    .nve-chart {
      --nc-ink: #e7edf5; --nc-ink-soft: #9db0c4; --nc-ink-faint: #4d6076;
      --nc-panel: #141f2d; --nc-line: #263344; --nc-grid: #1c2a3d;
      --nc-c1: #3987e5; --nc-c2: #d95926; --nc-c3: #199e70; --nc-c4: #c98500; --nc-c5: #d55181;
    }
  }
  .nve-chart, .nve-chart * { box-sizing: border-box; }
  .nve-chart .nc-wrap { border: 1px solid var(--nc-line); background: var(--nc-panel); padding: 14px 14px 10px; }
  .nve-chart svg { width: 100%; height: auto; display: block; }
  .nve-chart .nc-grid-line { stroke: var(--nc-grid); stroke-width: 1; }
  .nve-chart .nc-axis-text { fill: var(--nc-ink-faint); font-size: 10.5px; font-family: ui-monospace, "SF Mono", Consolas, monospace; }
  .nve-chart .nc-series { fill: none; stroke-width: 2; }
  .nve-chart .nc-dot { stroke: var(--nc-panel); stroke-width: 1.2; }
  .nve-chart .nc-legend { display: flex; flex-wrap: wrap; gap: 10px 18px; margin-top: 10px; font-size: 12px; }
  .nve-chart .nc-legend-item { display: flex; align-items: center; gap: 7px; color: var(--nc-ink-soft); }
  .nve-chart .nc-swatch { width: 16px; height: 2px; border-radius: 1px; flex: none; }
  .nve-chart .nc-caption { margin-top: 8px; font-size: 11.5px; color: var(--nc-ink-faint); line-height: 1.5; }
</style>
<div class="nc-wrap">
<svg viewBox="0 0 720 380" role="img" aria-label="NVE per generation across 5 AI Telco Engineer runs, log scale">
  <!-- y gridlines + labels (log scale: 10, 100, 1000, 10000) -->
  <line class="nc-grid-line" x1="56" y1="346" x2="700" y2="346"></line>
  <line class="nc-grid-line" x1="56" y1="236" x2="700" y2="236"></line>
  <line class="nc-grid-line" x1="56" y1="126" x2="700" y2="126"></line>
  <line class="nc-grid-line" x1="56" y1="16" x2="700" y2="16"></line>
  <text class="nc-axis-text" x="48" y="349.5" text-anchor="end">10</text>
  <text class="nc-axis-text" x="48" y="239.5" text-anchor="end">100</text>
  <text class="nc-axis-text" x="48" y="129.5" text-anchor="end">1,000</text>
  <text class="nc-axis-text" x="48" y="19.5" text-anchor="end">10,000</text>
  <!-- x axis labels (generation 0-9) -->
  <text class="nc-axis-text" x="56.0" y="365" text-anchor="middle">0</text>
  <text class="nc-axis-text" x="127.6" y="365" text-anchor="middle">1</text>
  <text class="nc-axis-text" x="199.1" y="365" text-anchor="middle">2</text>
  <text class="nc-axis-text" x="270.7" y="365" text-anchor="middle">3</text>
  <text class="nc-axis-text" x="342.2" y="365" text-anchor="middle">4</text>
  <text class="nc-axis-text" x="413.8" y="365" text-anchor="middle">5</text>
  <text class="nc-axis-text" x="485.3" y="365" text-anchor="middle">6</text>
  <text class="nc-axis-text" x="556.9" y="365" text-anchor="middle">7</text>
  <text class="nc-axis-text" x="628.4" y="365" text-anchor="middle">8</text>
  <text class="nc-axis-text" x="700.0" y="365" text-anchor="middle">9</text>

  <!-- testrun1 -->
  <polyline class="nc-series" stroke="var(--nc-c1)" points="127.6,193.7 199.1,247.5 270.7,247.5 342.2,19.5 413.8,242.4 485.3,247.5 556.9,247.5 628.4,245.4 700.0,247.4"></polyline>
  <circle class="nc-dot" cx="127.6" cy="193.7" r="4" fill="var(--nc-c1)"><title>testrun1 gen1: 242.44</title></circle>
  <circle class="nc-dot" cx="199.1" cy="247.5" r="4" fill="var(--nc-c1)"><title>testrun1 gen2: 78.68</title></circle>
  <circle class="nc-dot" cx="270.7" cy="247.5" r="4" fill="var(--nc-c1)"><title>testrun1 gen3: 78.68</title></circle>
  <circle class="nc-dot" cx="342.2" cy="19.5" r="4" fill="var(--nc-c1)"><title>testrun1 gen4: 9291.07</title></circle>
  <circle class="nc-dot" cx="413.8" cy="242.4" r="4" fill="var(--nc-c1)"><title>testrun1 gen5: 87.48</title></circle>
  <circle class="nc-dot" cx="485.3" cy="247.5" r="4" fill="var(--nc-c1)"><title>testrun1 gen6: 78.68</title></circle>
  <circle class="nc-dot" cx="556.9" cy="247.5" r="4" fill="var(--nc-c1)"><title>testrun1 gen7: 78.68</title></circle>
  <circle class="nc-dot" cx="628.4" cy="245.4" r="4" fill="var(--nc-c1)"><title>testrun1 gen8: 82.15</title></circle>
  <circle class="nc-dot" cx="700.0" cy="247.4" r="4" fill="var(--nc-c1)"><title>testrun1 gen9: 78.73</title></circle>

  <!-- testrun2 -->
  <polyline class="nc-series" stroke="var(--nc-c2)" points="56.0,286.9 127.6,286.5 199.1,280.0 556.9,293.7 628.4,296.6 700.0,295.1"></polyline>
  <circle class="nc-dot" cx="56.0" cy="286.9" r="4" fill="var(--nc-c2)"><title>testrun2 gen0: 34.49</title></circle>
  <circle class="nc-dot" cx="127.6" cy="286.5" r="4" fill="var(--nc-c2)"><title>testrun2 gen1: 34.74</title></circle>
  <circle class="nc-dot" cx="199.1" cy="280.0" r="4" fill="var(--nc-c2)"><title>testrun2 gen2: 39.77</title></circle>
  <circle class="nc-dot" cx="556.9" cy="293.7" r="4" fill="var(--nc-c2)"><title>testrun2 gen7: 29.88</title></circle>
  <circle class="nc-dot" cx="628.4" cy="296.6" r="4" fill="var(--nc-c2)"><title>testrun2 gen8: 28.12</title></circle>
  <circle class="nc-dot" cx="700.0" cy="295.1" r="4" fill="var(--nc-c2)"><title>testrun2 gen9: 29.00</title></circle>

  <!-- testrun3 -->
  <polyline class="nc-series" stroke="var(--nc-c3)" points="56.0,33.6 127.6,242.4 199.1,248.8 270.7,249.8 485.3,249.8 556.9,249.8 628.4,246.9 700.0,249.8"></polyline>
  <circle class="nc-dot" cx="56.0" cy="33.6" r="4" fill="var(--nc-c3)"><title>testrun3 gen0: 6912.60</title></circle>
  <circle class="nc-dot" cx="127.6" cy="242.4" r="4" fill="var(--nc-c3)"><title>testrun3 gen1: 87.40</title></circle>
  <circle class="nc-dot" cx="199.1" cy="248.8" r="4" fill="var(--nc-c3)"><title>testrun3 gen2: 76.42</title></circle>
  <circle class="nc-dot" cx="270.7" cy="249.8" r="4" fill="var(--nc-c3)"><title>testrun3 gen3: 74.91</title></circle>
  <circle class="nc-dot" cx="485.3" cy="249.8" r="4" fill="var(--nc-c3)"><title>testrun3 gen6: 74.91</title></circle>
  <circle class="nc-dot" cx="556.9" cy="249.8" r="4" fill="var(--nc-c3)"><title>testrun3 gen7: 74.91</title></circle>
  <circle class="nc-dot" cx="628.4" cy="246.9" r="4" fill="var(--nc-c3)"><title>testrun3 gen8: 79.57</title></circle>
  <circle class="nc-dot" cx="700.0" cy="249.8" r="4" fill="var(--nc-c3)"><title>testrun3 gen9: 74.91</title></circle>

  <!-- testrun4 -->
  <polyline class="nc-series" stroke="var(--nc-c4)" points="56.0,256.9 127.6,258.6 199.1,83.8 270.7,261.6 413.8,269.6 485.3,271.2 628.4,271.3"></polyline>
  <circle class="nc-dot" cx="56.0" cy="256.9" r="4" fill="var(--nc-c4)"><title>testrun4 gen0: 64.62</title></circle>
  <circle class="nc-dot" cx="127.6" cy="258.6" r="4" fill="var(--nc-c4)"><title>testrun4 gen1: 62.37</title></circle>
  <circle class="nc-dot" cx="199.1" cy="83.8" r="4" fill="var(--nc-c4)"><title>testrun4 gen2: 2420.44</title></circle>
  <circle class="nc-dot" cx="270.7" cy="261.6" r="4" fill="var(--nc-c4)"><title>testrun4 gen3: 58.51</title></circle>
  <circle class="nc-dot" cx="413.8" cy="269.6" r="4" fill="var(--nc-c4)"><title>testrun4 gen5: 49.53</title></circle>
  <circle class="nc-dot" cx="485.3" cy="271.2" r="4" fill="var(--nc-c4)"><title>testrun4 gen6: 47.85</title></circle>
  <circle class="nc-dot" cx="628.4" cy="271.3" r="4" fill="var(--nc-c4)"><title>testrun4 gen8: 47.78</title></circle>

  <!-- testrun5 -->
  <polyline class="nc-series" stroke="var(--nc-c5)" points="56.0,161.0 127.6,259.7 199.1,19.5 342.2,260.1 413.8,304.5 485.3,304.2 556.9,305.6 628.4,305.6 700.0,305.6"></polyline>
  <circle class="nc-dot" cx="56.0" cy="161.0" r="4" fill="var(--nc-c5)"><title>testrun5 gen0: 481.13</title></circle>
  <circle class="nc-dot" cx="127.6" cy="259.7" r="4" fill="var(--nc-c5)"><title>testrun5 gen1: 60.83</title></circle>
  <circle class="nc-dot" cx="199.1" cy="19.5" r="4" fill="var(--nc-c5)"><title>testrun5 gen2: 9291.07</title></circle>
  <circle class="nc-dot" cx="342.2" cy="260.1" r="4" fill="var(--nc-c5)"><title>testrun5 gen4: 60.35</title></circle>
  <circle class="nc-dot" cx="413.8" cy="304.5" r="4" fill="var(--nc-c5)"><title>testrun5 gen5: 23.83</title></circle>
  <circle class="nc-dot" cx="485.3" cy="304.2" r="4" fill="var(--nc-c5)"><title>testrun5 gen6: 23.99</title></circle>
  <circle class="nc-dot" cx="556.9" cy="305.6" r="4" fill="var(--nc-c5)"><title>testrun5 gen7: 23.31</title></circle>
  <circle class="nc-dot" cx="628.4" cy="305.6" r="4" fill="var(--nc-c5)"><title>testrun5 gen8: 23.31</title></circle>
  <circle class="nc-dot" cx="700.0" cy="305.6" r="4" fill="var(--nc-c5)"><title>testrun5 gen9: 23.31</title></circle>
</svg>
<div class="nc-legend">
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c1);"></span>testrun1</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c2);"></span>testrun2</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c3);"></span>testrun3</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c4);"></span>testrun4</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c5);"></span>testrun5</div>
</div>
<p class="nc-caption">Y axis is log-scaled (NVE ranges from ~10 to ~9,291 across these runs). Lines connect only the generations that actually returned a metric — hover a point for its exact value. Missing generations (hard failures, <code>NVE = inf</code>): testrun1 gen0 &middot; testrun2 gens 3&ndash;6 &middot; testrun3 gens 4&ndash;5 &middot; testrun4 gens 4, 7, 9 &middot; testrun5 gen3.</p>
</div>
</div>


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

*— = generation failed (`NVE = inf`) -- excluded from the chart above so the line connects straight through to the next successful generation, rather than breaking.*

### NVE per iteration -- EvoX / SkyDiscover

Iteration 0 **is** a fixed baseline -- the literal LS-only seed program, executed verbatim every run, always scoring NVE = 101.69. All four runs converge from the same starting point, which is what makes them directly comparable. (`testrun5` will be added once its clean re-run completes.)

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

![EvoX/SkyDiscover: NVE per iteration, 4 runs]({{ "/assets/images/evox_nve_per_iteration.png?v=1" | relative_url }})

## Qualitative

### Best Algorithm -- Side by Side

| | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| Run | `evox_testrun4`, iteration 5 | `workspace6_testrun5`, gen07 |
| NVE | **9.985** | 23.3115 |
| Approach | LS seed → delay-domain Wiener PDP shrinkage → RX-antenna spatial covariance eigenshrinkage → 5-tap time smoothing → residual-based error-variance calibration | LS seed → two parallel denoising branches (fixed-taper vs. PDP-adaptive-window Wiener filters) → 5 hand-tuned hyperparameter variants → pilot-residual cross-validation selects the best variant per call → pilot-consistency blending → error-variance calibration |
| Code size | ~55 lines | ~250 lines |

Notably, the more complex solution did *not* win -- AI Telco Engineer's best program builds and cross-validates 5 candidate estimators per call, while SkyDiscover's best program is a single, direct pipeline with no runtime branching, and still scores less than half the NVE.

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
<summary><strong>AI Telco Engineer best (workspace6_testrun5, gen07) -- click to expand</strong></summary>

~250 lines -- two-branch denoiser (`_branch_a`: fixed-taper Wiener; `_branch_b`: PDP-adaptive-window Wiener), 5 hand-tuned hyperparameter variants (`c0`–`c4`) evaluated per call via pilot-residual cross-validation (`_pilot_residual_norm`/`_pilot_residual_abs`), soft blending between branches (`_make_candidate`), a strict fallback to the LS baseline if every candidate is less pilot-consistent than raw LS, and post-hoc error-variance calibration against observed pilot residuals.

Full file: `the-ai-telco-engineer/tasks/channel_estimation/workspace_6/workspace6_testrun5/gen07-0007/solution.py`

</details>

### Initial Hypothesis vs. Best NVE -- AI Telco Engineer

Each run is assigned a distinct starting approach by the manager LLM before generation 0 begins.

| Run | Initial hypothesis | Best NVE |
|---|---|---|
| 1 | Delay-Doppler sparse Wiener estimator -- fit a low-dimensional 2D Fourier (delay + Doppler) basis to pilot LS observations via regularized least-squares. | 78.68 |
| 2 | Transform-domain denoising -- IFFT pilot LS estimates to the delay domain, apply adaptive shrinkage/Wiener filtering, then Doppler-aware time smoothing. | 28.12 |
| 3 | Parametric delay-Doppler estimator -- fit pilot observations to a truncated 2D Fourier basis via ridge regression. | 74.91 |
| 4 | 2D delay-Doppler denoising -- IFFT to delay domain with cyclic-prefix-windowed top-K tap shrinkage, plus Doppler-domain low-pass filtering. | 47.78 |
| 5 | Semi-blind iterative decision-directed estimator -- LS + delay-Doppler denoising, then 1-2 rounds of soft-decision-directed Kalman/LMMSE refinement using high-confidence data REs as virtual pilots. | 23.31 |

### Initial Hypothesis vs. Best NVE -- EvoX / SkyDiscover

EvoX has no per-run hypothesis assignment -- every run starts from the identical fixed LS baseline (`initial_program_path`), and the LLM is free to propose its own first direction at iteration 1 without a prescribed approach.

| Run | Initial hypothesis | Best NVE |
|---|---|---|
| 1 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 13.22 |
| 2 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 11.86 |
| 3 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 19.94 |
| 4 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | 9.98 |
| 5 | Fixed LS baseline (identical starting point every run, no assigned approach) -- NVE 101.69 | *pending re-run* |

## Methodology Notes

- **`evox_testrun5` and `evox_testrun6` folder reuse.** Both had multiple independent full runs written into the same output directory. Since checkpoints and `best/` are overwritten by filename collision (not versioned), only the *last* invocation's result survives on disk -- earlier runs' scores are only recoverable from timestamped log files, not from their code. `evox_testrun6` additionally changed a variable (guide LLM: gpt-5-mini → gpt-5.5) rather than being a clean repeat, so it's excluded from this comparison entirely.
- **No fixed baseline on the AI Telco Engineer side.** Unlike SkyDiscover's `initial_program_path`, AI Telco Engineer has no seed-injection config -- generation 0 is always the manager LLM's own first idea. The commonly-cited "LS baseline ≈ 94" figure appears verbatim in both frameworks' prompt text but has no traceable computation behind it in either repo, and doesn't match SkyDiscover's own measured baseline (101.69).
- **No held-out re-validation on the AI Telco Engineer side.** SkyDiscover re-evaluates its best program once more on fresh random draws before reporting a final score (the `test_nve` column, if shown). AI Telco Engineer's leaderboard "best NVE" is never re-validated -- so its numbers may be somewhat optimistic in the same way SkyDiscover's un-validated in-run numbers are.
- **SNR grid density differs** (7 points/1dB step for SkyDiscover vs. 4 points/2dB step for AI Telco Engineer, same -9 to -2 dB range) -- noted above, not yet reconciled.
