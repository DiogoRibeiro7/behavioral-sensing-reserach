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


def _filter() -> MultimodalBayesFilter:
    """Build a small aggregate-room deployment representative of CASAS hh."""
    specs, unmapped = hh_sensor_specs(
        ["Kitchen", "Bathroom", "Bedroom", "LivingRoom", "Hall", "FrontDoor"]
    )
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

    # With all sensor likelihoods disabled, a filter initialised at stationarity
    # remains at stationarity. The transition dynamics alone do not become
    # certain during the quiet hour.
    stationary_confidence = float(StateOntology().stationary().max())
    assert prior_only.confidence == pytest.approx(stationary_confidence)
    assert prior_only.confidence < 0.35

    # With the same transition dynamics but working event sensors, an hour with
    # no activations is repeatedly interpreted through the Poisson silence
    # likelihoods. The posterior becomes extremely concentrated on sleeping.
    assert silent_sensors.most_likely is BehaviouralState.SLEEPING
    assert silent_sensors.confidence > 0.95

    # No individual sensor strongly singles out sleeping in the final interval.
    # The concentration is produced by the accumulated joint pattern of weak,
    # mostly ambiguous silence evidence interacting with the state dynamics.
    evidence_strength = float(
        np.mean([abs(item.support) for item in silent_sensors.evidence])
    )
    assert evidence_strength < 0.02
