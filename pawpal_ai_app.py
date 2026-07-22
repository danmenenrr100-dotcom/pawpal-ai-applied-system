"""Streamlit interface for the PawPal AI planning workflow."""

from datetime import time

import streamlit as st

from pawpal_ai.agent import PawPalAgent


st.set_page_config(
    page_title="PawPal AI",
    page_icon="🐾",
    layout="wide",
)


@st.cache_resource
def load_agent() -> PawPalAgent:
    """Create and cache the PawPal AI workflow."""

    return PawPalAgent()


if "pawpal_tasks" not in st.session_state:
    st.session_state.pawpal_tasks = []

if "pawpal_result" not in st.session_state:
    st.session_state.pawpal_result = None


st.title("🐾 PawPal AI")
st.caption(
    "A retrieval-grounded, safety-aware assistant for creating "
    "daily pet-care plans."
)

with st.sidebar:
    st.header("Planning Settings")

    pet_name = st.text_input(
        "Pet name",
        value="Max",
    )

    request = st.text_area(
        "What should PawPal AI plan?",
        value="Create a safe daily care plan for my pet.",
        height=100,
    )

    available_start = st.time_input(
        "Available start time",
        value=time(8, 0),
    )

    available_minutes = st.number_input(
        "Available minutes",
        min_value=1,
        max_value=720,
        value=120,
        step=15,
    )

    top_k = st.slider(
        "Knowledge sources to retrieve",
        min_value=1,
        max_value=10,
        value=4,
    )

st.subheader("1. Add a care task")

with st.form("add_task_form", clear_on_submit=True):
    first_column, second_column = st.columns(2)

    with first_column:
        task_name = st.text_input(
            "Task name",
            placeholder="Morning Walk",
        )

        duration = st.number_input(
            "Duration in minutes",
            min_value=1,
            max_value=240,
            value=15,
        )

        priority = st.selectbox(
            "Priority",
            options=["high", "medium", "low"],
            index=1,
        )

    with second_column:
        category = st.selectbox(
            "Task category",
            options=["Routine care", "Medication"],
        )

        has_fixed_time = st.checkbox(
            "This task has a fixed time"
        )

        fixed_time = st.time_input(
            "Fixed time",
            value=time(8, 0),
            disabled=not has_fixed_time,
        )

    medication_name = ""
    dosage = ""
    time_or_frequency = ""
    veterinarian_directions = ""

    if category == "Medication":
        st.info(
            "PawPal AI only schedules owner-provided prescription "
            "instructions. It does not calculate or recommend dosages."
        )

        medication_column, dosage_column = st.columns(2)

        with medication_column:
            medication_name = st.text_input(
                "Medication name"
            )

            dosage = st.text_input(
                "Exact prescribed dosage",
                placeholder="1 tablet or 5 mg",
            )

        with dosage_column:
            time_or_frequency = st.text_input(
                "Administration time or frequency",
                placeholder="8:00 AM or once each morning",
            )

            veterinarian_directions = st.text_input(
                "Veterinarian directions",
                placeholder="Follow the prescription label.",
            )

    add_task = st.form_submit_button(
        "Add task",
        type="primary",
        use_container_width=True,
    )

if add_task:
    if not task_name.strip():
        st.error("Enter a task name before adding the task.")
    else:
        new_task = {
            "name": task_name.strip(),
            "duration": int(duration),
            "priority": priority,
            "category": category.lower(),
        }

        if has_fixed_time:
            new_task["fixed_time"] = fixed_time.strftime(
                "%I:%M %p"
            )

        if category == "Medication":
            new_task.update(
                {
                    "medication_name": medication_name.strip(),
                    "dosage": dosage.strip(),
                    "time_or_frequency": (
                        time_or_frequency.strip()
                    ),
                    "veterinarian_directions": (
                        veterinarian_directions.strip()
                    ),
                }
            )

        st.session_state.pawpal_tasks.append(new_task)
        st.session_state.pawpal_result = None
        st.success(f"Added task: {task_name.strip()}")

st.subheader("2. Review tasks")

tasks = st.session_state.pawpal_tasks

if not tasks:
    st.info("Add at least one care task to create a plan.")
else:
    task_rows = []

    for task in tasks:
        task_rows.append(
            {
                "Task": task["name"],
                "Category": task.get("category", "routine care"),
                "Duration": f"{task['duration']} minutes",
                "Priority": task["priority"],
                "Fixed time": task.get("fixed_time", "Flexible"),
            }
        )

    st.dataframe(
        task_rows,
        hide_index=True,
        use_container_width=True,
    )

    remove_column, clear_column = st.columns(2)

    with remove_column:
        selected_task = st.selectbox(
            "Select a task to remove",
            options=range(len(tasks)),
            format_func=lambda index: tasks[index]["name"],
        )

        if st.button(
            "Remove selected task",
            use_container_width=True,
        ):
            removed_task = tasks.pop(selected_task)
            st.session_state.pawpal_result = None
            st.success(
                f"Removed task: {removed_task['name']}"
            )
            st.rerun()

    with clear_column:
        st.write("")
        st.write("")

        if st.button(
            "Clear all tasks",
            use_container_width=True,
        ):
            st.session_state.pawpal_tasks = []
            st.session_state.pawpal_result = None
            st.rerun()

st.subheader("3. Generate the AI care plan")

generate_plan = st.button(
    "Generate validated plan",
    type="primary",
    disabled=not bool(tasks),
    use_container_width=True,
)

if generate_plan:
    try:
        agent = load_agent()

        with st.spinner(
            "Retrieving evidence and validating the plan..."
        ):
            st.session_state.pawpal_result = agent.run(
                request=request,
                tasks=tasks,
                pet_name=pet_name.strip() or None,
                available_start=available_start.strftime(
                    "%I:%M %p"
                ),
                available_minutes=int(available_minutes),
                top_k=top_k,
            )
    except (TypeError, ValueError) as error:
        st.error(str(error))
    except Exception as error:
        st.error(
            "PawPal AI could not generate the plan. "
            f"Details: {error}"
        )

result = st.session_state.pawpal_result

if result is not None:
    st.subheader("Plan Result")

    if result.status == "completed":
        st.success("The care plan passed all validation checks.")
    elif result.status == "completed_with_limits":
        st.warning(
            "A safe plan was created, but some tasks were blocked "
            "or deferred."
        )
    elif result.status == "urgent":
        st.error(
            "PawPal AI detected a potentially urgent veterinary issue."
        )
    else:
        st.error(
            f"The workflow ended with status: {result.status}"
        )

    for message in result.messages:
        st.write(f"- {message}")

    if result.plan:
        plan_rows = [
            {
                "Start": item.start_time,
                "End": item.end_time,
                "Task": item.task_name,
                "Duration": f"{item.duration_minutes} minutes",
                "Priority": item.priority.title(),
                "Reason": item.reason,
            }
            for item in result.plan
        ]

        st.dataframe(
            plan_rows,
            hide_index=True,
            use_container_width=True,
        )

    if result.blocked_tasks:
        with st.expander(
            f"Blocked tasks ({len(result.blocked_tasks)})",
            expanded=True,
        ):
            for issue in result.blocked_tasks:
                st.warning(
                    f"**{issue.task_name}:** {issue.reason}"
                )

    if result.deferred_tasks:
        with st.expander(
            f"Deferred tasks ({len(result.deferred_tasks)})",
            expanded=True,
        ):
            for issue in result.deferred_tasks:
                st.info(
                    f"**{issue.task_name}:** {issue.reason}"
                )

    with st.expander("Retrieved citations"):
        if result.citations:
            for citation in result.citations:
                st.write(f"- {citation}")
        else:
            st.write("No citations were retrieved.")

    with st.expander("Agent workflow trace"):
        trace_rows = [
            {
                "Action": step.action,
                "Status": step.status,
                "Details": step.detail,
            }
            for step in result.trace
        ]

        st.dataframe(
            trace_rows,
            hide_index=True,
            use_container_width=True,
        )

        st.write(
            "Revision attempted:",
            "Yes" if result.revision_attempted else "No",
        )

st.divider()
st.caption(
    "PawPal AI supports routine scheduling only. "
    "Contact a veterinarian for diagnosis, dosage decisions, "
    "medication changes, or emergencies."
)