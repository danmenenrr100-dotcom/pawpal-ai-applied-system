"""Tests for the complete PawPal AI agent workflow."""

from dataclasses import dataclass

import pytest

from pawpal_ai.agent import PawPalAgent


@dataclass(frozen=True)
class StubEvidence:
    """Minimal retrieved evidence used during agent tests."""

    citation: str


class StubRetriever:
    """Predictable retriever for isolated workflow testing."""

    def __init__(self):
        self.calls = []

    def retrieve(
        self,
        *,
        query: str,
        pet_name: str | None = None,
        top_k: int = 4,
    ):
        self.calls.append(
            {
                "query": query,
                "pet_name": pet_name,
                "top_k": top_k,
            }
        )

        return (
            StubEvidence(
                citation="[pet-max-care-notes] Max's care notes"
            ),
        )


@pytest.fixture
def retriever() -> StubRetriever:
    return StubRetriever()


@pytest.fixture
def agent(retriever: StubRetriever) -> PawPalAgent:
    return PawPalAgent(retriever=retriever)


def test_complete_workflow_returns_validated_plan(
    agent: PawPalAgent,
    retriever: StubRetriever,
):
    tasks = [
        {
            "name": "Morning Walk",
            "duration": 30,
            "priority": "high",
            "fixed_time": "8:00 AM",
        },
        {
            "name": "Breakfast",
            "duration": 10,
            "priority": "medium",
        },
        {
            "name": "Morning Medication",
            "duration": 5,
            "priority": "high",
            "fixed_time": "8:30 AM",
            "medication_name": "Example prescription",
            "dosage": "1 tablet",
            "time_or_frequency": "8:30 AM",
            "veterinarian_directions": (
                "Follow the prescription label."
            ),
        },
    ]

    result = agent.run(
        request="Create a safe morning care plan for Max.",
        tasks=tasks,
        pet_name="Max",
        available_start="8:00 AM",
        available_minutes=90,
    )

    assert result.status == "completed"
    assert result.revision_attempted is False
    assert [item.task_name for item in result.plan] == [
        "Morning Walk",
        "Morning Medication",
        "Breakfast",
    ]
    assert [item.start_time for item in result.plan] == [
        "8:00 AM",
        "8:30 AM",
        "8:35 AM",
    ]
    assert result.citations == (
        "[pet-max-care-notes] Max's care notes",
    )
    assert retriever.calls[0]["pet_name"] == "Max"


def test_flexible_tasks_are_ordered_by_priority(
    agent: PawPalAgent,
):
    tasks = [
        {
            "name": "Grooming",
            "duration": 10,
            "priority": "low",
        },
        {
            "name": "Morning Walk",
            "duration": 10,
            "priority": "high",
        },
        {
            "name": "Breakfast",
            "duration": 10,
            "priority": "medium",
        },
    ]

    result = agent.run(
        request="Schedule Max's routine care.",
        tasks=tasks,
        pet_name="Max",
        available_minutes=60,
    )

    assert [item.task_name for item in result.plan] == [
        "Morning Walk",
        "Breakfast",
        "Grooming",
    ]


def test_conflicting_fixed_tasks_trigger_one_revision(
    agent: PawPalAgent,
):
    tasks = [
        {
            "name": "Low-priority Grooming",
            "duration": 30,
            "priority": "low",
            "fixed_time": "8:00 AM",
        },
        {
            "name": "High-priority Walk",
            "duration": 30,
            "priority": "high",
            "fixed_time": "8:15 AM",
        },
    ]

    result = agent.run(
        request="Create Max's morning schedule.",
        tasks=tasks,
        pet_name="Max",
        available_minutes=90,
    )

    assert result.status == "completed_with_limits"
    assert result.revision_attempted is True
    assert [item.task_name for item in result.plan] == [
        "High-priority Walk",
    ]
    assert result.plan[0].start_time == "8:15 AM"
    assert result.deferred_tasks[0].task_name == (
        "Low-priority Grooming"
    )
    assert any(
        step.action == "revise_once"
        and step.status == "passed"
        for step in result.trace
    )


def test_incomplete_medication_task_is_blocked(
    agent: PawPalAgent,
):
    tasks = [
        {
            "name": "Morning Walk",
            "duration": 30,
            "priority": "high",
        },
        {
            "name": "Give medication",
            "duration": 5,
            "priority": "high",
        },
    ]

    result = agent.run(
        request="Create Max's morning care plan.",
        tasks=tasks,
        pet_name="Max",
    )

    assert result.status == "completed_with_limits"
    assert [item.task_name for item in result.plan] == [
        "Morning Walk",
    ]
    assert result.blocked_tasks[0].task_name == "Give medication"
    assert "required information is missing" in (
        result.blocked_tasks[0].reason
    )


def test_urgent_request_stops_before_retrieval(
    agent: PawPalAgent,
    retriever: StubRetriever,
):
    result = agent.run(
        request="My pet may have received an overdose.",
        tasks=[
            {
                "name": "Morning Walk",
                "duration": 30,
            }
        ],
        pet_name="Max",
    )

    assert result.status == "urgent"
    assert result.plan == ()
    assert result.revision_attempted is False
    assert retriever.calls == []


def test_task_is_deferred_when_window_is_full(
    agent: PawPalAgent,
):
    tasks = [
        {
            "name": "Morning Walk",
            "duration": 20,
            "priority": "high",
        },
        {
            "name": "Grooming",
            "duration": 20,
            "priority": "low",
        },
    ]

    result = agent.run(
        request="Create Max's short morning plan.",
        tasks=tasks,
        pet_name="Max",
        available_minutes=30,
    )

    assert result.status == "completed_with_limits"
    assert [item.task_name for item in result.plan] == [
        "Morning Walk",
    ]
    assert result.deferred_tasks[0].task_name == "Grooming"


def test_all_invalid_tasks_return_blocked_status(
    agent: PawPalAgent,
):
    result = agent.run(
        request="Create Max's care plan.",
        tasks=[
            {
                "name": "Breakfast",
            }
        ],
        pet_name="Max",
    )

    assert result.status == "blocked"
    assert result.plan == ()
    assert result.blocked_tasks[0].task_name == "Breakfast"
    assert "duration is required" in (
        result.blocked_tasks[0].reason.lower()
    )


def test_non_mapping_task_is_blocked(agent: PawPalAgent):
    result = agent.run(
        request="Create Max's care plan.",
        tasks=["Morning Walk"],
        pet_name="Max",
    )

    assert result.status == "blocked"
    assert result.plan == ()
    assert result.blocked_tasks[0].task_name == "Task 1"
    assert "mapping" in result.blocked_tasks[0].reason


def test_non_positive_available_minutes_are_rejected(
    agent: PawPalAgent,
):
    with pytest.raises(
        ValueError,
        match="available_minutes must be greater than zero",
    ):
        agent.run(
            request="Create Max's care plan.",
            tasks=[],
            available_minutes=0,
        )


def test_scheduling_window_cannot_cross_midnight(
    agent: PawPalAgent,
):
    with pytest.raises(
        ValueError,
        match="cannot cross midnight",
    ):
        agent.run(
            request="Create Max's care plan.",
            tasks=[],
            available_start="11:30 PM",
            available_minutes=60,
        )