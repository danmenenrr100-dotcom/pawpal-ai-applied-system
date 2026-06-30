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
