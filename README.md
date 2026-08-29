# Nordic Berry Optimizer

A deterministic recipe optimizer for a 250 g Nordic berry drink. It maps four
user-selected nutrient-emphasis sliders to a target vector, searches within
the fixed ingredient and mass constraints, and independently verifies the
resulting recipe.

This project makes no medical, treatment, or cognitive-performance claims.
Names such as “Genius” and “Fit” are labels for nutrient emphasis only.

## Run

Python 3 standard library only; no installation is required.

```bash
python3 -m src.cli --data 100 --liquid-base water
python3 -m unittest discover -s tests
```

`--power-mode` raises the Sugar target only when Fit is at least 50.
`--stimulant-boost` is rejected when Cute is 80 or above. Guarana caffeine
uses the documented project estimate of approximately 47 mg/g, not a
laboratory-verified measurement.

## Method

Nutrient table values are the locked Fineli data in `data/nutrients.json`.
The antioxidant figure is a project-specific equal-weight proxy constructed
from normalized VitC, VitE, and VitK values; it is not a biological potency
model. Recipe antioxidant score is the berry-mass-weighted ingredient score.

The optimizer is dependency-free and deterministic. It jointly searches the
five berry amounts and guarana amount, derives the remaining liquid mass, and
evaluates NNTD with the same fixed data. Verification independently recomputes
all totals and checks mass, ingredient bounds, liquid, caffeine, and safety
rules. Floating-point mass comparisons use a documented `1e-9 g` arithmetic
tolerance only.

## Evaluation

`tests/frozen_eval.py` contains the unchanged 14-case frozen evaluation set
and a harness for TASK 3. It has no import-time side effects. Baseline output
is intentionally parsed and scored by the same verifier as agent output.
