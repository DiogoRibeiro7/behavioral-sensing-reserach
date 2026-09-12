# Sensor Modeling Research Toolkit 0.3.0

`0.3.0` moves the project from simulator-only evaluation to an externally tested behavioural-sensing research pipeline while keeping the model interpretable and the evidence boundaries explicit.

## What is new

- Added public CASAS dataset adapters and evaluation utilities for annotated smart-home recordings.
- Added an optional circadian state-dynamics profile to the continuous-time behavioural prior.
- Added fixed-lag smoothing for offline evaluation and reporting.
- Added utilities for measuring and fitting emission rates from annotated recordings.
- Added typed sensor-ingestion exceptions using `DataExcept` while preserving legacy `ValueError` and `ImportError` catch behaviour.
- Added frozen external-validation machinery, cohort provenance, one-shot scoring controls, and line-ending-safe digest verification for tracked freeze artifacts.
- Added uncertainty diagnostics separating confidence, posterior margin, entropy, interval-level evidence strength, and per-update information gain without changing the abstention rule.

## External validation

The `0.3.0` candidate was frozen before primary external scoring as `v0.2` inference plus the optional circadian profile, with all other inference choices retained.

The primary test used 43 single-resident CASAS homes outside the development panel. The pre-specified primary estimand was the median paired household difference in balanced accuracy between the candidate and the `v0.2` baseline.

The one-shot result was:

- median paired balanced-accuracy difference: **+0.0091**;
- 95% household bootstrap interval: **[+0.0054, +0.0117]**;
- **37 of 43 homes improved**;
- 6 worsened;
- none were unchanged or unscoreable.

Secondary metrics moved in the same direction: balanced accuracy increased from approximately 0.496 to 0.504, calibration error decreased from 0.343 to 0.328, Brier score decreased from 0.842 to 0.812, and log loss decreased from 4.302 to 4.168.

The result establishes that the frozen circadian prior transfers under the stated CASAS motion/door instrumentation and evaluation contract. It does **not** establish clinical effectiveness, general smart-home performance, or equivalence to the simulator deployment.

## What the real-data work changed

The project now distinguishes simulator performance from what the same sensing problem supports on real recordings.

Across the 22-home development panel, the pipeline reaches a median balanced accuracy of about 0.420. A supervised diagnostic classifier using the same sensor information, together with time of day and recent history, reaches about 0.607. The bundled simulator reports about 0.816, so its figures should not be interpreted as expected field performance.

The real-data work also identified a central negative result: the current abstention mechanism does not provide reliable evidence about when the model is wrong. On real recordings, confidence only weakly separates correct from incorrect predictions and becomes less reliable in the highest-confidence band. In the frozen confirmatory simulation, abstention remains effectively silent even as missingness rises substantially.

Controlled quiet-period diagnostics narrow the mechanism. The transition prior alone remains near the stationary posterior; extreme confidence appears when complementary Poisson silence likelihoods from working room-motion and entrance-door streams accumulate under the persistent dynamics. Version `0.3.0` exposes this rather than hiding it: `StateEstimate` now includes optional per-update information gain,

\[
D_{\mathrm{KL}}\!\left(p_t\,\|\,p_{t|t-1}\right),
\]

as a passive diagnostic of how much the current interval moved the predicted belief. It does **not** enter abstention or add a new threshold.

That negative abstention result remains open in `0.3.0`; it is not hidden by the successful circadian transfer result.

## Compatibility

The circadian profile is optional and off by default, so existing inference behaviour remains available when it is not configured.

The new ingestion exceptions retain compatibility with broad catches used by earlier callers: sensor loading, format, validation, and missing-data errors continue to be catchable as `ValueError`, while dependency failures remain catchable as `ImportError`.

The new `StateEstimate.information_gain` field is optional. Manually constructed estimates remain compatible and receive `None` unless an update-level information gain is supplied.

## Archive status

The project concept DOI remains `10.5281/zenodo.21337272`.

A `0.3.0` version DOI must not be recorded until Zenodo has actually archived the GitHub release. If Zenodo is unavailable at release time, archival publication remains pending and must be synchronized afterwards rather than represented with a fabricated DOI.

## Scope

This is research software, not a medical device. No diagnosis, prognosis, or clinical-effectiveness claim is made or supported by this release.
