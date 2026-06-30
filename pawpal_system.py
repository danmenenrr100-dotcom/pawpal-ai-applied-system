from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents one pet care activity."""

    title: str
    task_type: str
    duration_minutes: int
    priority: int
    preferred_time: str
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_recurring(self) -> bool:
        """Return True if the task repeats."""
        pass

    def generate_next_occurrence(self) -> Optional["Task"]:
        """Create the next occurrence of a recurring task."""
        pass


@dataclass
class Pet:
    """Represents a pet and its care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        pass

    def remove_task(self, task_title: str) -> bool:
        """Remove a task by title."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        pass


@dataclass
class Owner:
    """Represents the pet owner."""

    name: str
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def find_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        pass


class Scheduler:
    """Organizes tasks into a daily pet care plan."""

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority."""
        pass

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred time."""
        pass

    def generate_daily_plan(self, owner: Owner, available_minutes: int) -> List[Task]:
        """Generate a daily plan based on task priority and available time."""
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Detect tasks with the same preferred time."""
        pass

    def explain_plan(self, plan: List[Task]) -> str:
        """Explain why the scheduler chose this plan."""
        pass
        