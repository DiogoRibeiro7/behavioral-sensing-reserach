# v0.3.0 Release Readiness

This document is the release-candidate record for `v0.3.0`. It separates the completed research result from the still-pending software release steps so that a successful external validation cannot be mistaken for an already-published package version.

## Candidate status

**Research result complete; software release not yet prepared.**

The frozen primary external validation was executed once on 2026-09-04 against the pre-specified 43-home cohort and evaluation grid. The primary estimand was the median paired household difference in balanced accuracy,

\[
D_h = BA_h(v0.3) - BA_h(v0.2).
\]

The observed median difference was **+0.0091**, with a 95% household bootstrap interval of **[+0.0054, +0.0117]**. Thirty-seven of 43 homes improved, six worsened, none were unchanged, and none were unscoreable. The result is recorded in `artifacts/v03/external_primary_result.json`; `artifacts/v03/external_primary_scored.json` binds the one-shot run to the stored result artifact.

This establishes transfer of the frozen circadian candidate under the scope defined by the external-validation contract. It does not establish clinical effectiveness, general smart-home performance, or equivalence to the simulator deployment.

## Why this is a minor release

`v0.3.0` is not only a documentation release. Since `v0.2.0`, `develop` has accumulated new public behaviour and research-facing capability, including:

- real CASAS dataset adapters and evaluation utilities;
- the optional circadian state-dynamics profile;
- fixed-lag smoothing utilities for offline evaluation and reporting;
- measured emission-rate utilities;
- structured `DataExcept` ingestion errors while preserving legacy broad catches;
- the frozen external-validation machinery, provenance records, and scored result;
- shared line-ending-safe digest verification for git-tracked freeze artifacts.

The public package metadata nevertheless still reports `0.2.0`. A minor version bump is therefore required before any release from `main`.

## Current blockers

### 1. Release metadata still says 0.2.0

The following release-facing files must be changed together and validated by `tests/test_project_metadata.py`:

- `pyproject.toml`;
- `sensor_modeling/__init__.py`;
- `CITATION.cff`;
- `.zenodo.json`;
- the README citation block.

The intended version is `0.3.0`. The release date must be the actual publication date, not the date the external scoring was executed.

### 2. Changelog is still Unreleased

The existing `Unreleased` material describes the work that belongs to `0.3.0`. Before release, it must be closed under a dated `## [0.3.0]` heading and a fresh empty `Unreleased` section must be started.

The external validation outcome itself must also be represented in that release entry; otherwise the package would ship the candidate mechanism without recording the result that motivated the release line.

### 3. `develop` and `main` have diverged

At the time this record was created, `develop` is 232 commits ahead of `main`, while `main` contains one commit not reachable from `develop`. This is not a routine fast-forward release.

Before the release merge, the unique `main` commit must be inspected and reconciled into `develop`, then CI must be rerun on the reconciled release candidate. No tag should be created from a merge whose ancestry has not been audited.

### 4. Hosted CI evidence must be current

The release checklist requires the `all checks passed` gate to be green on the exact release candidate. Earlier green runs are useful history but are not release evidence after metadata or ancestry changes.

The final candidate must therefore pass the complete required workflow after the version/date/changelog changes and after reconciliation with `main`.

### 5. Zenodo version DOI does not exist yet

The current concept DOI remains `10.5281/zenodo.21337272`. A version DOI for `0.3.0` can only be recorded after the GitHub release causes Zenodo to archive the new version.

Do not invent or pre-fill a version DOI. Publish the GitHub release first, verify the Zenodo record, then add the minted `0.3.0` DOI to `ZENODO.md` and citation metadata in the normal post-release synchronization step.

## Release gate

`v0.3.0` is ready to merge to `main` only when all of the following are true:

1. `main`'s unique commit has been reconciled into the candidate ancestry.
2. Every version-bearing metadata file reports `0.3.0`.
3. Release dates agree and reflect the actual release date.
4. The changelog has a dated `0.3.0` section and a new `Unreleased` section.
5. The README and archive notes no longer describe real-data validation as future work.
6. `pytest tests/test_project_metadata.py` passes.
7. The complete hosted `all checks passed` gate is green on the exact release-candidate head.
8. The candidate is merged to `main` before the `v0.3.0` tag is created.

## After publication

After the GitHub release and Zenodo archive exist:

- verify the new Zenodo version DOI and record URL;
- add the `0.3.0` row to `ZENODO.md`;
- ensure `CITATION.cff`, `.zenodo.json`, README citation text, and Zenodo agree;
- merge `main` back into `develop` according to `RELEASE.md`;
- begin the `0.4.0` evaluation/comparison work from the synchronized branch.

The next modelling priority remains the negative abstention result: confidence is not informative enough to support a safe abstention threshold, and this should be treated as an open research problem rather than hidden behind the successful circadian transfer result.
