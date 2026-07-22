# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit pet care planning app that helps a pet owner manage daily care tasks for their pets. The app allows users to enter owner and pet information, add pet care tasks, generate a daily plan, detect scheduling conflicts, and explain why a schedule was chosen.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks such as walks, feedings, medications, enrichment, grooming, and appointments
- Consider constraints such as available time, priority, and owner preferences
- Produce a daily care plan
- Explain why the plan was chosen

This project follows a design-first workflow. I first created a UML diagram, then implemented the backend logic in Python, verified it through a CLI demo and pytest tests, and finally connected the logic to a Streamlit UI.

## Features

PawPal+ includes the following features:

- Enter owner information and preferences
- Add pet profiles with name, species, and age
- Add care tasks for each pet
- Store task details including duration, priority, preferred time, frequency, and completion status
- Generate a daily schedule based on available care time and task priority
- Display the generated plan clearly
- Explain why the scheduler selected the plan
- Filter tasks by pet, task type, and completion status
- Detect conflicts when two tasks share the same preferred time
- Mark tasks as complete
- Automatically create a new task when a daily or weekly recurring task is completed
- Verify backend logic with automated pytest tests

## Project Structure

```text
ai110-module2show-pawpal-starter/
├── app.py
├── main.py
├── pawpal_system.py
├── README.md
├── reflection.md
├── requirements.txt
├── diagrams/
│   ├── uml_draft.mmd
│   └── uml_final.mmd
└── tests/
    └── test_pawpal.py

    
    ---

# PawPal AI — Applied AI System

PawPal AI extends the original PawPal+ scheduler into a retrieval-grounded, safety-aware pet-care planning assistant.

## What PawPal AI Does

PawPal AI can:

- Retrieve general guidance and pet-specific notes
- Organize tasks by priority, duration, and fixed time
- Detect scheduling conflicts
- Block incomplete or unsafe tasks
- Defer tasks that do not fit the available window
- Perform one controlled revision attempt
- Validate the final schedule
- Display citations and a complete workflow trace
- Detect potentially urgent veterinary requests

## AI Workflow

1. Evaluate the owner’s request with guardrails.
2. Stop when urgent veterinary language is detected.
3. Retrieve relevant knowledge sources.
4. Validate each submitted care task.
5. Block unsafe or incomplete tasks.
6. Schedule fixed-time tasks.
7. Schedule flexible tasks by priority.
8. Validate the complete schedule.
9. Revise the schedule once if conflicts are detected.
10. Return a validated plan or safe fallback response.

## Architecture

The Mermaid architecture diagram is available here:

`diagrams/pawpal_ai_architecture.mmd`

The system connects:

- A Streamlit user interface
- Request and task guardrails
- Multi-source retrieval
- Priority-based planning
- Conflict detection
- Plan validation
- Controlled revision
- Citations and workflow tracing

## Safety Boundaries

PawPal AI supports routine care planning only.

It does not:

- Diagnose medical conditions
- Select medications
- Calculate medication dosages
- Change prescriptions
- Replace a veterinarian
- Handle emergencies

Medication reminders require complete instructions supplied by the owner. Urgent situations are redirected to professional veterinary care.

## Run the PawPal AI Interface

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt