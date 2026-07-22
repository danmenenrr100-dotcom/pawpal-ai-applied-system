"""Deterministic pet-care safety guardrails for PawPal AI."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailDecision:
    """Result returned after a safety check."""

    allowed: bool
    status: str
    messages: tuple[str, ...]
    missing_fields: tuple[str, ...] = ()
    requires_veterinarian: bool = False


class PetCareGuardrails:
    """Validate medication tasks and unsupported medical requests."""

    MEDICATION_TERMS = {
        "medication",
        "medicine",
        "med",
        "meds",
        "prescription",
        "pill",
        "tablet",
        "capsule",
        "dose",
        "dosage",
    }

    GENERIC_MEDICATION_NAMES = {
        "medication",
        "medicine",
        "med",
        "meds",
        "pill",
        "prescription",
    }

    DOSAGE_WITH_UNIT_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:mg|mcg|g|kg|ml|l|iu|unit|units|"
        r"tablet|tablets|capsule|capsules|drop|drops|"
        r"pump|pumps)\b",
        re.IGNORECASE,
    )

    URGENT_PATTERNS = {
        "possible overdose": r"\boverdose\b",
        "accidental extra dose": r"\bextra dose\b",
        "possible poisoning": r"\bpoison(?:ed|ing)?\b",
        "adverse reaction": r"\badverse reaction\b",
        "breathing difficulty": r"\b(?:difficulty|trouble)\s+breathing\b",
        "seizure": r"\bseizure\b",
        "collapse": r"\bcollaps(?:e|ed|ing)\b",
        "loss of consciousness": r"\bunconscious\b",
    }

    UNSUPPORTED_ADVICE_PATTERNS = {
        "missed-dose decision": r"\bmissed (?:a )?dose\b",
        "double-dose request": r"\bdouble (?:the )?dose\b",
        "dosage calculation": (
            r"\b(?:calculate|choose|estimate|recommend)"
            r".{0,25}\b(?:dose|dosage)\b"
        ),
        "starting medication": r"\bstart(?:ing)?\s+(?:a |the )?medication\b",
        "stopping medication": r"\bstop(?:ping)?\s+(?:a |the )?medication\b",
        "medication substitution": (
            r"\b(?:replace|substitute|switch)"
            r".{0,25}\b(?:medication|medicine|drug)\b"
        ),
        "human medication request": (
            r"\b(?:human medication|human medicine|"
            r"ibuprofen|acetaminophen|paracetamol)\b"
        ),
        "diagnosis request": (
            r"\b(?:diagnose|diagnosis|what disease|what condition)\b"
        ),
    }

    @staticmethod
    def _value(
        task: Mapping[str, object],
        *field_names: str,
    ) -> str:
        for field_name in field_names:
            value = task.get(field_name)

            if value is not None and str(value).strip():
                return str(value).strip()

        return ""

    @classmethod
    def is_medication_task(
        cls,
        task: Mapping[str, object],
    ) -> bool:
        """Return whether a task involves administering medication."""

        searchable_fields = (
            "task_type",
            "category",
            "name",
            "title",
            "description",
        )

        text = " ".join(
            cls._value(task, field)
            for field in searchable_fields
        ).lower()

        return any(
            re.search(rf"\b{re.escape(term)}\b", text)
            for term in cls.MEDICATION_TERMS
        )

    @classmethod
    def validate_task(
        cls,
        task: Mapping[str, object],
    ) -> GuardrailDecision:
        """Validate one task before PawPal AI schedules it."""

        if not isinstance(task, Mapping):
            raise TypeError("task must be a mapping.")

        if not cls.is_medication_task(task):
            return GuardrailDecision(
                allowed=True,
                status="allowed",
                messages=("Routine care task passed safety validation.",),
            )

        missing_fields: list[str] = []

        medication_name = cls._value(
            task,
            "medication_name",
            "medicine_name",
        )

        if (
            not medication_name
            or medication_name.lower() in cls.GENERIC_MEDICATION_NAMES
        ):
            missing_fields.append("medication_name")

        dosage = cls._value(task, "dosage", "dose")
        dosage_unit = cls._value(
            task,
            "dosage_unit",
            "dose_unit",
            "unit",
        )

        if not dosage:
            missing_fields.append("dosage")
        elif not dosage_unit and not cls.DOSAGE_WITH_UNIT_PATTERN.search(
            dosage
        ):
            missing_fields.append("dosage_unit")

        administration_schedule = cls._value(
            task,
            "administration_time",
            "time_or_frequency",
            "frequency",
            "schedule",
        )

        if not administration_schedule:
            missing_fields.append("administration_time_or_frequency")

        veterinarian_directions = cls._value(
            task,
            "veterinarian_directions",
            "vet_instructions",
            "prescription_instructions",
        )

        if not veterinarian_directions:
            missing_fields.append("veterinarian_directions")

        if missing_fields:
            readable_fields = ", ".join(missing_fields)

            return GuardrailDecision(
                allowed=False,
                status="blocked",
                messages=(
                    "Medication task blocked because required "
                    f"information is missing: {readable_fields}.",
                    "Confirm the prescription label and instructions "
                    "with a veterinarian before scheduling this task.",
                ),
                missing_fields=tuple(missing_fields),
                requires_veterinarian=True,
            )

        return GuardrailDecision(
            allowed=True,
            status="allowed",
            messages=(
                "Medication task contains the required owner-provided "
                "prescription details.",
                "PawPal AI will schedule the reminder without changing "
                "the veterinarian's instructions.",
            ),
        )

    @classmethod
    def evaluate_request(cls, request: str) -> GuardrailDecision:
        """Block emergency handling and unsupported veterinary advice."""

        if not request or not request.strip():
            return GuardrailDecision(
                allowed=False,
                status="blocked",
                messages=("A pet-care request is required.",),
            )

        normalized_request = " ".join(request.lower().split())

        urgent_matches = [
            label
            for label, pattern in cls.URGENT_PATTERNS.items()
            if re.search(pattern, normalized_request)
        ]

        if urgent_matches:
            return GuardrailDecision(
                allowed=False,
                status="urgent",
                messages=(
                    "This request may involve an urgent veterinary issue: "
                    + ", ".join(urgent_matches)
                    + ".",
                    "Contact a veterinarian or emergency veterinary "
                    "hospital promptly. PawPal AI cannot provide "
                    "emergency treatment instructions.",
                ),
                requires_veterinarian=True,
            )

        blocked_matches = [
            label
            for label, pattern in cls.UNSUPPORTED_ADVICE_PATTERNS.items()
            if re.search(pattern, normalized_request)
        ]

        if blocked_matches:
            return GuardrailDecision(
                allowed=False,
                status="blocked",
                messages=(
                    "PawPal AI cannot provide this type of veterinary "
                    "guidance: "
                    + ", ".join(blocked_matches)
                    + ".",
                    "Ask a veterinarian for instructions. PawPal AI may "
                    "help schedule reminders after exact directions are "
                    "provided.",
                ),
                requires_veterinarian=True,
            )

        return GuardrailDecision(
            allowed=True,
            status="allowed",
            messages=(
                "The request is within PawPal AI's routine scheduling "
                "scope.",
            ),
        )

    @classmethod
    def validate_plan(
        cls,
        tasks: Iterable[Mapping[str, object]],
    ) -> list[GuardrailDecision]:
        """Validate every task in a proposed care plan."""

        return [cls.validate_task(task) for task in tasks]


if __name__ == "__main__":
    guardrails = PetCareGuardrails()

    example_task = {
        "name": "Morning Medication",
        "medication_name": "Example prescription",
        "dosage": "1 tablet",
        "time_or_frequency": "8:00 AM",
        "veterinarian_directions": "Follow the prescription label.",
    }

    decision = guardrails.validate_task(example_task)

    print(f"Status: {decision.status}")
    print(f"Allowed: {decision.allowed}")

    for message in decision.messages:
        print(f"- {message}")