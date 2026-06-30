# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?


##  Answers for Reflection -------------------------------------------------------------------

# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

For my initial UML design, I included four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

The `Owner` class represents the person using PawPal+. It stores the owner’s name, preferences, and list of pets. The `Pet` class represents each animal and stores details such as name, species, age, and that pet’s care tasks. The `Task` class represents one care activity, such as feeding, walking, medication, grooming, or enrichment. Each task stores information such as title, task type, duration, priority, preferred time, frequency, and completion status. The `Scheduler` class is responsible for organizing the tasks by sorting them, filtering them, generating a daily plan, detecting conflicts, handling recurring tasks, and explaining why a plan was chosen.

I chose this design because it matches the real-world structure of the app: an owner has pets, pets have tasks, and the scheduler organizes those tasks into a useful daily care plan.

**b. Design changes**

Yes, my design changed during implementation. At first, the system was mostly focused on basic task storage. During the project, I added more responsibility to the `Scheduler` class so it could act as the main logic layer. I added methods for filtering tasks, generating a daily plan based on available time, marking tasks complete, detecting conflicts, and explaining the plan.

Another change was adding `recurrence_generated` to the `Task` class. This helped prevent recurring tasks from creating duplicate future tasks after completion. I made this change because the system needed a safe way to handle daily or weekly tasks without repeatedly adding the same next task.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers several constraints: task priority, task duration, preferred time, completion status, frequency, and the owner’s available care time. The most important constraint is priority because high-priority tasks like medication or walks should be chosen before lower-priority tasks. The second major constraint is available time because the scheduler should only include tasks that fit within the amount of time the owner has.

The scheduler first sorts incomplete tasks by priority, then adds tasks to the daily plan as long as they fit within the available minutes. After choosing the tasks, it sorts the final plan by preferred time so the schedule is easier to read.

**b. Tradeoffs**

One tradeoff in my scheduler is that conflict detection only checks for exact matching preferred times. For example, if two tasks are both scheduled at `08:00`, the system flags a conflict. However, it does not detect overlapping durations, such as one task from `08:00–08:30` overlapping with another task at `08:15`.

This tradeoff is reasonable for this version of the project because the scheduler is meant to be simple, readable, and easy to test. The current system stores task duration, but the conflict logic does not yet calculate full start and end time ranges. A future version could improve this by converting preferred times into real time objects and checking for overlapping time windows.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools for design brainstorming, UML planning, Python class scaffolding, debugging, algorithm planning, test generation, and documentation support. AI was helpful for turning the project requirements into a clear class structure and for suggesting methods that matched the responsibilities of each class.

The most helpful prompts were specific ones, such as asking how the `Scheduler` should retrieve tasks from the owner’s pets, how to sort tasks by preferred time, how to detect conflicts, and how to create pytest tests for the scheduler. Breaking the work into separate phases helped me use AI more effectively because each chat focused on one task instead of mixing design, coding, testing, and documentation all at once.

**b. Judgment and verification**

One moment where I did not accept an AI suggestion as-is was when the AI assistant created or suggested a file named `pawpal.py`. The assignment specifically required the backend logic file to be named `pawpal_system.py`, so I rejected that file name and corrected the project structure.

I evaluated AI suggestions by checking them against the assignment instructions, running the code in the terminal, testing the Streamlit app, and running `python -m pytest`. I did not rely only on whether the code looked correct. I verified that the backend worked through `main.py`, that the tests passed, and that the UI actually used the classes from `pawpal_system.py`.

---

## 4. Testing and Verification

**a. What you tested**

I tested the most important backend behaviors in PawPal+. The tests verify that a task can be marked complete, a task can be added to a pet, tasks can be sorted by preferred time, tasks can be filtered by pet and completion status, recurring tasks create a new task after completion, and conflicts are detected when two tasks have the same preferred time.

These tests were important because they confirm that the main scheduling logic works before relying on the Streamlit interface. The tests also helped verify that the system’s core classes work together correctly.

**b. Confidence**

I am confident that the scheduler works correctly for the required project features. The test suite passes, the CLI demo works, and the Streamlit UI successfully connects to the backend logic. I would rate my confidence as four out of five stars.

If I had more time, I would test additional edge cases, such as invalid time formats, tasks with zero or negative duration, overlapping tasks based on duration, duplicate pet names, duplicate task names, and saving data after the app closes.

---

## 5. Reflection

**a. What went well**

The part of this project I am most satisfied with is how the backend logic, CLI demo, tests, UML diagram, and Streamlit UI all connect together. I started with a design, turned it into Python classes, verified it in the terminal, added tests, and then connected the logic to the app interface.

I am also satisfied with the `Scheduler` class because it became the main logic layer for sorting, filtering, generating plans, detecting conflicts, and explaining the schedule.

**b. What you would improve**

If I had another iteration, I would improve the scheduler by detecting overlapping task durations instead of only checking exact matching preferred times. I would also add persistent storage so the owner, pets, and tasks remain saved after the Streamlit app closes.

Another improvement would be stronger input validation. For example, the app could require preferred times to use a valid `HH:MM` format instead of accepting any text.

**c. Key takeaway**

One important thing I learned is that being the lead architect means making the final decisions, even when AI provides code quickly. AI was useful for brainstorming, scaffolding, and debugging, but I still had to check the assignment requirements, keep the design simple, test the system, and decide what belonged in the final project.

This project helped me understand that good system design comes from separating responsibilities clearly. The `Owner`, `Pet`, `Task`, and `Scheduler` classes each have a specific purpose, which made the project easier to build, test, and explain.


