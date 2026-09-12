"""Characterise confidence saturation during a quiet CASAS-style interval.

This is a diagnostic regression for the current abstention failure. It is not a
statement that high confidence under silence is desirable. When the uncertainty
model is changed deliberately, this test should change with it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from sensor_modeling.datasets import hh_sensor_specs
from sensor_modeling.fusion import MultimodalBayesFilter, default_emissions
from sensor_modeling.observations import SensorRegistry
from sensor_modeling.states import BehaviouralState, StateOntology

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
MOTION_LOCATIONS = ("Kitchen", "Bathroom", "Bedroom", "LivingRoom", "Hall")
DEFAULT_LOCATIONS = (*MOTION_LOCATIONS, "FrontDoor")


def _filter(locations: tuple[str, ...] = DEFAULT_LOCATIONS) -> MultimodalBayesFilter:
    """Build an aggregate-room deployment representative of CASAS hh."""
    specs, unmapped = hh_sensor_specs(locations)
    assert not unmapped
    registry = SensorRegistry.from_specs(specs)
    ontology = StateOntology()
    return MultimodalBayesFilter(
        ontology,
        default_emissions(registry, ontology),
        registry=registry,
    )


def _after_one_quiet_hour(model: MultimodalBayesFilter, *, reliability: float):
    """Advance twelve five-minute intervals without sensor activations."""
    estimate = model.update(T0, (), reliabilities=reliability)
    for index in range(1, 13):
        estimate = model.update(
            T0 + timedelta(minutes=5 * index),
            (),
            reliabilities=reliability,
        )
    return estimate


def test_quiet_period_saturation_requires_silence_likelihoods() -> None:
    """Separate transition-prior persistence from accumulated silence evidence."""
    prior_only = _after_one_quiet_hour(_filter(), reliability=0.0)
    silent_sensors = _after_one_quiet_hour(_filter(), reliability=1.0)

    stationary_confidence = float(StateOntology().stationary().max())
    assert prior_only.confidence == pytest.approx(stationary_confidence)
    assert prior_only.confidence < 0.35

    assert silent_sensors.most_likely is BehaviouralState.SLEEPING
    assert silent_sensors.confidence > 0.95

    evidence_strength = float(
        np.mean([abs(item.support) for item in silent_sensors.evidence])
    )
    assert evidence_strength < 0.02


def test_extreme_confidence_requires_complementary_silence_streams() -> None:
    """Room-motion and entrance-door silence eliminate different alternatives."""
    motion_only = _after_one_quiet_hour(
        _filter(MOTION_LOCATIONS),
        reliability=1.0,
    )
    door_only = _after_one_quiet_hour(_filter(("FrontDoor",)), reliability=1.0)
    combined = _after_one_quiet_hour(_filter(), reliability=1.0)

    assert motion_only.confidence < 0.60
    assert door_only.confidence < 0.50
    assert combined.most_likely is BehaviouralState.SLEEPING
    assert combined.confidence > 0.95

    partial_confidence = max(motion_only.confidence, door_only.confidence)
    assert combined.confidence - partial_confidence > 0.35
