# v0.3.0 Release Readiness

This document is the release-candidate record for `v0.3.0`. It separates the completed research result from the still-pending software release steps so that a successful external validation cannot be mistaken for an already-published package version.

## Candidate status

**Research result complete; release ancestry reconciled; software metadata still at 0.2.0.**

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

## Resolved blocker: branch ancestry

The previous version of this record noted that `develop` and `main` had diverged: `main` contained one commit not reachable from `develop`.

That commit was inspected. It is `3c5cc661524230ebdc3490a10764efe3aa17d23f`, the historical merge used to publish `v0.2.0`, not a later hotfix or content-only change. A no-content ancestry merge was then created on `develop` at `7652668f49aaa554a9c162baa8073c4047e14a34`, using the current `develop` tree unchanged and adding the `v0.2.0` release merge as a second parent.

After that reconciliation, `main` is an ancestor of `develop`; the branch comparison is 235 commits ahead and 0 behind. No file content changed in the ancestry merge.

## Remaining blockers

### 1. Release metadata still says 0.2.0

The following release-facing files must be changed together and validated by `tests/test_project_metadata.py`:

- `pyproject.toml`;
- `sensor_modeling/__init__.py`;
- `CITATION.cff`;
- `.zenodo.json`;
- the README version badge and citation block.

The intended version is `0.3.0`. The release date must be the actual publication date, not the date the external scoring was executed.

### 2. Changelog is still Unreleased

The existing `Unreleased` material describes the work that belongs to `0.3.0`. Before release, it must be closed under a dated `## [0.3.0]` heading and a fresh empty `Unreleased` section must be started.

The external validation outcome itself must also be represented in that release entry; otherwise the package would ship the candidate mechanism without recording the result that motivated the release line.

### 3. README contains stale evidence claims

The README still contains statements that nothing has been validated on real sensor data, despite the development evaluation and the completed frozen external validation. It also foregrounds a four-seed ablation pilot that the later 100-seed study superseded.

Those statements must be corrected before `0.3.0`; they are not cosmetic because they change how a reader interprets the evidence distributed with the package.

### 4. Hosted CI evidence must be current

PR #160 was green on CI run #334. The ancestry merge is content-preserving, but the final `0.3.0` metadata/changelog candidate will still require a fresh hosted run on its exact head.

The release checklist requires the `all checks passed` gate to be green after the version/date/changelog changes. Earlier green runs remain provenance, not final release evidence.

### 5. Zenodo publication is externally blocked

The current concept DOI remains `10.5281/zenodo.21337272`. A version DOI for `0.3.0` can only be recorded after the GitHub release causes Zenodo to archive the new version.

Zenodo is currently unavailable to the maintainer. This does **not** block repository preparation, CI validation, or merging a release candidate to `main`; it does block claiming that the `0.3.0` archive exists.

Do not invent or pre-fill a version DOI. Keep the concept DOI as the citation target during preparation. Once Zenodo is available again, publish or verify the GitHub-triggered archive, then add the minted `0.3.0` version DOI to `ZENODO.md` and citation metadata in a post-publication synchronization change.

## Release gate

`v0.3.0` is ready to merge to `main` only when all of the following are true:

1. Every version-bearing metadata file reports `0.3.0`.
2. Release dates agree and reflect the actual release date.
3. The changelog has a dated `0.3.0` section and a new `Unreleased` section.
4. The README no longer describes real-data validation as future work or foregrounds superseded pilot figures.
5. `pytest tests/test_project_metadata.py` passes.
6. The complete hosted `all checks passed` gate is green on the exact release-candidate head.
7. The candidate is merged to `main` before the `v0.3.0` tag is created.

Zenodo availability is a publication dependency, not a software-readiness criterion. If it is still unavailable when the GitHub release is otherwise ready, the repository must record the archive as pending rather than fabricate a DOI or silently imply archival completion.

## After publication

After the GitHub release and Zenodo archive exist:

- verify the new Zenodo version DOI and record URL;
- add the `0.3.0` row to `ZENODO.md`;
- ensure `CITATION.cff`, `.zenodo.json`, README citation text, and Zenodo agree;
- merge `main` back into `develop` according to `RELEASE.md`;
- begin the `0.4.0` evaluation/comparison work from the synchronized branch.

The next modelling priority remains the negative abstention result: confidence is not informative enough to support a safe abstention threshold, and this should be treated as an open research problem rather than hidden behind the successful circadian transfer result.
