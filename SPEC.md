# Nordic Berry Optimizer — v1.0 Mathematical Specification

Status: **LOCKED v1.0-rev6**. No further mathematical changes permitted
before implementation. This document is the ground truth for the Codex
build task. Do not modify nutrient data or core formulas without
updating this file and re-running the frozen evaluation set.

**Revision note (pre-implementation, still before any code was written):**
this is v1.0-rev6. Fixes vs. rev1 (first draft): normalized the
slider→target formula to prevent unbounded overflow with multiple high
sliders (§5); made caffeine a separate objective with its own target/range
so Stimulant Boost actually does something measurable (§6, §7); made
liquid_base a fixed per-case input rather than an ambiguous optimizer
decision (§6, §11); gave Na an explicit dimension_scale so it behaves
correctly inside NNTD (§5, §9); simplified the antioxidant proxy to an
unweighted mean, removing an unjustifiable coefficient (§2); fixed the
mass balance to include guarana grams (§3); added an explicit
all-zero-slider validation step (§5, §8); raised the Cute/Stimulant
reject threshold from 100 to ≥80 with a boundary test (§6, §11).
Fixes vs. rev2: `target[Na]` changed from a fixed 0 mg to a
`liquid_base`-dependent value (0 mg water / 25 mg mineral_water), because
a fixed zero target made mineral_water strictly worse for NNTD in every
case, defeating the entire electrolyte-tradeoff rationale for introducing
it (§5); Na excluded from the unreachable-dimension report since its
target is a consequence of `liquid_base`, not a user goal (§8).
**Fixes vs. rev3 (found by Codex's first read-only TASK 1 review):** §7
still referenced the old "fixed-zero Na target" wording after the rev3
fix — corrected to point at §5's liquid_base-dependent target; the
recipe-level antioxidant aggregation formula was entirely missing from
rev3 — added as a mass-weighted average over berries used, with a
zero-berry edge case (§2); §7 now explicitly forbids treating guarana as
a variable fixed before a separate berry optimization — berries and
guarana must be optimized jointly; the stimulant objective was
restructured into an explicit lexicographic order — `50 ≤ caffeine ≤ 200`
is a hard feasibility constraint, with `|caffeine - 100|` minimized only
as a tie-break.
**Fixes vs. rev4 (found by Codex's second read-only review of the rev4
text):** (1) caffeine below 50 mg was ambiguous between "verifier fixes
it" and "verifier flags it" — resolved by making the verifier a pure
classifier that never modifies a recipe: `<50mg` → WARN +
`invalid_for_boost` flag, `>200mg` → REJECT as an optimizer bug, never a
"reduce and recompute" (§8.4); (2) the "near-equal NNTD" tie-break had no
defined tolerance — fixed at `≤ 1e-9` for a fully deterministic outcome
(§7); (3) Stimulant Boost's slider eligibility (originally "Data Expert,
Fit only") directly contradicted frozen eval case §11.10, which tests
Genius + Stimulant Boost — expanded eligibility to include Genius rather
than alter a frozen case (§6); (4) liquid `< 40g` had the same
verifier-tries-to-fix-it problem as the caffeine case — resolved
identically: this must hold by construction via the optimizer's own
constraint (§7), and the verifier only checks and rejects on violation,
treating it as an internal error rather than something to repair (§3,
§8.3). This full revision history (rev1 → rev5, including two
independent read-only agent review passes before any implementation)
is itself strong material for the Improvement Changelog deliverable —
it demonstrates disciplined, structured iteration on the specification
driven by review from multiple angles, not trial and error against the
eval set.

## 1. Purpose statement (no health claims)

This tool optimizes a berry drink recipe toward a **user-defined nutrient
target profile**. It does not diagnose, treat, or claim any medical or
cognitive effect. Slider names ("Genius", "Fit", etc.) describe the
*nutrient emphasis* of the target profile, not a promised outcome. This
framing must be preserved in all UI text, README, and video narration.

## 2. Ingredients and nutrient reference data

Source: THL Fineli National Food Composition Database (accessed 28 Aug 2026).
All values per 100 g edible portion. This table is fixed ground truth —
the agent must not alter these numbers.

| Ingredient (Fineli id)      | kcal | Sugar g | Fiber g | VitC mg | VitE mg | VitK ug | K mg | Ca mg | Mg mg | Na mg |
|------------------------------|------|---------|---------|---------|---------|---------|------|-------|-------|-------|
| Blueberry (442)              | 64.5 | 8.39    | 3.30    | 7.16    | 1.85    | 9.00    | 110  | 19    | 9     | 2.0   |
| Lingonberry                  | 48.8 | 8.17    | 2.60    | 10.70   | 1.53    | 9.00    | 80   | 22    | 9     | 2.0   |
| Cloudberry                   | 55.0 | 5.81    | 6.30    | 61.60   | 2.95    | 9.00    | 170  | 16    | 29    | 2.0   |
| Redcurrant                   | 56.6 | 7.50    | 5.00    | 30.00   | 0.82    | 11.00   | 310  | 40    | 14    | 0.6   |
| Blackcurrant                 | 74.1 | 8.58    | 5.80    | 128.00  | 2.23    | 30.00   | 340  | 72    | 24    | 2.0   |
| Mineral water (915)          | 0    | 0       | 0       | 0       | 0       | 0       | 13.5 | 4.7   | 7.23  | 45.0  |
| Plain water                  | 0    | 0       | 0       | 0       | 0       | 0       | 0    | 0     | 0     | 0     |

**Stimulant add-in (guarana powder):** ~47 mg caffeine/g, based on the
average of a 3.6–5.8% caffeine-by-weight range reported across three
independent sources (caffeineinformer.com, cornercoffeestore.com,
news-medical.net, all retrieved 28 Aug 2026). Documented in README as an
estimate, not a laboratory-verified value.

**Antioxidant proxy:** `antioxidant_score` = mean of three independently
min-max normalized (0–1 across the 5 berries) Fineli values: VitC, VitE,
VitK. Equal weighting — no arbitrary multiplier to justify. Uses **only
sourced data**, no invented index. Documented explicitly as "a
project-specific proxy built from published vitamin data with equal
weighting across three vitamins; an engineering construction for
optimization, not a biological antioxidant potency model."

**Recipe-level antioxidant aggregation (this was underspecified in rev3
— now fixed):** the per-berry `antioxidant_score` values above describe
individual ingredients. The *achieved* antioxidant score for a finished
recipe is the **mass-weighted average across the berries actually used**:

`recipe_antioxidant_score = Σ(berry_g[i] × antioxidant_score[i]) / Σ(berry_g[i])`

Liquid (water or mineral_water) has no antioxidant score and is excluded
from this calculation — the score describes the composition of the
berry component, not dilution by liquid. **Edge case:** if
`Σ(berry_g) == 0` (a recipe with no berries at all — should be rare
given the 6 berry-driven target dimensions, but must be handled),
`recipe_antioxidant_score = 0` by definition.

## 3. Serving size and mass model

- Standard serving: **250 g total** (approximation: 1 g ≈ 1 ml for both
  berries and liquid, stated explicitly as a simplification in the README).
- Mass balance (must hold exactly): `Σ(berry_g) + guarana_g + liquid_g = 250`.
- Berry mass per ingredient: bounded **0–80 g** per serving (realistic
  handful-scale amounts).
- Liquid is the balancing term: `liquid_g = 250 - Σ(berry_g) - guarana_g`.
  Must be **≥ 40 g**. This is a **hard constraint the optimizer enforces
  during search** (§7) — it must never propose a candidate violating it.
  Verification (§8) only checks that the constraint holds in the final
  output; it does not attempt to repair a violation.

## 4. Target vector dimensions (7)

`[VitC, K, Mg, Ca, Na, Sugar, antioxidant_score]`

## 5. Slider → target weight matrix

**Input validation (before target-building):** if `Data + Genius + Fit +
Cute == 0`, reject the input with a clear validation error ("select at
least one goal") rather than proceeding — this also prevents division by
zero in the step below.

**Normalization:** `slider_sum = Data + Genius + Fit + Cute` (guaranteed
> 0 past validation). `normalized_slider[s] = slider[s] / slider_sum`.

**Target formula** for each nutrient dimension *d* (VitC, K, Mg, Ca,
Sugar, antioxidant — Na handled separately below):

`target[d] = dimension_scale[d] × Σ_s (normalized_slider[s] × weight[s][d])`

Because `normalized_slider` values sum to 1 and each `weight[s][d] ≤ 1`,
this keeps `target[d] ≤ dimension_scale[d]` under normal slider input.
**Exception:** Power Mode (§6) multiplies the Sugar target by 1.40
*after* this formula, which can legitimately push `target[Sugar]` above
`dimension_scale[Sugar]`. This is intentional — see §6 and the note on
`dimension_scale` below.

| Weight            | VitC | K   | Mg  | Ca  | Sugar | antioxidant |
|--------------------|------|-----|-----|-----|-------|-------------|
| Data Expert        | 0.3  | 0.9 | 0.9 | 0.2 | 0.1   | 0.4         |
| Genius             | 0.6  | 0.3 | 0.3 | 0.2 | 0.1   | 0.9         |
| Fit                | 0.3  | 0.9 | 0.9 | 0.2 | 0.6   | 0.2         |
| Cute               | 0.4  | 0.1 | 0.1 | 0.1 | 0.8   | 0.2         |

**dimension_scale** — a normalization constant used to convert weighted
sums into absolute units and to normalize NNTD deviations (§9). It is
**not** a nutritional safety threshold and **not always a hard target
ceiling** (see Power Mode exception above and Na below):

VitC=150mg, K=350mg, Mg=35mg, Ca=60mg, Sugar=25g, antioxidant=1.0
(already 0–1), **Na=100mg** (approx. max achievable Na per serving if
liquid were entirely mineral_water at max liquid volume).

**Na target depends on `liquid_base`, not on sliders directly:**
`target[Na] = 0 mg` when `liquid_base = water`; `target[Na] = 25 mg` when
`liquid_base = mineral_water`. This makes the trade-off genuine rather
than one-directional: choosing `mineral_water` sets a small non-zero
electrolyte target that the achieved Na can actually satisfy, while any
Na *beyond* that target still increases `deviation_Na` — so the optimizer
has a real reason to prefer `mineral_water` for Data Expert/Fit cases
(where K/Mg targets are high and mineral_water helps reach them), without
that choice being penalized outright by the Na term. Choosing
`mineral_water` for a low-electrolyte profile (e.g. Cute) still costs
more on Na than `water` would, since 25 mg target is far below what a
full mineral_water liquid volume actually contributes.

## 6. Toggles

- **Power Mode** (Fit only): `target[Sugar] *= 1.40`, applied *after* the
  §5 formula. Not clipped back down to `dimension_scale[Sugar]` — the
  optimizer should genuinely lean harder on blackcurrant/blueberry (the
  two highest-sugar sourced berries) to chase the raised target, and NNTD
  will simply reflect how close it got. No-op with a warning if Fit < 50
  (Power Mode without a Fit emphasis is not a meaningful combination).

- **Stimulant Boost** (Data Expert, Fit, **and Genius** — see reject rule
  below; expanded from the rev4 wording to match frozen eval case #11.10,
  which already tests Genius + Stimulant Boost and must remain valid):
  when ON, `50 ≤ caffeine ≤ 200 mg` is a **hard feasibility constraint**
  on the optimizer (§7) — not an optional secondary objective, and not
  something the optimizer can satisfy with zero guarana. Within feasible
  recipes, the optimizer pulls toward `caffeine_target = 100 mg` as a
  tie-break (§7). `hard_safety_max = 200 mg` (EFSA single-dose guidance)
  is enforced independently at verification time too (§8) as a final
  guard. Optimizer adds 0–4.2 g guarana powder (~47 mg caffeine/g, §2)
  to reach this. **Hard REJECT if requested with `Cute ≥ 80`** (raised
  from the original `Cute = 100` threshold — 80 gives a cleaner, more
  defensible "kid-friendly zone" boundary; see the boundary test in §11).

- **liquid_base**: `water` | `mineral_water`. User-selected input, fixed
  per case (not an optimizer decision variable — see the frozen
  evaluation set in §11, where cases 1 and 6 hold sliders identical and
  vary only this field for a clean before/after comparison). Default
  `water`. If `mineral_water` selected with `Cute ≥ 80`, emit a soft
  WARNING (sodium contribution noted in output), not a hard reject —
  sodium is a materially lower acute risk than caffeine.

## 7. Optimizer

Constrained search over `(berry grams × 5, guarana grams)` — `liquid_g`
is always derived from the mass balance in §3, never a free variable.
**These are jointly optimized decision variables, not a two-stage
process.** Do not fix guarana first and then solve berries separately
(or vice versa): guarana displaces mass from the 250 g total, and when
`liquid_base = mineral_water` the liquid itself carries K/Ca/Mg/Na, so
guarana's amount can genuinely interact with how much liquid — and
therefore how much mineral content — remains available. A sequential
"fix guarana, then optimize berries" approach is a simplification that
is not equivalent to the joint problem and must not be used.

**Objectives, in order (lexicographic):**

*When Stimulant Boost is OFF:*
1. Minimize NNTD (§9) over the 6 slider-driven dimensions (VitC, K, Mg,
   Ca, Sugar, antioxidant) plus the `liquid_base`-dependent Na target
   defined in §5.

*When Stimulant Boost is ON:*
1. **Hard feasibility constraint** (not merely an objective): achieved
   caffeine must satisfy `50 ≤ caffeine ≤ 200` mg. Only recipes meeting
   this are considered valid candidates — a recipe with `caffeine = 0`
   is infeasible when Stimulant Boost is ON, not just suboptimal. This
   prevents the optimizer from ever "satisfying" Stimulant Boost with
   zero guarana.
2. Among feasible candidates, minimize NNTD (as above).
3. Tie-break: two candidates are considered **near-equal** if
   `|NNTD_a - NNTD_b| ≤ 1e-9` (a tight, essentially-exact-tie threshold —
   appropriate since the deterministic search in §7 is expected to
   produce exact or near-exact ties between discrete candidates, not
   near-misses that should be conflated). Among near-equal candidates,
   minimize `|caffeine - 100|` (pull toward the 100 mg target from §6).

Exact algorithm choice (constrained least-squares, heuristic search, a
small custom deterministic solver, etc.) is Codex's implementation task —
this spec fixes objectives, constraints, and their priority order, not
the solver. Prefer a solution with minimal external dependencies if it
doesn't compromise correctness or reproducibility in a clean-environment
context — but correctness of the constraint ordering above takes
priority over dependency minimalism.

## 8. Verification (deterministic, non-LLM)

0. **Input validation** (before any computation): reject if
   `Data + Genius + Fit + Cute == 0` (§5); reject if `Stimulant Boost`
   requested with `Cute ≥ 80` (§6, checked here as well as pre-optimization
   to fail fast).
1. Recompute nutrient totals from final ingredient amounts (independent of
   optimizer's own accounting) — never trust the optimizer's self-reported
   totals.
2. Mass balance: `Σ(berry_g) + guarana_g + liquid_g == 250` (§3) →
   else REJECT (internal error, should be impossible if optimizer respects
   constraints).
3. Liquid ≥ 40 g → this must already hold by construction, since the
   optimizer (§7) treats it as a hard constraint during search, never as
   something to fix afterward. If verification ever observes
   `liquid_g < 40`, this indicates the optimizer violated its own
   constraints — **REJECT as an internal error** (same category as a
   mass-balance failure in step 2), not something the verifier attempts
   to repair. The verifier classifies; it does not re-optimize.
4. Caffeine (only meaningful when Stimulant Boost is ON): the verifier
   classifies, it does not adjust guarana or recompute anything.
   - `50 ≤ caffeine ≤ 200 mg` → PASS.
   - `caffeine > 200 mg` → **REJECT — hard safety violation.** This
     should be impossible if the optimizer respects the §7 feasibility
     constraint; if it happens, it is an optimizer bug, not something
     verification silently corrects.
   - `caffeine < 50 mg` → **WARN**, not a reject: the overall recipe may
     still be nutritionally valid, but it is flagged as
     `invalid_for_boost = true` in the report, meaning it does not count
     as having satisfied the Stimulant Boost requirement for evaluation
     purposes (§9, §11).
5. Cute + Stimulant Boost (`Cute ≥ 80`) → REJECT with explicit reason
   (redundant with step 0, kept here as a final guard).
6. Cute ≥ 80 + mineral_water → WARN, do not block.
7. Report which of the 6 **user-driven** dimensions (VitC, K, Mg, Ca,
   Sugar, antioxidant) were unreachable within ingredient bounds, if any
   (e.g. target exceeds what 5×80g berries could ever supply). **Na is
   excluded from this report** — its target is a consequence of the
   `liquid_base` choice (§5), not a user goal, so an "unreachable sodium
   target" message would be confusing and meaningless to the user.

## 9. Metric — Normalized Nutrient Target Deviation (NNTD)

For each of the 7 dimensions *d* (VitC, K, Mg, Ca, Na, Sugar, antioxidant):
`deviation_d = |achieved_d - target_d| / dimension_scale[d]`
`NNTD = mean(deviation_d)` across all 7 dimensions. Lower is better.
`target[Na]` is 0 mg (water) or 25 mg (mineral_water) per §5, not
slider-driven — so `deviation_Na` reflects both "no unwanted sodium" and
"mineral_water's electrolyte target roughly met," not a pure penalty.

Caffeine is **not** included in NNTD (§6, §7) — reported separately as
`caffeine_achieved_mg`, `caffeine_in_range` (bool, PASS per §8.4), and
`invalid_for_boost` (bool, set by the `< 50 mg` WARN case in §8.4), only
when Stimulant Boost is applicable.

**Report per-dimension deviation, not just the aggregate NNTD**, for both
baseline and agent, across all frozen cases (§11) — this makes the
before/after evidence far more concrete than a single number.

Secondary reported metrics: valid recipes / total, safety violations
(§8.4 REJECT), invalid-for-boost count (§8.4 WARN), Cute+Stimulant
violations correctly rejected, unreachable targets flagged.

## 10. Baseline definition (frozen prompt)

Baseline = single call to the same LLM used elsewhere in the project, with
this exact system-free prompt and no tools:

> "Suggest a berry drink recipe using any of blueberry, lingonberry,
> cloudberry, redcurrant, blackcurrant, water, and mineral water. The
> drink should emphasize: Data Expert {x}%, Genius {y}%, Fit {z}%, Cute
> {w}%. Power Mode: {on/off}. Stimulant Boost: {on/off}. Liquid base:
> {water/mineral_water}. Give exact grams of each ingredient for a 250g
> serving."

`liquid_base` is an exclusive v1 choice: `water` means the
derived liquid portion is water, and `mineral_water` means it is mineral
water. Mixing water and mineral water, including a mineral-water fraction, is
outside v1 scope and may be considered future work.

Baseline output is parsed and scored with the same verification and NNTD
code as the agent — same inputs, same evaluation, no nutrient tools
available to the baseline.

## 11. Frozen evaluation set (14 cases)

1. Data Expert=100, others=0, water
2. Genius=100, others=0, water
3. Fit=100, others=0, water
4. Cute=100, others=0, water
5. Balanced 25/25/25/25, water
6. Data Expert=100, mineral_water (paired with #1 for before/after demo)
7. Fit=100 + Power Mode, water
8. Fit=100 + Power Mode + Stimulant Boost, mineral_water
9. Data Expert=100 + Stimulant Boost, water
10. Genius=100 + Stimulant Boost (edge: allowed slider but low relevance)
11. Cute=100 + Stimulant Boost → expect REJECT
12. Cute=100 + mineral_water → expect WARN, not reject
13. All sliders=100 + Power + Stimulant + mineral_water → stress test
14. Cute=79, Data Expert=21, Stimulant Boost=ON → expect ALLOWED
    (boundary test just below the Cute≥80 reject threshold in §6/§8)

This set is frozen before implementation. Do not add/remove cases after
seeing results, to keep the baseline-vs-agent comparison honest.

**v1.0-rev6 pre-evaluation correction:** before any frozen evaluation result
was observed, the baseline protocol was amended to communicate each case's
selected `liquid_base` explicitly in the baseline prompt. This is an
input-parity correction; it does not change the frozen cases, optimization
semantics, target construction, nutrient data, constraints, verifier, or NNTD.
