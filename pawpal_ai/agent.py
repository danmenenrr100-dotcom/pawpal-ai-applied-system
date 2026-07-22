"""Agentic planning workflow for PawPal AI."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime

from pawpal_ai.guardrails import PetCareGuardrails
from pawpal_ai.retriever import (
    MultiSourceRetriever,
    RetrievedEvidence,
)


@dataclass(frozen=True)
class WorkflowStep:
    """One recorded action in the agent workflow."""

    action: str
    status: str
    detail: str


@dataclass(frozen=True)
class TaskIssue:
    """A task that was blocked or deferred."""

    task_name: str
    reason: str


@dataclass(frozen=True)
class PlanItem:
    """One validated item in the generated care plan."""

    task_name: str
    start_time: str
    end_time: str
    duration_minutes: int
    priority: str
    reason: str
    original_task: dict[str, object] = field(repr=False)
    _start_minute: int = field(repr=False)
    _end_minute: int = field(repr=False)


@dataclass(frozen=True)
class AgentResult:
    """Final result returned by the PawPal AI workflow."""

    status: str
    request: str
    pet_name: str | None
    plan: tuple[PlanItem, ...]
    blocked_tasks: tuple[TaskIssue, ...]
    deferred_tasks: tuple[TaskIssue, ...]
    citations: tuple[str, ...]
    evidence: tuple[RetrievedEvidence, ...]
    trace: tuple[WorkflowStep, ...]
    revision_attempted: bool
    messages: tuple[str, ...]


@dataclass(frozen=True)
class _TaskCandidate:
    """Normalized task used internally by the planner."""

    index: int
    name: str
    duration_minutes: int
    priority: str
    priority_rank: int
    fixed_start: int | None
    raw: dict[str, object]


class PawPalAgent:
    """Retrieve, plan, validate, and revise a pet-care schedule."""

    PRIORITY_RANK = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    def __init__(
        self,
        retriever: MultiSourceRetriever | None = None,
        guardrails: PetCareGuardrails | None = None,
    ) -> None:
        self.retriever = retriever or MultiSourceRetriever()
        self.guardrails = guardrails or PetCareGuardrails()

    @staticmethod
    def _first_value(
        task: Mapping[str, object],
        *field_names: str,
    ) -> object | None:
        for field_name in field_names:
            value = task.get(field_name)

            if value is not None and str(value).strip():
                return value

        return None

    @staticmethod
    def _parse_time(value: object) -> int:
        text = str(value).strip().upper()

        for time_format in ("%H:%M", "%I:%M %p", "%I %p"):
            try:
                parsed = datetime.strptime(text, time_format)
                return parsed.hour * 60 + parsed.minute
            except ValueError:
                continue

        raise ValueError(
            f"Invalid time '{value}'. Use HH:MM or H:MM AM/PM."
        )

    @staticmethod
    def _format_time(total_minutes: int) -> str:
        hour = (total_minutes // 60) % 24
        minute = total_minutes % 60
        suffix = "AM" if hour < 12 else "PM"
        display_hour = hour % 12 or 12
        return f"{display_hour}:{minute:02d} {suffix}"

    @classmethod
    def _normalize_priority(cls, value: object | None) -> tuple[str, int]:
        if value is None:
            return "medium", cls.PRIORITY_RANK["medium"]

        text = str(value).strip().lower()

        aliases = {
            "1": "high",
            "2": "medium",
            "3": "low",
            "urgent": "high",
            "normal": "medium",
        }

        text = aliases.get(text, text)

        if text not in cls.PRIORITY_RANK:
            raise ValueError(
                "Priority must be high, medium, low, 1, 2, or 3."
            )

        return text, cls.PRIORITY_RANK[text]

    @classmethod
    def _normalize_task(
        cls,
        task: Mapping[str, object],
        index: int,
    ) -> _TaskCandidate:
        name_value = cls._first_value(task, "name", "title")

        if name_value is None:
            raise ValueError("Task name is required.")

        duration_value = cls._first_value(
            task,
            "duration_minutes",
            "duration",
        )

        if duration_value is None:
            raise ValueError("Task duration is required.")

        try:
            duration_minutes = int(str(duration_value).strip())
        except ValueError as error:
            raise ValueError(
                "Task duration must be a whole number of minutes."
            ) from error

        if duration_minutes <= 0:
            raise ValueError("Task duration must be greater than zero.")

        priority, priority_rank = cls._normalize_priority(
            cls._first_value(task, "priority")
        )

        time_value = cls._first_value(
            task,
            "fixed_time",
            "required_time",
            "start_time",
            "time",
        )

        fixed_start = (
            cls._parse_time(time_value)
            if time_value is not None
            else None
        )

        return _TaskCandidate(
            index=index,
            name=str(name_value).strip(),
            duration_minutes=duration_minutes,
            priority=priority,
            priority_rank=priority_rank,
            fixed_start=fixed_start,
            raw=dict(task),
        )

    @classmethod
    def _create_plan_item(
        cls,
        candidate: _TaskCandidate,
        start_minute: int,
        reason: str,
    ) -> PlanItem:
        end_minute = start_minute + candidate.duration_minutes

        return PlanItem(
            task_name=candidate.name,
            start_time=cls._format_time(start_minute),
            end_time=cls._format_time(end_minute),
            duration_minutes=candidate.duration_minutes,
            priority=candidate.priority,
            reason=reason,
            original_task=dict(candidate.raw),
            _start_minute=start_minute,
            _end_minute=end_minute,
        )

    @staticmethod
    def _overlaps(
        start_minute: int,
        end_minute: int,
        plan: Sequence[PlanItem],
    ) -> bool:
        return any(
            start_minute < item._end_minute
            and end_minute > item._start_minute
            for item in plan
        )

    @staticmethod
    def _find_opening(
        duration_minutes: int,
        plan: Sequence[PlanItem],
        window_start: int,
        window_end: int,
    ) -> int | None:
        cursor = window_start

        for item in sorted(plan, key=lambda entry: entry._start_minute):
            if cursor + duration_minutes <= item._start_minute:
                return cursor

            cursor = max(cursor, item._end_minute)

        if cursor + duration_minutes <= window_end:
            return cursor

        return None

    def _create_initial_plan(
        self,
        candidates: Sequence[_TaskCandidate],
        window_start: int,
        window_end: int,
    ) -> tuple[list[PlanItem], list[TaskIssue]]:
        plan: list[PlanItem] = []
        deferred: list[TaskIssue] = []

        fixed_tasks = sorted(
            (
                candidate
                for candidate in candidates
                if candidate.fixed_start is not None
            ),
            key=lambda candidate: (
                candidate.fixed_start or 0,
                candidate.index,
            ),
        )

        for candidate in fixed_tasks:
            start = candidate.fixed_start or 0
            end = start + candidate.duration_minutes

            if start < window_start or end > window_end:
                deferred.append(
                    TaskIssue(
                        candidate.name,
                        "The fixed time is outside the owner's "
                        "available scheduling window.",
                    )
                )
                continue

            plan.append(
                self._create_plan_item(
                    candidate,
                    start,
                    "Kept the owner-provided fixed time.",
                )
            )

        flexible_tasks = sorted(
            (
                candidate
                for candidate in candidates
                if candidate.fixed_start is None
            ),
            key=lambda candidate: (
                candidate.priority_rank,
                candidate.index,
            ),
        )

        for candidate in flexible_tasks:
            start = self._find_opening(
                candidate.duration_minutes,
                plan,
                window_start,
                window_end,
            )

            if start is None:
                deferred.append(
                    TaskIssue(
                        candidate.name,
                        "Not enough available time remained for this task.",
                    )
                )
                continue

            plan.append(
                self._create_plan_item(
                    candidate,
                    start,
                    "Placed the flexible task in the earliest available "
                    f"opening based on {candidate.priority} priority.",
                )
            )

        plan.sort(key=lambda item: item._start_minute)
        return plan, deferred

    def _validate_plan(
        self,
        plan: Sequence[PlanItem],
        window_start: int,
        window_end: int,
    ) -> list[str]:
        errors: list[str] = []
        ordered_plan = sorted(
            plan,
            key=lambda item: item._start_minute,
        )

        for item in ordered_plan:
            if (
                item._start_minute < window_start
                or item._end_minute > window_end
            ):
                errors.append(
                    f"{item.task_name} is outside the available window."
                )

            if (
                item._end_minute - item._start_minute
                != item.duration_minutes
            ):
                errors.append(
                    f"{item.task_name} has an incorrect duration."
                )

            safety_decision = self.guardrails.validate_task(
                item.original_task
            )

            if not safety_decision.allowed:
                errors.append(
                    f"{item.task_name} failed output safety validation."
                )

        for previous, current in zip(
            ordered_plan,
            ordered_plan[1:],
        ):
            if current._start_minute < previous._end_minute:
                errors.append(
                    f"{previous.task_name} overlaps with "
                    f"{current.task_name}."
                )

        return errors

    def _revise_plan(
        self,
        candidates: Sequence[_TaskCandidate],
        window_start: int,
        window_end: int,
    ) -> tuple[list[PlanItem], list[TaskIssue]]:
        """Make one conflict-aware revision attempt."""

        plan: list[PlanItem] = []
        deferred: list[TaskIssue] = []

        fixed_tasks = sorted(
            (
                candidate
                for candidate in candidates
                if candidate.fixed_start is not None
            ),
            key=lambda candidate: (
                candidate.priority_rank,
                candidate.fixed_start or 0,
                candidate.index,
            ),
        )

        for candidate in fixed_tasks:
            start = candidate.fixed_start or 0
            end = start + candidate.duration_minutes

            if start < window_start or end > window_end:
                deferred.append(
                    TaskIssue(
                        candidate.name,
                        "The fixed time is outside the available window.",
                    )
                )
                continue

            if self._overlaps(start, end, plan):
                deferred.append(
                    TaskIssue(
                        candidate.name,
                        "Deferred during revision because its fixed time "
                        "conflicted with another higher-priority task.",
                    )
                )
                continue

            plan.append(
                self._create_plan_item(
                    candidate,
                    start,
                    "Preserved the non-conflicting fixed time.",
                )
            )

        flexible_tasks = sorted(
            (
                candidate
                for candidate in candidates
                if candidate.fixed_start is None
            ),
            key=lambda candidate: (
                candidate.priority_rank,
                candidate.index,
            ),
        )

        for candidate in flexible_tasks:
            start = self._find_opening(
                candidate.duration_minutes,
                plan,
                window_start,
                window_end,
            )

            if start is None:
                deferred.append(
                    TaskIssue(
                        candidate.name,
                        "Deferred during revision because no safe opening "
                        "was available.",
                    )
                )
                continue

            plan.append(
                self._create_plan_item(
                    candidate,
                    start,
                    "Rescheduled into the earliest non-conflicting opening.",
                )
            )

        plan.sort(key=lambda item: item._start_minute)
        return plan, deferred

    def run(
        self,
        request: str,
        tasks: Sequence[Mapping[str, object]],
        pet_name: str | None = None,
        available_start: str = "8:00 AM",
        available_minutes: int = 120,
        top_k: int = 4,
    ) -> AgentResult:
        """Execute the complete PawPal AI workflow."""

        if available_minutes <= 0:
            raise ValueError("available_minutes must be greater than zero.")

        window_start = self._parse_time(available_start)
        window_end = window_start + available_minutes

        if window_end > 24 * 60:
            raise ValueError(
                "The available scheduling window cannot cross midnight."
            )

        trace: list[WorkflowStep] = []

        request_decision = self.guardrails.evaluate_request(request)
        trace.append(
            WorkflowStep(
                action="request_guardrail",
                status=request_decision.status,
                detail=" ".join(request_decision.messages),
            )
        )

        if not request_decision.allowed:
            return AgentResult(
                status=request_decision.status,
                request=request,
                pet_name=pet_name,
                plan=(),
                blocked_tasks=(),
                deferred_tasks=(),
                citations=(),
                evidence=(),
                trace=tuple(trace),
                revision_attempted=False,
                messages=request_decision.messages,
            )

        task_list = list(tasks)

        query_parts = [
            request,
            pet_name or "",
            " ".join(
                str(self._first_value(task, "name", "title") or "")
                for task in task_list
                if isinstance(task, Mapping)
            ),
            "pet care scheduling safety",
        ]

        evidence = self.retriever.retrieve(
            query=" ".join(query_parts),
            pet_name=pet_name,
            top_k=top_k,
        )

        trace.append(
            WorkflowStep(
                action="retrieve_evidence",
                status="completed",
                detail=f"Retrieved {len(evidence)} knowledge sources.",
            )
        )

        candidates: list[_TaskCandidate] = []
        blocked_tasks: list[TaskIssue] = []

        for index, task in enumerate(task_list):
            if not isinstance(task, Mapping):
                blocked_tasks.append(
                    TaskIssue(
                        task_name=f"Task {index + 1}",
                        reason="Task must be provided as a mapping.",
                    )
                )
                continue

            safety_decision = self.guardrails.validate_task(task)
            task_name = str(
                self._first_value(task, "name", "title")
                or f"Task {index + 1}"
            )

            if not safety_decision.allowed:
                blocked_tasks.append(
                    TaskIssue(
                        task_name=task_name,
                        reason=" ".join(safety_decision.messages),
                    )
                )
                continue

            try:
                candidates.append(
                    self._normalize_task(task, index)
                )
            except ValueError as error:
                blocked_tasks.append(
                    TaskIssue(
                        task_name=task_name,
                        reason=str(error),
                    )
                )

        trace.append(
            WorkflowStep(
                action="validate_tasks",
                status="completed",
                detail=(
                    f"{len(candidates)} tasks passed; "
                    f"{len(blocked_tasks)} tasks were blocked."
                ),
            )
        )

        citations = tuple(item.citation for item in evidence)

        if not candidates:
            return AgentResult(
                status="blocked",
                request=request,
                pet_name=pet_name,
                plan=(),
                blocked_tasks=tuple(blocked_tasks),
                deferred_tasks=(),
                citations=citations,
                evidence=tuple(evidence),
                trace=tuple(trace),
                revision_attempted=False,
                messages=(
                    "No tasks passed the required safety and input checks.",
                ),
            )

        plan, deferred_tasks = self._create_initial_plan(
            candidates,
            window_start,
            window_end,
        )

        validation_errors = self._validate_plan(
            plan,
            window_start,
            window_end,
        )

        revision_attempted = False

        if validation_errors:
            trace.append(
                WorkflowStep(
                    action="validate_plan",
                    status="revision_required",
                    detail=" ".join(validation_errors),
                )
            )

            revision_attempted = True
            plan, deferred_tasks = self._revise_plan(
                candidates,
                window_start,
                window_end,
            )

            validation_errors = self._validate_plan(
                plan,
                window_start,
                window_end,
            )

            trace.append(
                WorkflowStep(
                    action="revise_once",
                    status=(
                        "passed"
                        if not validation_errors
                        else "failed"
                    ),
                    detail=(
                        "Revised plan passed validation."
                        if not validation_errors
                        else " ".join(validation_errors)
                    ),
                )
            )
        else:
            trace.append(
                WorkflowStep(
                    action="validate_plan",
                    status="passed",
                    detail="Initial plan passed all safety checks.",
                )
            )

        if validation_errors:
            return AgentResult(
                status="safe_fallback",
                request=request,
                pet_name=pet_name,
                plan=(),
                blocked_tasks=tuple(blocked_tasks),
                deferred_tasks=tuple(deferred_tasks),
                citations=citations,
                evidence=tuple(evidence),
                trace=tuple(trace),
                revision_attempted=revision_attempted,
                messages=(
                    "PawPal AI could not produce a conflict-free plan "
                    "after one revision attempt.",
                    "Review the task times or available minutes manually.",
                ),
            )

        status = (
            "completed_with_limits"
            if blocked_tasks or deferred_tasks
            else "completed"
        )

        messages = [
            "Created a validated pet-care plan using owner input and "
            "retrieved guidance."
        ]

        if blocked_tasks:
            messages.append(
                f"{len(blocked_tasks)} unsafe or incomplete task(s) "
                "were blocked."
            )

        if deferred_tasks:
            messages.append(
                f"{len(deferred_tasks)} task(s) were deferred because "
                "of time or scheduling conflicts."
            )

        return AgentResult(
            status=status,
            request=request,
            pet_name=pet_name,
            plan=tuple(plan),
            blocked_tasks=tuple(blocked_tasks),
            deferred_tasks=tuple(deferred_tasks),
            citations=citations,
            evidence=tuple(evidence),
            trace=tuple(trace),
            revision_attempted=revision_attempted,
            messages=tuple(messages),
        )


if __name__ == "__main__":
    agent = PawPalAgent()

    example_tasks = [
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
        tasks=example_tasks,
        pet_name="Max",
        available_start="8:00 AM",
        available_minutes=90,
    )

    print(f"Status: {result.status}")
    print(f"Revision attempted: {result.revision_attempted}")
    print()

    for item in result.plan:
        print(
            f"{item.start_time}-{item.end_time}: "
            f"{item.task_name} ({item.priority})"
        )

    print()
    print("Citations:")

    for citation in result.citations:
        print(f"- {citation}")