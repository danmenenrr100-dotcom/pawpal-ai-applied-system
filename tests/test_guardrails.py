"""Tests for PawPal AI pet-care safety guardrails."""

import pytest

from pawpal_ai.guardrails import PetCareGuardrails


def test_routine_care_task_is_allowed():
    task = {
        "name": "Morning Walk",
        "duration": 30,
    }

    decision = PetCareGuardrails.validate_task(task)

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.requires_veterinarian is False


def test_complete_medication_task_is_allowed():
    task = {
        "name": "Morning Medication",
        "medication_name": "Example prescription",
        "dosage": "1 tablet",
        "time_or_frequency": "8:00 AM",
        "veterinarian_directions": "Follow the prescription label.",
    }

    decision = PetCareGuardrails.validate_task(task)

    assert decision.allowed is True
    assert decision.status == "allowed"
    assert decision.missing_fields == ()


def test_medication_task_missing_details_is_blocked():
    task = {
        "name": "Give medication",
    }

    decision = PetCareGuardrails.validate_task(task)

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.requires_veterinarian is True
    assert "medication_name" in decision.missing_fields
    assert "dosage" in decision.missing_fields
    assert "administration_time_or_frequency" in decision.missing_fields
    assert "veterinarian_directions" in decision.missing_fields


def test_missing_dosage_unit_is_blocked():
    task = {
        "name": "Evening Medication",
        "medication_name": "Example prescription",
        "dosage": "5",
        "frequency": "Once each evening",
        "vet_instructions": "Follow the prescription label.",
    }

    decision = PetCareGuardrails.validate_task(task)

    assert decision.allowed is False
    assert "dosage_unit" in decision.missing_fields


def test_separate_dosage_unit_is_accepted():
    task = {
        "category": "medication",
        "medication_name": "Example prescription",
        "dosage": "5",
        "dosage_unit": "mg",
        "administration_time": "8:00 PM",
        "veterinarian_directions": "Follow the prescription label.",
    }

    decision = PetCareGuardrails.validate_task(task)

    assert decision.allowed is True


def test_overdose_request_is_marked_urgent():
    decision = PetCareGuardrails.evaluate_request(
        "My pet may have received an overdose."
    )

    assert decision.allowed is False
    assert decision.status == "urgent"
    assert decision.requires_veterinarian is True


def test_breathing_difficulty_is_marked_urgent():
    decision = PetCareGuardrails.evaluate_request(
        "My dog is having trouble breathing."
    )

    assert decision.allowed is False
    assert decision.status == "urgent"
    assert decision.requires_veterinarian is True


def test_missed_dose_advice_is_blocked():
    decision = PetCareGuardrails.evaluate_request(
        "What should I do about a missed dose?"
    )

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert decision.requires_veterinarian is True


def test_diagnosis_request_is_blocked():
    decision = PetCareGuardrails.evaluate_request(
        "Can you diagnose my pet?"
    )

    assert decision.allowed is False
    assert decision.status == "blocked"


def test_routine_scheduling_request_is_allowed():
    decision = PetCareGuardrails.evaluate_request(
        "Schedule Max's morning walk for 8:00 AM."
    )

    assert decision.allowed is True
    assert decision.status == "allowed"


def test_empty_request_is_blocked():
    decision = PetCareGuardrails.evaluate_request("   ")

    assert decision.allowed is False
    assert decision.status == "blocked"


def test_non_mapping_task_is_rejected():
    with pytest.raises(TypeError, match="task must be a mapping"):
        PetCareGuardrails.validate_task("Morning Walk")