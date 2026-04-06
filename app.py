import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "plan" not in st.session_state:
    st.session_state.plan = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRIORITY_COLOUR = {"high": "🔴", "medium": "🟡", "low": "🟢"}

def tasks_to_rows(tasks):
    """Convert a list of Task objects into display-friendly dicts."""
    rows = []
    for t in tasks:
        rows.append({
            "Time": t.scheduled_time or "--:--",
            "Task": t.title,
            "Duration": f"{t.duration_minutes} min",
            "Priority": f"{PRIORITY_COLOUR.get(t.priority, '')} {t.priority}",
            "Category": t.category,
            "Frequency": t.frequency,
            "Done": "Yes" if t.completed else "No",
        })
    return rows


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("PawPal+")
st.caption("A smart daily planner for pet owners.")
st.divider()

# ---------------------------------------------------------------------------
# Section 1: Owner & Pet information
# ---------------------------------------------------------------------------
st.subheader("1. Owner & Pet Information")

col_a, col_b = st.columns(2)
with col_a:
    owner_name       = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)
with col_b:
    pet_name     = st.text_input("Pet name", value="Mochi")
    species      = st.selectbox("Species", ["dog", "cat", "other"])
    energy_level = st.selectbox("Energy level", ["low", "medium", "high"], index=1)

if st.button("Save owner & pet", type="primary"):
    pet   = Pet(name=pet_name, species=species, breed="", age=0, energy_level=energy_level)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner    = owner
    st.session_state.pet      = pet
    st.session_state.plan     = None
    st.session_state.scheduler = None
    st.success(f"Saved — {owner_name} with pet {pet_name} ({species}).")

if st.session_state.pet is not None:
    with st.expander("Pet profile"):
        st.json(st.session_state.pet.get_profile())

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task management
# ---------------------------------------------------------------------------
st.subheader("2. Add Tasks")

if st.session_state.pet is None:
    st.info("Save owner & pet info above before adding tasks.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.selectbox("Category", ["exercise", "feeding", "medical", "grooming", "enrichment"])
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])

    if st.button("Add task"):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            frequency=frequency,
        )
        st.session_state.pet.add_task(new_task)
        st.session_state.plan = None   # stale plan no longer valid
        st.success(f"Added: {task_title}")

    # --- Task list with filtering ---
    current_tasks = st.session_state.pet.get_tasks()

    if current_tasks:
        filter_col1, filter_col2 = st.columns([1, 3])
        with filter_col1:
            status_filter = st.radio("Show", ["All", "Pending", "Completed"], horizontal=True)

        if status_filter == "Pending":
            display_tasks = Scheduler.filter_pending(current_tasks)
        elif status_filter == "Completed":
            display_tasks = Scheduler.filter_completed(current_tasks)
        else:
            display_tasks = current_tasks

        if display_tasks:
            st.dataframe(tasks_to_rows(display_tasks), use_container_width=True, hide_index=True)
        else:
            st.info(f"No {status_filter.lower()} tasks.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Build schedule
# ---------------------------------------------------------------------------
st.subheader("3. Build Schedule")

start_time = st.text_input("Schedule start time (HH:MM)", value="08:00")

if st.button("Generate schedule", type="primary"):
    if st.session_state.owner is None:
        st.warning("Please save owner & pet info first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Please add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner, start_time=start_time)
        plan      = scheduler.generate_plan()
        st.session_state.scheduler = scheduler
        st.session_state.plan      = plan

if st.session_state.plan is not None:
    plan      = st.session_state.plan
    scheduler = st.session_state.scheduler
    summary   = plan.get_summary()

    # --- Summary metrics ---
    st.success(f"Schedule generated for **{summary['date']}**")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tasks scheduled",    summary["scheduled_count"])
    m2.metric("Tasks skipped",      summary["unscheduled_count"])
    m3.metric("Time used (min)",    summary["total_duration_minutes"])
    m4.metric("Time remaining (min)", summary["remaining_minutes"])

    # --- Medication alert (needs_medication) ---
    if scheduler.needs_medication():
        st.warning("Medication reminder: one or more medical tasks are in today's plan. Make sure to complete them.")

    # --- Conflict detection ---
    conflicts = Scheduler.detect_conflicts(plan.scheduled_tasks)
    if conflicts:
        st.error(
            f"Schedule conflict detected — {len(conflicts)} overlapping task pair(s). "
            "Review the times below and adjust durations or task order."
        )
        for task_a, task_b in conflicts:
            st.error(
                f"  Conflict: **{task_a.title}** ({task_a.scheduled_time}, {task_a.duration_minutes} min) "
                f"overlaps with **{task_b.title}** ({task_b.scheduled_time}, {task_b.duration_minutes} min)"
            )
    else:
        st.success("No scheduling conflicts detected.")

    # --- Scheduled tasks sorted chronologically ---
    if plan.scheduled_tasks:
        st.markdown("#### Today's plan (chronological order)")
        sorted_tasks = Scheduler.sort_by_time(plan.scheduled_tasks)
        st.dataframe(tasks_to_rows(sorted_tasks), use_container_width=True, hide_index=True)

    # --- Skipped tasks ---
    if plan.unscheduled_tasks:
        st.markdown("#### Skipped — did not fit in available time")
        st.dataframe(tasks_to_rows(plan.unscheduled_tasks), use_container_width=True, hide_index=True)

    # --- Plan explanation ---
    with st.expander("Why were these tasks chosen? (Plan explanation)"):
        st.text(scheduler.explain_plan())
