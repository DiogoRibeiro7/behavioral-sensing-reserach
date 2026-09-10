"""Tests for real-data uncertainty diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast

import numpy as np

from sensor_modeling.datasets.evaluate import uncertainty_diagnostics
from sensor_modeling.fusion.estimate import EvidenceContribution, StateEstimate
from sensor_modeling.observations.types import Modality
from sensor_modeling.online.pipeline import PipelineStep
from sensor_modeling.states import BehaviouralState, StateOntology

S = BehaviouralState
T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _step(
    belief: list[float],
    *,
    support: float,
    state: BehaviouralState,
) -> PipelineStep:
    """Build the minimal pipeline-step shape needed by the diagnostic helper."""
    ontology = StateOntology()
    vector = np.zeros(ontology.size, dtype=float)
    vector[ontology.states.index(state)] = belief[0]
    remainder = (1.0 - belief[0]) / (ontology.size - 1)
    vector[vector == 0.0] = remainder

    estimate = StateEstimate(
        at=T0,
        ontology=ontology,
        belief=vector,
        evidence=(
            EvidenceContribution(
                sensor_id="motion",
                modality=Modality.MOTION,
                support=support,
                reliability=1.0,
                attribution=1.0,
                observations=1,
            ),
        ),
        completeness=1.0,
        min_confidence=0.35,
        min_completeness=0.25,
    )
    return cast(PipelineStep, SimpleNamespace(state=estimate))


def test_uncertainty_diagnostics_split_correct_from_incorrect() -> None:
    """Diagnostics should preserve the contrast the abstention study needs."""
    steps = [
        _step([0.80], support=2.0, state=S.HOME_ACTIVE),
        _step([0.90], support=0.2, state=S.KITCHEN_ACTIVITY),
    ]
    truth = [S.HOME_ACTIVE, S.BATHROOM_ACTIVITY]

    result = uncertainty_diagnostics(truth, steps)

    assert result.scored == 2
    assert result.correct == 1
    assert result.median_confidence_correct == 0.80
    assert result.median_confidence_incorrect == 0.90
    assert result.median_evidence_strength_correct == 2.0
    assert result.median_evidence_strength_incorrect == 0.2
    assert result.median_margin_correct is not None
    assert result.median_margin_incorrect is not None
    assert result.median_normalised_entropy_correct is not None
    assert result.median_normalised_entropy_incorrect is not None


def test_uncertainty_diagnostics_ignore_unlabelled_steps() -> None:
    """Unlabelled positions must not enter correct/incorrect summaries."""
    steps = [
        _step([0.75], support=1.0, state=S.HOME_ACTIVE),
        _step([0.99], support=9.0, state=S.KITCHEN_ACTIVITY),
    ]

    result = uncertainty_diagnostics([S.HOME_ACTIVE, None], steps)

    assert result.scored == 1
    assert result.correct == 1
    assert result.median_confidence_correct == 0.75
    assert result.median_confidence_incorrect is None
    assert result.median_evidence_strength_incorrect is None
