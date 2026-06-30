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
    recurrence_generated: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_recurring(self) -> bool:
        """Return True if the task repeats."""
        return self.frequency.lower() in ["daily", "weekly"]

    def generate_next_occurrence(self) -> Optional["Task"]:
        """Create the next occurrence of a recurring task."""
        if not self.is_recurring():
            return None

        return Task(
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            completed=False,
        )


@dataclass
class Pet:
    """Represents a pet and its care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> bool:
        """Remove a task by title."""
        for task in self.tasks:
            if task.title.lower() == task_title.lower():
                self.tasks.remove(task)
                return True

        return False

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def find_task(self, task_title: str) -> Optional[Task]:
        """Find a task by title."""
        for task in self.tasks:
            if task.title.lower() == task_title.lower():
                return task

        return None


@dataclass
class Owner:
    """Represents the pet owner."""

    name: str
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def find_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet

        return None

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        all_tasks = []

        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())

        return all_tasks


class Scheduler:
    """Organizes tasks into a daily pet care plan."""

    def get_task_records(self, owner: Owner) -> List[tuple[Pet, Task]]:
        """Return pet-task pairs for every task owned by an owner."""
        records = []

        for pet in owner.pets:
            for task in pet.get_tasks():
                records.append((pet, task))

        return records

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority."""
        return sorted(tasks, key=lambda task: task.priority)

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred time."""
        return sorted(tasks, key=lambda task: task.preferred_time)

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        task_type: Optional[str] = None,
    ) -> List[tuple[Pet, Task]]:
        """Filter tasks by pet name, completion status, or task type."""
        filtered_records = []

        for pet, task in self.get_task_records(owner):
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue

            if completed is not None and task.completed != completed:
                continue

            if task_type is not None and task.task_type.lower() != task_type.lower():
                continue

            filtered_records.append((pet, task))

        return filtered_records

    def generate_daily_plan(self, owner: Owner, available_minutes: int) -> List[Task]:
        """Generate a daily plan based on task priority and available time."""
        tasks = self.sort_tasks_by_priority(owner.get_all_tasks())

        plan = []
        used_minutes = 0

        for task in tasks:
            if task.completed:
                continue

            if used_minutes + task.duration_minutes <= available_minutes:
                plan.append(task)
                used_minutes += task.duration_minutes

        return self.sort_tasks_by_time(plan)

    def mark_task_complete(self, pet: Pet, task_title: str) -> Optional[Task]:
        """Mark a task complete and create a recurring task if needed."""
        task = pet.find_task(task_title)

        if task is None:
            return None

        task.mark_complete()

        if task.is_recurring() and not task.recurrence_generated:
            next_task = task.generate_next_occurrence()
            task.recurrence_generated = True

            if next_task is not None:
                pet.add_task(next_task)

        return task

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Detect tasks with the same preferred time."""
        conflicts = []
        seen_times = {}

        for task in tasks:
            if task.preferred_time in seen_times:
                conflicts.append(
                    f"Conflict: {task.title} and {seen_times[task.preferred_time]} "
                    f"are both scheduled at {task.preferred_time}."
                )
            else:
                seen_times[task.preferred_time] = task.title

        return conflicts

    def explain_plan(self, plan: List[Task]) -> str:
        """Explain why the scheduler chose this plan."""
        if not plan:
            return "No tasks were selected because there were no available tasks or not enough available time."

        total_minutes = sum(task.duration_minutes for task in plan)

        return (
            f"This plan was selected by prioritizing incomplete tasks with the highest importance "
            f"while staying within the available time. The final plan includes {len(plan)} task(s) "
            f"and uses {total_minutes} total minute(s)."
        )