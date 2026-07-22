# PawPal AI Model Card

## System Name

PawPal AI: Retrieval-Grounded Pet-Care Planning Assistant

## Version

Version 1.0

## Goal

PawPal AI helps pet owners organize routine care tasks into a safe daily schedule. It considers task priority, duration, fixed times, owner availability, pet-specific notes, and retrieved pet-care guidance.

## System Type

PawPal AI is an agentic, retrieval-grounded planning system. It combines:

- Multi-source information retrieval
- Request and task guardrails
- Priority-based scheduling
- Conflict detection
- One controlled revision attempt
- Output validation
- Citations and workflow tracing

The current version uses deterministic planning logic rather than training a new machine-learning model.

## Inputs

The system accepts:

- Owner planning request
- Pet name
- Available start time
- Total available minutes
- Task name
- Task duration
- Task priority
- Optional fixed time
- Medication details supplied by the owner
- Number of knowledge sources to retrieve

## Outputs

The system can produce:

- A validated daily pet-care plan
- Start and end times for each task
- An explanation for each scheduling decision
- Retrieved citations
- Blocked-task explanations
- Deferred-task explanations
- Workflow status and trace
- A safe fallback response when necessary

## Knowledge Sources

PawPal AI retrieves information from:

1. General pet-care guidance
2. Pet-specific notes

The retrieved evidence is included with citations so the user can see what information supported the workflow.

## Agent Workflow

1. Evaluate the request with safety guardrails.
2. Stop and return urgent guidance when emergency language is detected.
3. Retrieve relevant general and pet-specific information.
4. Validate every task and its required fields.
5. Block unsafe or incomplete tasks.
6. Normalize task times, durations, and priorities.
7. Schedule fixed-time tasks.
8. Place flexible tasks by priority in available openings.
9. Validate the completed plan for conflicts, duration errors, safety issues, and scheduling-window violations.
10. Make one conflict-aware revision attempt when validation fails.
11. Return the validated plan or a safe fallback response.

## Safety Guardrails

PawPal AI is designed to:

- Detect potentially urgent veterinary situations
- Avoid diagnosing medical conditions
- Avoid calculating or recommending medication dosages
- Require owner-provided medication instructions
- Block incomplete medication tasks
- Reject invalid task durations and scheduling windows
- Prevent overlapping tasks in the final plan
- Stop after one revision attempt
- Recommend professional veterinary help when appropriate

## Evaluation Process

The system was evaluated with automated tests and manual interface testing.

The test suite checks:

- Successful end-to-end plan generation
- Priority ordering
- Fixed-time scheduling
- Conflict detection and revision
- Full scheduling windows
- Missing task information
- Invalid task formats
- Medication guardrails
- Urgent-request handling
- Retrieval behavior
- Citation generation
- Scheduling-window validation
- Safe fallback behavior

At the time of this version, the complete project test suite passed 37 tests.

## Observed Behavior

The system consistently:

- Preserves valid fixed times
- Schedules high-priority flexible tasks first
- Places flexible tasks in the earliest available opening
- Defers tasks that do not fit
- Blocks incomplete or unsafe tasks
- Revises conflicting plans once
- Provides evidence citations and a visible workflow trace

## Limitations

PawPal AI:

- Is not a veterinarian
- Cannot diagnose illnesses or injuries
- Cannot determine whether a medication is appropriate
- Cannot calculate or change medication dosages
- Depends on the accuracy of owner-provided information
- Depends on the quality and coverage of its local knowledge sources
- Uses a simple scheduling strategy that may not capture every real-life preference
- Does not currently learn from previous schedules
- Does not automatically synchronize with calendars or veterinary systems
- Cannot guarantee that retrieved guidance applies to every animal

## Potential Risks and Biases

The available guidance may be incomplete or more applicable to common household pets than unusual species. Pet-specific notes may also become outdated. Priority values are supplied by the owner, so an incorrectly assigned priority can affect the plan.

To reduce these risks, the system validates inputs, shows citations, explains its decisions, blocks unsafe tasks, and keeps the owner responsible for reviewing the final plan.

## Intended Use

PawPal AI is intended for:

- Routine pet-care scheduling
- Walks
- Feeding
- Grooming
- Enrichment
- Owner-provided medication reminders
- Organizing tasks within a limited time window
- Educational demonstrations of retrieval, guardrails, and agentic workflows

## Non-Intended Use

PawPal AI should not be used for:

- Veterinary diagnosis
- Emergency response
- Medication selection
- Dosage calculation
- Changing a prescription
- Replacing professional veterinary advice
- Making decisions when required information is missing

## Privacy Considerations

Users should avoid entering unnecessary sensitive information. Pet-specific notes should contain only the information required for care planning. Future versions should add access controls, secure storage, retention policies, and deletion controls before handling real private data.

## Future Improvements

Future versions could include:

- Editable generated schedules
- Recurring task support
- Calendar integration
- Better semantic retrieval
- Source freshness checks
- More detailed pet profiles
- Species-specific safety rules
- User feedback and preference learning
- Additional accessibility features
- Expanded evaluation datasets
- Human review for high-risk requests
- More advanced conflict-resolution strategies

## Human Oversight

The pet owner must review the generated plan before using it. A veterinarian or emergency veterinary service should handle medical questions, dosage decisions, medication changes, suspected poisoning, overdoses, or urgent symptoms.