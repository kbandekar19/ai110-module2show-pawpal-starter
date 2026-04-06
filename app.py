import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialisation
# st.session_state is a dictionary that survives reruns. The "not in" guard
# means each key is only initialised once; every later rerun finds it already
# there and skips the block, so our objects are never accidentally reset.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None       # Owner object — set when user saves info

if "pet" not in st.session_state:
    st.session_state.pet = None         # Pet object — tasks live on this object

if "plan" not in st.session_state:
    st.session_state.plan = None        # ActivityPlan — populated on "Generate"

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None   # Scheduler — kept so explain_plan() works

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Section 1: Owner & Pet information
# Wired to: Owner.__init__, Pet.__init__, Owner.add_pet()
# ---------------------------------------------------------------------------
st.subheader("1. Owner & Pet Information")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=90
    )
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    energy_level = st.selectbox("Energy level", ["low", "medium", "high"], index=1)

if st.button("Save owner & pet"):
    # Build the objects using our class constructors, then link them.
    # owner.add_pet(pet) is the method that registers the pet under the owner,
    # which is exactly what Scheduler.generate_plan() later reads via
    # owner.get_all_tasks() -> pet.get_tasks().
    pet = Pet(name=pet_name, species=species, breed="", age=0, energy_level=energy_level)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)                  # <-- Owner.add_pet() called here

    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.plan = None        # reset plan when owner/pet changes
    st.success(f"Saved — {owner_name} with pet {pet_name} ({species}).")

# Show current pet profile if one exists
if st.session_state.pet is not None:
    with st.expander("Current pet profile"):
        st.json(st.session_state.pet.get_profile())   # <-- Pet.get_profile() called here

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task management
# Wired to: Task.__init__, Pet.add_task(), Pet.get_tasks(), Task.to_dict()
# ---------------------------------------------------------------------------
st.subheader("2. Add & Edit Tasks")

if st.session_state.pet is None:
    st.info("Save owner & pet info above before adding tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.selectbox(
            "Category", ["exercise", "feeding", "medical", "grooming", "enrichment"]
        )

    if st.button("Add task"):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
        )
        st.session_state.pet.add_task(new_task)   # <-- Pet.add_task() called here
        st.success(f"Added: {task_title}")
        st.session_state.plan = None              # stale plan is no longer valid

    # Read tasks directly from the Pet object — it is the single source of truth.
    # Pet.get_tasks() returns a copy of the internal list so the UI can't
    # accidentally mutate it.
    current_tasks = st.session_state.pet.get_tasks()   # <-- Pet.get_tasks() called here

    if current_tasks:
        st.write(f"Tasks for {st.session_state.pet.name}:")
        st.table([t.to_dict() for t in current_tasks])  # <-- Task.to_dict() called here
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# Wired to: Scheduler.__init__, Scheduler.generate_plan(), Scheduler.explain_plan()
#           ActivityPlan.get_summary(), ActivityPlan.scheduled_tasks / unscheduled_tasks
# ---------------------------------------------------------------------------
st.subheader("3. Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save owner & pet info first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Please add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)  # <-- Scheduler.__init__()
        plan = scheduler.generate_plan()               # <-- Scheduler.generate_plan()
        st.session_state.scheduler = scheduler
        st.session_state.plan = plan

if st.session_state.plan is not None:
    plan = st.session_state.plan
    scheduler = st.session_state.scheduler
    summary = plan.get_summary()                       # <-- ActivityPlan.get_summary()

    st.success(f"Schedule generated for {summary['date']}!")

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Tasks scheduled", summary["scheduled_count"])
    col_s2.metric("Time used (min)", summary["total_duration_minutes"])
    col_s3.metric("Time remaining (min)", summary["remaining_minutes"])

    if plan.scheduled_tasks:
        st.markdown("#### Scheduled tasks")
        st.table([t.to_dict() for t in plan.scheduled_tasks])

    if plan.unscheduled_tasks:
        st.markdown("#### Skipped (did not fit)")
        st.table([t.to_dict() for t in plan.unscheduled_tasks])

    with st.expander("Plan explanation"):
        st.text(scheduler.explain_plan())              # <-- Scheduler.explain_plan()
