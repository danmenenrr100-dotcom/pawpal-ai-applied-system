from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    task = Task(
        title="Morning Walk",
        task_type="Walk",
        duration_minutes=30,
        priority=1,
        preferred_time="08:00",
        frequency="daily",
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_to_pet():
    pet = Pet(name="Max", species="Dog", age=4)

    task = Task(
        title="Breakfast",
        task_type="Feeding",
        duration_minutes=10,
        priority=2,
        preferred_time="09:00",
        frequency="daily",
    )

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] == task


def test_sort_tasks_by_time():
    scheduler = Scheduler()

    later_task = Task(
        title="Dinner",
        task_type="Feeding",
        duration_minutes=10,
        priority=2,
        preferred_time="18:00",
    )

    earlier_task = Task(
        title="Morning Walk",
        task_type="Walk",
        duration_minutes=30,
        priority=1,
        preferred_time="08:00",
    )

    sorted_tasks = scheduler.sort_tasks_by_time([later_task, earlier_task])

    assert sorted_tasks[0] == earlier_task
    assert sorted_tasks[1] == later_task


def test_filter_tasks_by_pet_and_status():
    owner = Owner(name="Danny")
    pet = Pet(name="Max", species="Dog", age=4)
    owner.add_pet(pet)

    pending_task = Task(
        title="Morning Walk",
        task_type="Walk",
        duration_minutes=30,
        priority=1,
        preferred_time="08:00",
        completed=False,
    )

    completed_task = Task(
        title="Breakfast",
        task_type="Feeding",
        duration_minutes=10,
        priority=2,
        preferred_time="09:00",
        completed=True,
    )

    pet.add_task(pending_task)
    pet.add_task(completed_task)

    scheduler = Scheduler()

    filtered = scheduler.filter_tasks(
        owner,
        pet_name="Max",
        completed=False,
    )

    assert len(filtered) == 1
    assert filtered[0][0] == pet
    assert filtered[0][1] == pending_task


def test_recurring_task_created_when_completed():
    pet = Pet(name="Max", species="Dog", age=4)

    task = Task(
        title="Morning Walk",
        task_type="Walk",
        duration_minutes=30,
        priority=1,
        preferred_time="08:00",
        frequency="daily",
    )

    pet.add_task(task)

    scheduler = Scheduler()
    scheduler.mark_task_complete(pet, "Morning Walk")

    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False
    assert pet.tasks[1].title == "Morning Walk"
    assert pet.tasks[1].frequency == "daily"


def test_conflict_detection():
    task_one = Task(
        title="Morning Walk",
        task_type="Walk",
        duration_minutes=30,
        priority=1,
        preferred_time="08:00",
    )

    task_two = Task(
        title="Medication",
        task_type="Medication",
        duration_minutes=5,
        priority=1,
        preferred_time="08:00",
    )

    scheduler = Scheduler()
    conflicts = scheduler.detect_conflicts([task_one, task_two])

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]