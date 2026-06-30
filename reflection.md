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


duration + priority
daily schedule/plan
constraints
explanation of reasoning
tests for scheduling behavior


## 1a. Initial design

For the initial design of PawPal+, I chose four main classes: Owner, Pet, Task, and Scheduler.

The Owner class represents the person using the app. It stores the owner’s name, preferences, and pets. The Pet class represents each animal and stores details such as name, species, age, and the pet’s care tasks. The Task class represents one care activity, such as feeding, walking, medication, grooming, or enrichment. Each task stores details like duration, priority, preferred time, frequency, and completion status. The Scheduler class is responsible for organizing tasks into a daily plan, sorting tasks by priority or time, detecting conflicts, and explaining why a plan was chosen.

I chose this structure because it matches the real-world relationship of the system: an owner has pets, pets have tasks, and the scheduler organizes those tasks into a useful care plan.

In Phase 2, I translated my UML design into working Python code. I implemented the Owner, Pet, Task, and Scheduler classes in `pawpal_system.py`. The Owner class manages pets, the Pet class stores care tasks, the Task class tracks details like duration, priority, preferred time, frequency, and completion status, and the Scheduler class generates a daily care plan based on available time and task priority.

I verified the backend logic using a CLI-first workflow by creating `main.py`. This helped me confirm that the system could create pets, add tasks, generate a daily plan, explain the plan, and detect scheduling conflicts before connecting anything to the Streamlit interface. I also added initial pytest tests for task completion and adding tasks to a pet.

2b. Tradeoffs

One tradeoff in my scheduler is that conflict detection only checks for exact matching preferred times. For example, if two tasks are both scheduled at 08:00, the system flags a conflict. However, it does not detect overlapping durations, such as one task from 08:00–08:30 and another task at 08:15.

I chose this simpler approach because my current Task class stores a preferred time and duration, but the conflict detection logic is still lightweight. This keeps the algorithm easier to understand and test. A future improvement would be to calculate start and end times so PawPal+ can detect real overlapping task windows.
