---
layout: page
title: Architecture
permalink: /architecture/
---

# Architecture

This page describes how SkyDiscover's **EvoX** search algorithm works — the same generic solution loop is shared by every search algorithm SkyDiscover supports, but EvoX adds a second, outer loop that evolves the search strategy itself.

## Two-Level Co-Evolution

EvoX runs two nested evolutionary processes at once:

- An **inner loop** that evolves candidate *solutions* to the target problem (e.g. a channel estimator), using whatever sampling/selection logic is currently installed in the program database.
- An **outer loop** that evolves the *search strategy itself* — the Python code deciding how solutions are sampled and combined — whenever progress on the inner loop stalls.

Solutions evolve inside the current database's logic, while that logic evolves across "switches." This is the literal meaning of co-evolution: both levels adapt, and each shapes what the other can discover next.

### Diagram

<div class="evox-diag">
<style>
  .evox-diag {
    --evox-bg: #f6f8fb; --evox-ink: #1e2b3c; --evox-ink-soft: #5b6b80; --evox-ink-faint: #a7b3c2;
    --evox-accent: #b8611f; --evox-accent-soft: #b8611f1c; --evox-store: #227368; --evox-store-soft: #2273681a;
    --evox-panel: #ffffff; --evox-line: #d3dce6;
    display: block; box-sizing: border-box; max-width: 1000px; margin: 28px 0;
    font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; color: var(--evox-ink);
  }
  @media (prefers-color-scheme: dark) {
    .evox-diag {
      --evox-bg: #0e1620; --evox-ink: #e7edf5; --evox-ink-soft: #9db0c4; --evox-ink-faint: #4d6076;
      --evox-accent: #eb9a51; --evox-accent-soft: #eb9a5124; --evox-store: #57d3c1; --evox-store-soft: #57d3c11c;
      --evox-panel: #141f2d; --evox-line: #263344;
    }
  }
  .evox-diag, .evox-diag * { box-sizing: border-box; }
  .evox-diag .evox-caption { margin: 0 0 14px; color: var(--evox-ink-soft); font-size: 14px; line-height: 1.55; max-width: 66ch; }
  .evox-diag .evox-legend {
    display: flex; flex-wrap: wrap; gap: 8px 20px;
    margin: 0 0 16px; padding: 10px 16px;
    border: 1px solid var(--evox-line); background: var(--evox-panel); font-size: 12.5px;
  }
  .evox-diag .evox-legend-item { display: flex; align-items: center; gap: 8px; color: var(--evox-ink-soft); }
  .evox-diag .evox-sw { width: 13px; height: 13px; border-radius: 2px; flex: none; display: inline-block; }
  .evox-diag .evox-sw.evox-llm { background: var(--evox-accent-soft); border: 1.5px solid var(--evox-accent); }
  .evox-diag .evox-sw.evox-logic { background: transparent; border: 1.5px solid var(--evox-ink-faint); }
  .evox-diag .evox-sw.evox-store { background: var(--evox-store-soft); border: 1.5px solid var(--evox-store); }
  .evox-diag .evox-sw.evox-bus { background: var(--evox-accent); border: none; height: 3px; align-self: center; }

  .evox-diag .evox-diagram-scroll {
    overflow-x: auto; overflow-y: hidden;
    border: 1px solid var(--evox-line); background: var(--evox-panel); padding: 8px 0;
  }
  .evox-diag .evox-canvas { position: relative; width: 960px; height: 1140px; }
  .evox-diag svg.evox-wires { position: absolute; top: 0; left: 0; overflow: visible; }

  .evox-diag .evox-node {
    position: absolute; border: 1.5px solid var(--evox-ink-faint);
    background: var(--evox-panel); padding: 7px 10px 20px; overflow: hidden;
  }
  .evox-diag .evox-node.evox-logic { border-color: var(--evox-ink-faint); border-style: dashed; }
  .evox-diag .evox-node.evox-llm { border-color: var(--evox-accent); background: linear-gradient(0deg, var(--evox-accent-soft), var(--evox-accent-soft)), var(--evox-panel); }
  .evox-diag .evox-node.evox-store { border-color: var(--evox-store); background: linear-gradient(0deg, var(--evox-store-soft), var(--evox-store-soft)), var(--evox-panel); }
  .evox-diag .evox-node.evox-highlight { border-width: 2.5px; }
  .evox-diag .evox-node .evox-tag {
    display: block; font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 8.5px; letter-spacing: 0.09em; text-transform: uppercase;
    color: var(--evox-ink-faint); margin-bottom: 3px;
  }
  .evox-diag .evox-node.evox-llm .evox-tag { color: var(--evox-accent); }
  .evox-diag .evox-node.evox-store .evox-tag { color: var(--evox-store); }
  .evox-diag .evox-node .evox-ttl { font-size: 12.5px; font-weight: 700; line-height: 1.22; margin-bottom: 3px; }
  .evox-diag .evox-node .evox-dsc { font-size: 10.2px; line-height: 1.32; color: var(--evox-ink-soft); }
  .evox-diag .evox-node .evox-detail {
    font-size: 9.7px; line-height: 1.38; color: var(--evox-ink-soft);
    margin-top: 6px; padding-top: 6px; border-top: 1px dotted var(--evox-line);
  }
  .evox-diag .evox-node .evox-detail b { color: var(--evox-ink); font-weight: 600; }
  .evox-diag .evox-node .evox-detail.evox-formula {
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 10px; color: var(--evox-ink); background: var(--evox-bg);
    padding: 5px 7px; margin-top: 6px; border: 1px dashed var(--evox-line); white-space: pre-line;
  }
  .evox-diag .evox-node .evox-cap {
    position: absolute; left: 10px; bottom: 5px; right: 10px;
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 8.5px; color: var(--evox-ink-faint); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .evox-diag .evox-rowlabel {
    position: absolute; font-family: ui-monospace, "SF Mono", Consolas, monospace;
    font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--evox-ink);
  }
  .evox-diag .evox-rowlabel span { color: var(--evox-ink-faint); text-transform: none; letter-spacing: 0; }
  .evox-diag .evox-term-label {
    position: absolute; font-size: 10px; color: var(--evox-ink-soft); text-align: center;
    font-family: ui-monospace, "SF Mono", Consolas, monospace;
  }
  .evox-diag .evox-stamp {
    margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--evox-line);
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px;
    font-size: 11px; color: var(--evox-ink-faint); font-family: ui-monospace, "SF Mono", Consolas, monospace;
  }
</style>

  <p class="evox-caption">Every box below is a real step in the loop — LLM inputs and both governing formulas are written directly inside the box where they apply. The thick dashed line on the far left is the one moment the strategy loop reaches back and rewrites the solution loop.</p>

  <div class="evox-legend">
    <div class="evox-legend-item"><span class="evox-sw evox-llm"></span>LLM call</div>
    <div class="evox-legend-item"><span class="evox-sw evox-logic"></span>Logic, no model</div>
    <div class="evox-legend-item"><span class="evox-sw evox-store"></span>Storage</div>
    <div class="evox-legend-item"><span class="evox-sw evox-bus"></span>the strategy-swap, Loop 2 → Loop 1</div>
  </div>

  <div class="evox-diagram-scroll">
    <div class="evox-canvas">
      <svg class="evox-wires" width="960" height="1140" viewBox="0 0 960 1140">
        <defs>
          <marker id="evox-a1" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="var(--evox-ink-soft)"></path>
          </marker>
          <marker id="evox-a2" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="var(--evox-accent)"></path>
          </marker>
        </defs>

        <line x1="250" y1="106" x2="250" y2="150" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>
        <circle cx="250" cy="100" r="4" fill="var(--evox-panel)" stroke="var(--evox-ink-soft)" stroke-width="1.5"></circle>

        <line x1="770" y1="110" x2="770" y2="150" stroke="var(--evox-ink-faint)" stroke-width="1.3" stroke-dasharray="2 3" marker-end="url(#evox-a1)"></line>

        <line x1="360" y1="196" x2="400" y2="196" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>
        <line x1="620" y1="196" x2="660" y2="196" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="770" y1="250" x2="770" y2="300" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="660" y1="346" x2="620" y2="346" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>
        <line x1="400" y1="346" x2="360" y2="346" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="250" y1="300" x2="250" y2="250" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="250" y1="470" x2="250" y2="520" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="250" y1="650" x2="250" y2="700" stroke="var(--evox-ink)" stroke-width="2" marker-end="url(#evox-a1)"></line>

        <line x1="360" y1="746" x2="400" y2="746" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>
        <line x1="620" y1="746" x2="660" y2="746" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="770" y1="890" x2="770" y2="940" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="660" y1="986" x2="620" y2="986" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>
        <line x1="400" y1="986" x2="360" y2="986" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <line x1="250" y1="940" x2="250" y2="890" stroke="var(--evox-ink-soft)" stroke-width="1.5" marker-end="url(#evox-a1)"></line>

        <polyline points="140,986 60,986 60,196 140,196" fill="none" stroke="var(--evox-accent)" stroke-width="2.25" stroke-dasharray="7 5" marker-end="url(#evox-a2)"></polyline>
        <text x="40" y="591" fill="var(--evox-accent)" font-size="11" font-family="ui-monospace, monospace" letter-spacing="0.08em" transform="rotate(-90 40 591)" text-anchor="middle">REWRITES LOOP 1 ↑</text>
      </svg>

      <div class="evox-term-label" style="left:150px; top:80px; width:200px;">your problem + evaluator.py</div>

      <div class="evox-rowlabel" style="left:140px; top:128px;">Loop 1 <span>— solution loop, every iteration</span></div>
      <div class="evox-rowlabel" style="left:140px; top:678px;">Loop 2 <span>— strategy loop, only when Loop 1 stalls</span></div>

      <div class="evox-node evox-llm" style="left:660px; top:10px; width:220px; height:100px;">
        <span class="evox-tag">LLM call · once, before iteration 1</span>
        <div class="evox-ttl" style="font-size:11.5px;">Write explore/refine guidance</div>
        <div class="evox-detail"><b>in →</b> your problem's system message + evaluator.py source + the list of packages available in the environment</div>
        <div class="evox-cap">generate_variation_operators()</div>
      </div>

      <div class="evox-node evox-store" style="left:140px; top:150px; width:220px; height:100px;">
        <span class="evox-tag">Storage</span>
        <div class="evox-ttl">Current search strategy</div>
        <div class="evox-dsc">today's rule for choosing what to try next</div>
        <div class="evox-cap">self.database</div>
      </div>
      <div class="evox-node evox-logic" style="left:400px; top:150px; width:220px; height:100px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Sample parent + examples</div>
        <div class="evox-dsc">asks the current strategy who to mutate next</div>
        <div class="evox-cap">database.sample()</div>
      </div>
      <div class="evox-node evox-logic" style="left:660px; top:150px; width:220px; height:100px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Write the prompt</div>
        <div class="evox-dsc">parent's code + examples + your problem</div>
        <div class="evox-cap">context_builder.build_prompt()</div>
      </div>

      <div class="evox-node evox-store" style="left:140px; top:300px; width:220px; height:170px;">
        <span class="evox-tag">Storage</span>
        <div class="evox-ttl">Save to database</div>
        <div class="evox-dsc">the candidate joins the pool for next time</div>
        <div class="evox-cap">database.add()</div>
      </div>
      <div class="evox-node evox-logic" style="left:400px; top:300px; width:220px; height:170px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Run it, score it</div>
        <div class="evox-dsc">executes the candidate, returns a score</div>
        <div class="evox-cap">evaluator.evaluate_program()</div>
      </div>
      <div class="evox-node evox-llm" style="left:660px; top:300px; width:220px; height:170px;">
        <span class="evox-tag">LLM call</span>
        <div class="evox-ttl">Generate a candidate</div>
        <div class="evox-dsc">reads the prompt, writes new code</div>
        <div class="evox-detail"><b>in →</b> parent's code + a few example candidates + your problem description + the parent's current metrics. Retrying after a failure? the exact error from last time is appended too.</div>
        <div class="evox-cap">self._call_llm() → self.llms</div>
      </div>

      <div class="evox-node evox-logic" style="left:140px; top:520px; width:220px; height:130px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl" style="font-size:11.5px;">Has progress stalled?</div>
        <div class="evox-dsc">pure arithmetic — no model asked</div>
        <div class="evox-detail evox-formula">stalled &#8660; &#916;(best score) &lt; 0.01
for switch_interval iters straight
(&#8776;10% of total, default)</div>
        <div class="evox-cap">_should_evolve_search() · No &#8594; continue, Yes &#8595; Loop 2</div>
      </div>

      <div class="evox-node evox-store" style="left:140px; top:700px; width:220px; height:190px;">
        <span class="evox-tag">Storage</span>
        <div class="evox-ttl">Strategy memory</div>
        <div class="evox-dsc">every strategy ever tried, plus its grade</div>
        <div class="evox-detail evox-formula">combined_score =
  improvement &#215; (1 + log(1+start_score))
  / &#8730;horizon</div>
        <div class="evox-detail">improvement = best-score gain while active &middot; start_score = best score when it took over &middot; horizon = iterations it ran</div>
        <div class="evox-cap">SearchStrategyDatabase</div>
      </div>
      <div class="evox-node evox-logic" style="left:400px; top:700px; width:220px; height:190px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Sample best strategy</div>
        <div class="evox-dsc">picks the best-graded strategy to refine</div>
        <div class="evox-cap">sample()</div>
      </div>
      <div class="evox-node evox-logic" style="left:660px; top:700px; width:220px; height:190px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Write the prompt</div>
        <div class="evox-dsc">best past strategy + 3 guide-model summaries:</div>
        <div class="evox-detail"><b>(a)</b> population stats &mdash; score trends / diversity <b>(b)</b> problem context &mdash; reads evaluator + system message, cached <b>(c)</b> batch summaries &mdash; the other past strategies shown as context</div>
        <div class="evox-cap">EvoxContextBuilder</div>
      </div>

      <div class="evox-node evox-store evox-highlight" style="left:140px; top:940px; width:220px; height:160px;">
        <span class="evox-tag">Storage</span>
        <div class="evox-ttl">Swap in the new strategy</div>
        <div class="evox-dsc">the one line the search strategy actually changes</div>
        <div class="evox-detail">&#8593; replaces "Current search strategy" at the top of Loop 1 &mdash; see the dashed line on the left. Graded afterward and remembered in Strategy memory.</div>
        <div class="evox-cap">self.database = new_db</div>
      </div>
      <div class="evox-node evox-logic" style="left:400px; top:940px; width:220px; height:160px;">
        <span class="evox-tag">Logic</span>
        <div class="evox-ttl">Validate &times;2</div>
        <div class="evox-dsc">fake data, then your real candidates.</div>
        <div class="evox-detail">Fails either test &#8594; discarded. Old strategy keeps running; tries again next time Loop 1 stalls.</div>
        <div class="evox-cap">search_strategy_evaluator.py</div>
      </div>
      <div class="evox-node evox-llm" style="left:660px; top:940px; width:220px; height:160px;">
        <span class="evox-tag">LLM call</span>
        <div class="evox-ttl">Write a new strategy</div>
        <div class="evox-dsc">writes a whole new database class, from scratch</div>
        <div class="evox-detail"><b>in &#8594;</b> best-graded past strategy's code + a few other strategies as context + the 3 summaries above + window stats (iterations so far, window size, stall threshold)</div>
        <div class="evox-cap">search_controller._call_llm()</div>
      </div>
    </div>
  </div>

  <div class="evox-stamp">
    <span>drawn from: skydiscover/search/evox/</span>
    <span>scroll right on small screens &middot; conceptual, not to scale</span>
  </div>
</div>

## The Solution Loop

Every iteration follows the same generic cycle, reused unchanged by every search algorithm in SkyDiscover: **sample a parent (and context programs) → build a prompt → the LLM generates a candidate → evaluate it → add it back to the database.** For EvoX, the database driving `sample()` starts as a default evolved-program database and is replaced over the course of a run by the meta-evolution process described below.

## Meta-Evolution of the Search Strategy

When the best score stagnates (improvement below a small threshold) for a run of iterations — by default about 10% of the total iteration budget — EvoX triggers a strategy switch:

1. It scores the just-used search algorithm based on how much improvement it achieved, weighted by how long it had to work.
2. It asks an LLM to generate an entirely new database class implementing the sampling/selection logic — effectively a new search algorithm, written in Python.
3. The new database is validated before being trusted.
4. All existing solution programs and their prompt history are migrated into the new database, which is hot-swapped in as the active search strategy.

If the newly generated database throws an error at runtime, EvoX falls back to the previous database and keeps any new solutions found in the meantime. The database of past search-strategy attempts is itself evolved across switches, so the meta-evolution process learns from which strategies worked.

## Explore vs Exploit

There's no single global explore/exploit knob — the tradeoff is decided *inside whatever sampling code the LLM currently has installed*. At the start of a run, EvoX generates two problem-specific labels — one for "explore" (try a fundamentally different approach) and one for "exploit" (refine within the current approach) — and it's up to each generated database's `sample()` method to decide, per iteration, which label to attach to the parent it selects (typically based on how long the run has been stagnating). That label then surfaces directly in the next prompt as guidance attached to the current solution.

## Prompt Context

Each iteration's prompt is assembled from several pieces:

- **Metrics & focus areas** — the parent's current score, a per-metric breakdown, and heuristics about whether the score is trending up or down.
- **Previous attempts** — a handful of recent programs with what changed, their metrics, and whether each was an improvement, a regression, or a no-op.
- **Other context programs** — other strong/elite programs from the database, shown with their metrics and full code, plus recent failed attempts (with the LLM's response or a traceback) so the model can avoid repeating mistakes.
- **Current program** — the parent's code, its score breakdown, and any evaluator feedback (`artifacts`) it returned.
- **Task/response-format instructions** — whether to reply with a diff, a full rewrite, or a from-scratch solution.

At the meta-evolution level, EvoX additionally injects a summary of the population's current state and a batch summary of prior search strategies and how well they scored, so the LLM proposing new search strategies can see what's already been tried.

## Checkpointing & Resuming

Every run periodically checkpoints the full program database — all candidate programs, their prompt history, and the current best program — to a `checkpoints/checkpoint_<iteration>/` directory, alongside a `best_program` file and `best_program_info.json` with its metrics. Checkpointing happens on a configurable interval and always at the end of a run.

Resuming is CLI/API-only (there's no config-file equivalent): pass `--checkpoint <path>` to `skydiscover-run`, and the run restores the database and continues from the next iteration after the checkpoint. Completed runs can also be replayed visually with `skydiscover-viewer /path/to/checkpoints/checkpoint_100`.
