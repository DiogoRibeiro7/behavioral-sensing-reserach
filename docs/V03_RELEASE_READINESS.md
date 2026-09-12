# v0.3.0 Release Readiness

This document is the release-candidate record for `v0.3.0`. It separates the completed research result from the remaining publication steps so that a successful validation result cannot be mistaken for an already-published package version.

## Candidate status

**Research result complete; release ancestry reconciled; release metadata prepared for 0.3.0.**

The frozen primary external validation was executed once on 2026-09-04 against the pre-specified 43-home cohort and evaluation grid. The primary estimand was the median paired household difference in balanced accuracy,

\[
D_h = BA_h(v0.3) - BA_h(v0.2).
\]

The observed median difference was **+0.0091**, with a 95% household bootstrap interval of **[+0.0054, +0.0117]**. Thirty-seven of 43 homes improved, six worsened, none were unchanged, and none were unscoreable. The result is recorded in `artifacts/v03/external_primary_result.json`; `artifacts/v03/external_primary_scored.json` binds the one-shot run to the stored result artifact.

This establishes transfer of the frozen circadian candidate under the scope defined by the external-validation contract. It does not establish clinical effectiveness, general smart-home performance, or equivalence to the simulator deployment.

## Why this is a minor release

`v0.3.0` is not only a documentation release. Since `v0.2.0`, the package has accumulated new public behaviour and research-facing capability, including:

- real CASAS dataset adapters and evaluation utilities;
- the optional circadian state-dynamics profile;
- fixed-lag smoothing utilities for offline evaluation and reporting;
- measured emission-rate utilities;
- structured `DataExcept` ingestion errors while preserving legacy broad catches;
- frozen external-validation machinery, provenance records, and scored result;
- line-ending-safe digest verification for git-tracked freeze artifacts;
- real-data uncertainty diagnostics, including per-update information gain.

The final release metadata now reports `0.3.0` with intended publication date `2026-09-12`. The concept DOI remains `10.5281/zenodo.21337272`; no `0.3.0` version DOI is recorded before Zenodo actually mints one.

## Resolved release preparation

The release candidate now has:

- `pyproject.toml` at `0.3.0` with `bumpversion.current_version = 0.3.0`;
- `sensor_modeling/__init__.py` at `0.3.0`;
- `CITATION.cff` at `0.3.0` with release date `2026-09-12`;
- `.zenodo.json` at `0.3.0`, dated `2026-09-12`, with `isNewVersionOf` pointing to the archived `0.2.0` DOI `10.5281/zenodo.22171268`;
- README version/citation text at `0.3.0`, with stale simulator-only and four-seed claims removed;
- `CHANGELOG.md` closed under `## [0.3.0] - 2026-09-12` with a fresh empty `Unreleased` section;
- `RELEASE_NOTES_0.3.0.md` updated with the frozen external-validation result and uncertainty diagnostics.

The earlier branch-ancestry blocker was already resolved by the no-content ancestry merge at `7652668f49aaa554a9c162baa8073c4047e14a34`, after which `main` became an ancestor of `develop`.

## Remaining gate

The repository preparation is complete. The remaining software-release gate is mechanical:

1. `pytest tests/test_project_metadata.py` must pass on the exact release-candidate head.
2. The full hosted CI `all checks passed` gate must be green on that exact head.
3. The release candidate must be merged into `develop`.
4. The resulting `develop` release state must be merged to `main`.
5. The `v0.3.0` tag must be created from the resulting `main` commit, never from `develop`.
6. The GitHub release must be created from that tag using `RELEASE_NOTES_0.3.0.md`.

Zenodo availability is a publication dependency, not a software-readiness criterion. If it is unavailable when the GitHub release is published, archival publication remains pending. Do not invent or pre-fill a version DOI.

## What remains scientifically open

The successful circadian transfer result does not repair abstention.

Real-data diagnostics show stated confidence is only weakly related to correctness and becomes less reliable in the highest-confidence band. Controlled quiet-period tests further show that the transition prior alone does not create extreme certainty: complementary Poisson silence likelihoods from working room-motion and entrance-door streams accumulate under the persistent dynamics and can drive `sleeping` confidence above 0.95.

Version `0.3.0` therefore exposes more uncertainty information rather than claiming a solved safety rule. `StateEstimate.information_gain` records

\[
D_{\mathrm{KL}}\!\left(p_t\,\|\,p_{t|t-1}\right)
\]

as a passive diagnostic and does not enter abstention.

## After publication

After the GitHub release and Zenodo archive exist:

- verify the new Zenodo version DOI and record URL;
- add the `0.3.0` row to `ZENODO.md`;
- add the minted version DOI to citation metadata without replacing the concept DOI as the preferred citation target;
- merge `main` back into `develop` according to `RELEASE.md`;
- continue the uncertainty work from the synchronized post-release branch.
