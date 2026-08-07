---
layout: page
title: Quantitative
permalink: /quantitative/
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
<a href="{{ '/' | relative_url }}" class="">Home</a><span class="sep">/</span><a href="{{ '/quantitative/' | relative_url }}" class="current">Quantitative</a><span class="sep">/</span><a href="{{ '/qualitative/' | relative_url }}" class="">Qualitative</a><span class="sep">/</span><a href="{{ '/evaluation/' | relative_url }}" class="">Evaluation</a>
</div>

# Quantitative Results

**Numbers only.** For the actual algorithms -- what each framework's best run came up with, and each run's starting hypothesis -- see [Qualitative](/qualitative/).

## The Task

Both frameworks were given the same problem: given the noisy received signal from a multi-antenna uplink transmission over a realistic outdoor wireless channel, estimate that channel well enough to recover the transmitted bits.

The transmitter sends a mix of known reference symbols (pilots) and unknown data symbols across many subcarriers and time slots, all distorted by the channel and corrupted by additive receiver noise. A solution receives two things: the received signal, covering every antenna, subcarrier, and time slot, and the noise level at the receiver. From that, it must produce a channel estimate, plus a confidence/error-variance measure, using only the pilot symbols to infer what happened to the unseen data symbols.

That channel estimate then feeds a fixed downstream pipeline that turns it into soft bit decisions, which a standard error-correcting code decodes into a final result. A solution is scored by how close its resulting bit-error rate gets to the bit-error rate achievable with perfect knowledge of the channel, averaged across several low-SNR (noisy) operating points.

## Channel-Estimation Benchmark

Both frameworks target the same task: implement `mimo_detector(y, no)` for a 4×16 MIMO OFDM uplink (3GPP UMi channel, 5G NR LDPC, QPSK), minimizing the **Normalized Validation Error**, defined as:

```
       1           BLER_candidate(s) 
NVE = ───   · Σ   ───────────────────
      |S|   s∈S   BLER_perfect-CSI(s)
```

where **S** is the set of SNR test points the benchmark evaluates at, **BLER_candidate(s)** is the block error rate produced by the candidate channel estimator at SNR point *s*, and **BLER_perfect-CSI(s)** is the block error rate produced by the same fixed equalizer and demapper given perfect knowledge of the channel at that same SNR point. NVE = 1 means the candidate matches perfect-CSI performance exactly; lower is better, and values below 1 are possible since BLER is itself a noisy Monte Carlo estimate. Only the channel-estimation stage is mutable: the LMMSE equalizer and APP demapper are fixed scaffold in both frameworks. Physical-layer parameters (antenna counts, FFT size, subcarrier spacing, carrier frequency, batch size, Monte-Carlo iterations) are identical between the two setups. One methodology difference remains: SkyDiscover averages NVE over 7 SNR points (-9 to -2 dB, 1 dB step); AI Telco Engineer averages over 4 (-9 to -2 dB, 2 dB step).

## Run Summary

Both frameworks were run under matched settings so the comparison is head-to-head:

| Setting | Matched between frameworks |
|---|---|
| Mode | Single job, single idea, single worker per generation/iteration |
| Budget | 10 generations/iterations, 5 runs each (50 total per framework) |
| Physical-layer config | Identical (antenna counts, FFT size, subcarrier spacing, carrier frequency, batch size, Monte-Carlo iterations) |

| Framework | Runs compared | Model |
|---|---|---|
| **EvoX / SkyDiscover** | Run 1–5 | gpt-5.5 (solution) + gpt-5 / gpt-5-mini (search-strategy meta-evolution) |
| **AI Telco Engineer** | Run 1–5 | gpt-5.5 (agent + manager) |

### Cost & Run Time

| Framework | Average Cost | Average Run Time |
|---|---|---|
| **EvoX / SkyDiscover** | **$2.34** | **43.2 min** |
| **AI Telco Engineer** | **$4.43** | **45.8 min** |

### Best NVE per run

| Run # | EvoX / SkyDiscover | AI Telco Engineer |
|---|---|---|
| 1 | 13.22 | 76.75 |
| 2 | 11.86 | **14.70** |
| 3 | 19.94 | 94.38 |
| 4 | 9.98* | 58.72 |
| 5 | 58.27 | 90.21 |
| **Best** | **9.98\*** | **14.70** |
| **Worst** | **58.27** | **94.38** |

\* This value was reproduced using the 4-point SNR method, as used by AI Telco Engineer. Since NVE is a Monte Carlo estimate, this was measured across 10 reseeded evaluations; the average was 11.77.

## NVE per generation -- AI Telco Engineer

Generation 0 is **not** a fixed baseline -- AI Telco Engineer has no seed-injection mechanism, so gen0 is always the manager LLM's own first idea, which varies wildly run to run (from 525 to 9,291 NVE).

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
  <line class="nc-grid-line" x1="56" y1="346" x2="700" y2="346"></line>
  <line class="nc-grid-line" x1="56" y1="236" x2="700" y2="236"></line>
  <line class="nc-grid-line" x1="56" y1="126" x2="700" y2="126"></line>
  <line class="nc-grid-line" x1="56" y1="16" x2="700" y2="16"></line>
  <text class="nc-axis-text" x="48" y="349.5" text-anchor="end">10</text>
  <text class="nc-axis-text" x="48" y="239.5" text-anchor="end">100</text>
  <text class="nc-axis-text" x="48" y="129.5" text-anchor="end">1,000</text>
  <text class="nc-axis-text" x="48" y="19.5" text-anchor="end">10,000</text>
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

  <!-- Run 1 -->
  <polyline class="nc-series" stroke="var(--nc-c1)" points="56.0,69.4 127.6,242.9 199.1,239.9 270.7,242.8 342.2,242.9 413.8,247.3 485.3,246.8 556.9,243.7 628.4,246.4 700.0,248.6"></polyline>
  <circle class="nc-dot" cx="56.0" cy="69.4" r="4" fill="var(--nc-c1)"><title>Run 1 gen0: 3269.05</title></circle>
  <circle class="nc-dot" cx="127.6" cy="242.9" r="4" fill="var(--nc-c1)"><title>Run 1 gen1: 86.63</title></circle>
  <circle class="nc-dot" cx="199.1" cy="239.9" r="4" fill="var(--nc-c1)"><title>Run 1 gen2: 92.08</title></circle>
  <circle class="nc-dot" cx="270.7" cy="242.8" r="4" fill="var(--nc-c1)"><title>Run 1 gen3: 86.67</title></circle>
  <circle class="nc-dot" cx="342.2" cy="242.9" r="4" fill="var(--nc-c1)"><title>Run 1 gen4: 86.63</title></circle>
  <circle class="nc-dot" cx="413.8" cy="247.3" r="4" fill="var(--nc-c1)"><title>Run 1 gen5: 78.88</title></circle>
  <circle class="nc-dot" cx="485.3" cy="246.8" r="4" fill="var(--nc-c1)"><title>Run 1 gen6: 79.73</title></circle>
  <circle class="nc-dot" cx="556.9" cy="243.7" r="4" fill="var(--nc-c1)"><title>Run 1 gen7: 85.12</title></circle>
  <circle class="nc-dot" cx="628.4" cy="246.4" r="4" fill="var(--nc-c1)"><title>Run 1 gen8: 80.40</title></circle>
  <circle class="nc-dot" cx="700.0" cy="248.6" r="4" fill="var(--nc-c1)"><title>Run 1 gen9: 76.75</title></circle>

  <!-- Run 2 -->
  <polyline class="nc-series" stroke="var(--nc-c2)" points="56.0,64.6 127.6,310.8 199.1,324.0 270.7,231.1 342.2,327.6 413.8,324.0 485.3,327.6 556.9,325.0 628.4,327.6 700.0,327.5"></polyline>
  <circle class="nc-dot" cx="56.0" cy="64.6" r="4" fill="var(--nc-c2)"><title>Run 2 gen0: 3616.34</title></circle>
  <circle class="nc-dot" cx="127.6" cy="310.8" r="4" fill="var(--nc-c2)"><title>Run 2 gen1: 20.89</title></circle>
  <circle class="nc-dot" cx="199.1" cy="324.0" r="4" fill="var(--nc-c2)"><title>Run 2 gen2: 15.84</title></circle>
  <circle class="nc-dot" cx="270.7" cy="231.1" r="4" fill="var(--nc-c2)"><title>Run 2 gen3: 110.70</title></circle>
  <circle class="nc-dot" cx="342.2" cy="327.6" r="4" fill="var(--nc-c2)"><title>Run 2 gen4: 14.70</title></circle>
  <circle class="nc-dot" cx="413.8" cy="324.0" r="4" fill="var(--nc-c2)"><title>Run 2 gen5: 15.84</title></circle>
  <circle class="nc-dot" cx="485.3" cy="327.6" r="4" fill="var(--nc-c2)"><title>Run 2 gen6: 14.70</title></circle>
  <circle class="nc-dot" cx="556.9" cy="325.0" r="4" fill="var(--nc-c2)"><title>Run 2 gen7: 15.51</title></circle>
  <circle class="nc-dot" cx="628.4" cy="327.6" r="4" fill="var(--nc-c2)"><title>Run 2 gen8: 14.70</title></circle>
  <circle class="nc-dot" cx="700.0" cy="327.5" r="4" fill="var(--nc-c2)"><title>Run 2 gen9: 14.72</title></circle>

  <!-- Run 3 -->
  <polyline class="nc-series" stroke="var(--nc-c3)" points="56.0,156.7 127.6,66.7 199.1,224.6 270.7,238.1 342.2,238.5 413.8,238.8 485.3,238.6 556.9,238.0 628.4,238.2 700.0,238.1"></polyline>
  <circle class="nc-dot" cx="56.0" cy="156.7" r="4" fill="var(--nc-c3)"><title>Run 3 gen0: 525.38</title></circle>
  <circle class="nc-dot" cx="127.6" cy="66.7" r="4" fill="var(--nc-c3)"><title>Run 3 gen1: 3458.74</title></circle>
  <circle class="nc-dot" cx="199.1" cy="224.6" r="4" fill="var(--nc-c3)"><title>Run 3 gen2: 127.01</title></circle>
  <circle class="nc-dot" cx="270.7" cy="238.1" r="4" fill="var(--nc-c3)"><title>Run 3 gen3: 95.70</title></circle>
  <circle class="nc-dot" cx="342.2" cy="238.5" r="4" fill="var(--nc-c3)"><title>Run 3 gen4: 94.90</title></circle>
  <circle class="nc-dot" cx="413.8" cy="238.8" r="4" fill="var(--nc-c3)"><title>Run 3 gen5: 94.38</title></circle>
  <circle class="nc-dot" cx="485.3" cy="238.6" r="4" fill="var(--nc-c3)"><title>Run 3 gen6: 94.62</title></circle>
  <circle class="nc-dot" cx="556.9" cy="238.0" r="4" fill="var(--nc-c3)"><title>Run 3 gen7: 95.94</title></circle>
  <circle class="nc-dot" cx="628.4" cy="238.2" r="4" fill="var(--nc-c3)"><title>Run 3 gen8: 95.56</title></circle>
  <circle class="nc-dot" cx="700.0" cy="238.1" r="4" fill="var(--nc-c3)"><title>Run 3 gen9: 95.68</title></circle>

  <!-- Run 4 -->
  <polyline class="nc-series" stroke="var(--nc-c4)" points="56.0,42.8 127.6,171.9 199.1,236.1 270.7,178.7 342.2,233.8 413.8,238.2 485.3,231.4 556.9,238.2 628.4,237.3 700.0,261.4"></polyline>
  <circle class="nc-dot" cx="56.0" cy="42.8" r="4" fill="var(--nc-c4)"><title>Run 4 gen0: 5712.23</title></circle>
  <circle class="nc-dot" cx="127.6" cy="171.9" r="4" fill="var(--nc-c4)"><title>Run 4 gen1: 382.42</title></circle>
  <circle class="nc-dot" cx="199.1" cy="236.1" r="4" fill="var(--nc-c4)"><title>Run 4 gen2: 99.74</title></circle>
  <circle class="nc-dot" cx="270.7" cy="178.7" r="4" fill="var(--nc-c4)"><title>Run 4 gen3: 331.91</title></circle>
  <circle class="nc-dot" cx="342.2" cy="233.8" r="4" fill="var(--nc-c4)"><title>Run 4 gen4: 104.68</title></circle>
  <circle class="nc-dot" cx="413.8" cy="238.2" r="4" fill="var(--nc-c4)"><title>Run 4 gen5: 95.47</title></circle>
  <circle class="nc-dot" cx="485.3" cy="231.4" r="4" fill="var(--nc-c4)"><title>Run 4 gen6: 110.01</title></circle>
  <circle class="nc-dot" cx="556.9" cy="238.2" r="4" fill="var(--nc-c4)"><title>Run 4 gen7: 95.47</title></circle>
  <circle class="nc-dot" cx="628.4" cy="237.3" r="4" fill="var(--nc-c4)"><title>Run 4 gen8: 97.30</title></circle>
  <circle class="nc-dot" cx="700.0" cy="261.4" r="4" fill="var(--nc-c4)"><title>Run 4 gen9: 58.72</title></circle>

  <!-- Run 5 -->
  <polyline class="nc-series" stroke="var(--nc-c5)" points="56.0,19.5 127.6,197.7 199.1,197.0 270.7,238.0 342.2,238.2 413.8,238.2 485.3,238.1 556.9,238.2 628.4,238.2 700.0,240.9"></polyline>
  <circle class="nc-dot" cx="56.0" cy="19.5" r="4" fill="var(--nc-c5)"><title>Run 5 gen0: 9291.07</title></circle>
  <circle class="nc-dot" cx="127.6" cy="197.7" r="4" fill="var(--nc-c5)"><title>Run 5 gen1: 222.96</title></circle>
  <circle class="nc-dot" cx="199.1" cy="197.0" r="4" fill="var(--nc-c5)"><title>Run 5 gen2: 226.20</title></circle>
  <circle class="nc-dot" cx="270.7" cy="238.0" r="4" fill="var(--nc-c5)"><title>Run 5 gen3: 95.90</title></circle>
  <circle class="nc-dot" cx="342.2" cy="238.2" r="4" fill="var(--nc-c5)"><title>Run 5 gen4: 95.47</title></circle>
  <circle class="nc-dot" cx="413.8" cy="238.2" r="4" fill="var(--nc-c5)"><title>Run 5 gen5: 95.52</title></circle>
  <circle class="nc-dot" cx="485.3" cy="238.1" r="4" fill="var(--nc-c5)"><title>Run 5 gen6: 95.79</title></circle>
  <circle class="nc-dot" cx="556.9" cy="238.2" r="4" fill="var(--nc-c5)"><title>Run 5 gen7: 95.47</title></circle>
  <circle class="nc-dot" cx="628.4" cy="238.2" r="4" fill="var(--nc-c5)"><title>Run 5 gen8: 95.47</title></circle>
  <circle class="nc-dot" cx="700.0" cy="240.9" r="4" fill="var(--nc-c5)"><title>Run 5 gen9: 90.21</title></circle>
</svg>
<div class="nc-legend">
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c1);"></span>Run 1</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c2);"></span>Run 2</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c3);"></span>Run 3</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c4);"></span>Run 4</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c5);"></span>Run 5</div>
</div>
<p class="nc-caption">Y axis is log-scaled (NVE ranges from ~14.7 to ~9,291 across these runs). Hover a point for its exact value. All 10 generations succeeded in every one of these 5 runs, with no missing points.</p>
</div>
</div>


| Gen | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---|---|---|---|---|
| 0 | 3269.05 | 3616.34 | 525.38 | 5712.23 | 9291.07 |
| 1 | 86.63 | 20.89 | 3458.74 | 382.42 | 222.96 |
| 2 | 92.08 | 15.84 | 127.01 | 99.74 | 226.20 |
| 3 | 86.67 | 110.70 | 95.70 | 331.91 | 95.90 |
| 4 | 86.63 | 14.70 | 94.90 | 104.68 | 95.47 |
| 5 | 78.88 | 15.84 | 94.38 | 95.47 | 95.52 |
| 6 | 79.73 | 14.70 | 94.62 | 110.01 | 95.79 |
| 7 | 85.12 | 15.51 | 95.94 | 95.47 | 95.47 |
| 8 | 80.40 | 14.70 | 95.56 | 97.30 | 95.47 |
| 9 | 76.75 | 14.72 | 95.68 | 58.72 | 90.21 |


## NVE per iteration -- EvoX / SkyDiscover

Iteration 0 **is** a fixed baseline -- the literal LS-only seed program, executed verbatim every run, always scoring NVE = 101.69. All five runs converge from the same starting point, which is what makes them directly comparable.

| Iter | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---|---|---|---|---|
| 0 | 101.69 | 101.69 | 101.69 | 101.69 | 101.69 |
| 1 | 58.46 | 222.85 | 69.44 | 45.36 | 129.98 |
| 2 | 57.82 | 104.62 | 80.99 | 17.07 | 96.32 |
| 3 | 19.70 | 28.79 | 56.32 | 23.22 | 99.50 |
| 4 | 20.74 | 27.04 | 145.32 | 17.31 | 81.04 |
| 5 | 13.49 | 29.22 | 58.20 | 9.99 | 85.57 |
| 6 | 16.56 | 27.95 | 56.20 | 10.51 | 84.06 |
| 7 | 13.22 | 18.74 | 21.68 | 10.33 | 76.52 |
| 8 | 22.22 | 12.18 | 19.94 | 11.11 | 59.51 |
| 9 | 16.39 | 11.86 | 21.47 | 10.33 | 58.27 |
| 10 | 17.30 | 14.14 | 20.98 | 10.58 | 58.32 |

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
<svg viewBox="0 0 720 380" role="img" aria-label="NVE per iteration across 5 EvoX runs, log scale">
  <line class="nc-grid-line" x1="56" y1="338.6" x2="700" y2="338.6"></line>
  <line class="nc-grid-line" x1="56" y1="177.3" x2="700" y2="177.3"></line>
  <line class="nc-grid-line" x1="56" y1="16" x2="700" y2="16"></line>
  <text class="nc-axis-text" x="48" y="342.1" text-anchor="end">10</text>
  <text class="nc-axis-text" x="48" y="180.8" text-anchor="end">100</text>
  <text class="nc-axis-text" x="48" y="19.5" text-anchor="end">1,000</text>
  <text class="nc-axis-text" x="56.0" y="365" text-anchor="middle">0</text>
  <text class="nc-axis-text" x="120.4" y="365" text-anchor="middle">1</text>
  <text class="nc-axis-text" x="184.8" y="365" text-anchor="middle">2</text>
  <text class="nc-axis-text" x="249.2" y="365" text-anchor="middle">3</text>
  <text class="nc-axis-text" x="313.6" y="365" text-anchor="middle">4</text>
  <text class="nc-axis-text" x="378.0" y="365" text-anchor="middle">5</text>
  <text class="nc-axis-text" x="442.4" y="365" text-anchor="middle">6</text>
  <text class="nc-axis-text" x="506.8" y="365" text-anchor="middle">7</text>
  <text class="nc-axis-text" x="571.2" y="365" text-anchor="middle">8</text>
  <text class="nc-axis-text" x="635.6" y="365" text-anchor="middle">9</text>
  <text class="nc-axis-text" x="700.0" y="365" text-anchor="middle">10</text>

  <!-- Run 1 -->
  <polyline class="nc-series" stroke="var(--nc-c1)" points="56.0,176.1 120.4,214.9 184.8,215.7 249.2,291.1 313.6,287.5 378.0,317.6 442.4,303.3 506.8,319.1 571.2,282.7 635.6,304.0 700.0,300.2"></polyline>
  <circle class="nc-dot" cx="56.0" cy="176.1" r="4" fill="var(--nc-c1)"><title>Run 1 iter0: 101.69</title></circle>
  <circle class="nc-dot" cx="120.4" cy="214.9" r="4" fill="var(--nc-c1)"><title>Run 1 iter1: 58.46</title></circle>
  <circle class="nc-dot" cx="184.8" cy="215.7" r="4" fill="var(--nc-c1)"><title>Run 1 iter2: 57.82</title></circle>
  <circle class="nc-dot" cx="249.2" cy="291.1" r="4" fill="var(--nc-c1)"><title>Run 1 iter3: 19.70</title></circle>
  <circle class="nc-dot" cx="313.6" cy="287.5" r="4" fill="var(--nc-c1)"><title>Run 1 iter4: 20.74</title></circle>
  <circle class="nc-dot" cx="378.0" cy="317.6" r="4" fill="var(--nc-c1)"><title>Run 1 iter5: 13.49</title></circle>
  <circle class="nc-dot" cx="442.4" cy="303.3" r="4" fill="var(--nc-c1)"><title>Run 1 iter6: 16.56</title></circle>
  <circle class="nc-dot" cx="506.8" cy="319.1" r="4" fill="var(--nc-c1)"><title>Run 1 iter7: 13.22</title></circle>
  <circle class="nc-dot" cx="571.2" cy="282.7" r="4" fill="var(--nc-c1)"><title>Run 1 iter8: 22.22</title></circle>
  <circle class="nc-dot" cx="635.6" cy="304.0" r="4" fill="var(--nc-c1)"><title>Run 1 iter9: 16.39</title></circle>
  <circle class="nc-dot" cx="700.0" cy="300.2" r="4" fill="var(--nc-c1)"><title>Run 1 iter10: 17.30</title></circle>

  <!-- Run 2 -->
  <polyline class="nc-series" stroke="var(--nc-c2)" points="56.0,176.1 120.4,121.2 184.8,174.1 249.2,264.5 313.6,268.9 378.0,263.5 442.4,266.6 506.8,294.6 571.2,324.8 635.6,326.7 700.0,314.3"></polyline>
  <circle class="nc-dot" cx="56.0" cy="176.1" r="4" fill="var(--nc-c2)"><title>Run 2 iter0: 101.69</title></circle>
  <circle class="nc-dot" cx="120.4" cy="121.2" r="4" fill="var(--nc-c2)"><title>Run 2 iter1: 222.85</title></circle>
  <circle class="nc-dot" cx="184.8" cy="174.1" r="4" fill="var(--nc-c2)"><title>Run 2 iter2: 104.62</title></circle>
  <circle class="nc-dot" cx="249.2" cy="264.5" r="4" fill="var(--nc-c2)"><title>Run 2 iter3: 28.79</title></circle>
  <circle class="nc-dot" cx="313.6" cy="268.9" r="4" fill="var(--nc-c2)"><title>Run 2 iter4: 27.04</title></circle>
  <circle class="nc-dot" cx="378.0" cy="263.5" r="4" fill="var(--nc-c2)"><title>Run 2 iter5: 29.22</title></circle>
  <circle class="nc-dot" cx="442.4" cy="266.6" r="4" fill="var(--nc-c2)"><title>Run 2 iter6: 27.95</title></circle>
  <circle class="nc-dot" cx="506.8" cy="294.6" r="4" fill="var(--nc-c2)"><title>Run 2 iter7: 18.74</title></circle>
  <circle class="nc-dot" cx="571.2" cy="324.8" r="4" fill="var(--nc-c2)"><title>Run 2 iter8: 12.18</title></circle>
  <circle class="nc-dot" cx="635.6" cy="326.7" r="4" fill="var(--nc-c2)"><title>Run 2 iter9: 11.86</title></circle>
  <circle class="nc-dot" cx="700.0" cy="314.3" r="4" fill="var(--nc-c2)"><title>Run 2 iter10: 14.14</title></circle>

  <!-- Run 3 -->
  <polyline class="nc-series" stroke="var(--nc-c3)" points="56.0,176.1 120.4,202.9 184.8,192.1 249.2,217.5 313.6,151.1 378.0,215.2 442.4,217.7 506.8,284.4 571.2,290.3 635.6,285.1 700.0,286.7"></polyline>
  <circle class="nc-dot" cx="56.0" cy="176.1" r="4" fill="var(--nc-c3)"><title>Run 3 iter0: 101.69</title></circle>
  <circle class="nc-dot" cx="120.4" cy="202.9" r="4" fill="var(--nc-c3)"><title>Run 3 iter1: 69.44</title></circle>
  <circle class="nc-dot" cx="184.8" cy="192.1" r="4" fill="var(--nc-c3)"><title>Run 3 iter2: 80.99</title></circle>
  <circle class="nc-dot" cx="249.2" cy="217.5" r="4" fill="var(--nc-c3)"><title>Run 3 iter3: 56.32</title></circle>
  <circle class="nc-dot" cx="313.6" cy="151.1" r="4" fill="var(--nc-c3)"><title>Run 3 iter4: 145.32</title></circle>
  <circle class="nc-dot" cx="378.0" cy="215.2" r="4" fill="var(--nc-c3)"><title>Run 3 iter5: 58.20</title></circle>
  <circle class="nc-dot" cx="442.4" cy="217.7" r="4" fill="var(--nc-c3)"><title>Run 3 iter6: 56.20</title></circle>
  <circle class="nc-dot" cx="506.8" cy="284.4" r="4" fill="var(--nc-c3)"><title>Run 3 iter7: 21.68</title></circle>
  <circle class="nc-dot" cx="571.2" cy="290.3" r="4" fill="var(--nc-c3)"><title>Run 3 iter8: 19.94</title></circle>
  <circle class="nc-dot" cx="635.6" cy="285.1" r="4" fill="var(--nc-c3)"><title>Run 3 iter9: 21.47</title></circle>
  <circle class="nc-dot" cx="700.0" cy="286.7" r="4" fill="var(--nc-c3)"><title>Run 3 iter10: 20.98</title></circle>

  <!-- Run 4 -->
  <polyline class="nc-series" stroke="var(--nc-c4)" points="56.0,176.1 120.4,232.7 184.8,301.2 249.2,279.6 313.6,300.2 378.0,338.7 442.4,335.1 506.8,336.3 571.2,331.2 635.6,336.3 700.0,334.7"></polyline>
  <circle class="nc-dot" cx="56.0" cy="176.1" r="4" fill="var(--nc-c4)"><title>Run 4 iter0: 101.69</title></circle>
  <circle class="nc-dot" cx="120.4" cy="232.7" r="4" fill="var(--nc-c4)"><title>Run 4 iter1: 45.36</title></circle>
  <circle class="nc-dot" cx="184.8" cy="301.2" r="4" fill="var(--nc-c4)"><title>Run 4 iter2: 17.07</title></circle>
  <circle class="nc-dot" cx="249.2" cy="279.6" r="4" fill="var(--nc-c4)"><title>Run 4 iter3: 23.22</title></circle>
  <circle class="nc-dot" cx="313.6" cy="300.2" r="4" fill="var(--nc-c4)"><title>Run 4 iter4: 17.31</title></circle>
  <circle class="nc-dot" cx="378.0" cy="338.7" r="4" fill="var(--nc-c4)"><title>Run 4 iter5: 9.99</title></circle>
  <circle class="nc-dot" cx="442.4" cy="335.1" r="4" fill="var(--nc-c4)"><title>Run 4 iter6: 10.51</title></circle>
  <circle class="nc-dot" cx="506.8" cy="336.3" r="4" fill="var(--nc-c4)"><title>Run 4 iter7: 10.33</title></circle>
  <circle class="nc-dot" cx="571.2" cy="331.2" r="4" fill="var(--nc-c4)"><title>Run 4 iter8: 11.11</title></circle>
  <circle class="nc-dot" cx="635.6" cy="336.3" r="4" fill="var(--nc-c4)"><title>Run 4 iter9: 10.33</title></circle>
  <circle class="nc-dot" cx="700.0" cy="334.7" r="4" fill="var(--nc-c4)"><title>Run 4 iter10: 10.58</title></circle>

  <!-- Run 5 -->
  <polyline class="nc-series" stroke="var(--nc-c5)" points="56.0,176.1 120.4,158.9 184.8,179.9 249.2,177.7 313.6,192.0 378.0,188.2 442.4,189.5 506.8,196.1 571.2,213.7 635.6,215.1 700.0,215.1"></polyline>
  <circle class="nc-dot" cx="56.0" cy="176.1" r="4" fill="var(--nc-c5)"><title>Run 5 iter0: 101.69</title></circle>
  <circle class="nc-dot" cx="120.4" cy="158.9" r="4" fill="var(--nc-c5)"><title>Run 5 iter1: 129.98</title></circle>
  <circle class="nc-dot" cx="184.8" cy="179.9" r="4" fill="var(--nc-c5)"><title>Run 5 iter2: 96.32</title></circle>
  <circle class="nc-dot" cx="249.2" cy="177.7" r="4" fill="var(--nc-c5)"><title>Run 5 iter3: 99.50</title></circle>
  <circle class="nc-dot" cx="313.6" cy="192.0" r="4" fill="var(--nc-c5)"><title>Run 5 iter4: 81.04</title></circle>
  <circle class="nc-dot" cx="378.0" cy="188.2" r="4" fill="var(--nc-c5)"><title>Run 5 iter5: 85.57</title></circle>
  <circle class="nc-dot" cx="442.4" cy="189.5" r="4" fill="var(--nc-c5)"><title>Run 5 iter6: 84.06</title></circle>
  <circle class="nc-dot" cx="506.8" cy="196.1" r="4" fill="var(--nc-c5)"><title>Run 5 iter7: 76.52</title></circle>
  <circle class="nc-dot" cx="571.2" cy="213.7" r="4" fill="var(--nc-c5)"><title>Run 5 iter8: 59.51</title></circle>
  <circle class="nc-dot" cx="635.6" cy="215.1" r="4" fill="var(--nc-c5)"><title>Run 5 iter9: 58.27</title></circle>
  <circle class="nc-dot" cx="700.0" cy="215.1" r="4" fill="var(--nc-c5)"><title>Run 5 iter10: 58.32</title></circle>
</svg>
<div class="nc-legend">
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c1);"></span>Run 1</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c2);"></span>Run 2</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c3);"></span>Run 3</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c4);"></span>Run 4</div>
  <div class="nc-legend-item"><span class="nc-swatch" style="background:var(--nc-c5);"></span>Run 5</div>
</div>
<p class="nc-caption">Y axis is log-scaled. All 5 runs start from the identical fixed LS baseline (iteration 0, NVE 101.69), the only point where every line coincides.</p>
</div>
</div>

