"""
Test suite for PawPal+ scheduling system.

Covers:
  - Task completion status
  - Pet task management
  - Sorting: priority order and chronological time order
  - Filtering: by completion status and by pet name
  - Recurring tasks: daily, weekly, as_needed
  - Scheduler: plan generation, time-slot assignment, skipping completed tasks
  - Conflict detection: overlapping intervals, exact adjacency, no conflicts
  - Edge cases: no tasks, no pets, budget exactly met, all tasks completed,
                unknown pet name, invalid field edit
"""
from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers — reused across multiple tests
# ---------------------------------------------------------------------------

def make_owner(minutes=90):
    owner = Owner(name="Jordan", available_minutes=minutes)
    return owner

def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", breed="Shiba Inu", age=3, energy_level="high")

def make_task(title="Walk", duration=20, priority="medium", category="exercise", frequency="daily"):
    return Task(title=title, duration_minutes=duration, priority=priority,
                category=category, frequency=frequency)


# ---------------------------------------------------------------------------
# 1. Task completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_starts_incomplete():
    """A freshly created task must not be marked complete."""
    assert make_task().completed is False


# ---------------------------------------------------------------------------
# 2. Pet task management
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


def test_remove_task_decreases_pet_task_count():
    """Removing a task from a Pet should decrease its task list by one."""
    pet = make_pet()
    task = make_task()
    pet.add_task(task)
    pet.remove_task(task)
    assert len(pet.tasks) == 0


def test_get_tasks_returns_copy():
    """Pet.get_tasks() should return a copy; mutating it must not affect the pet."""
    pet = make_pet()
    pet.add_task(make_task())
    copy = pet.get_tasks()
    copy.clear()
    assert len(pet.tasks) == 1   # original untouched


# ---------------------------------------------------------------------------
# 3. Sorting — priority order
# ---------------------------------------------------------------------------

def test_sort_by_priority_high_before_low():
    """sort_by_priority must place high-priority tasks before low-priority ones."""
    low  = make_task("Low task",  duration=10, priority="low")
    high = make_task("High task", duration=10, priority="high")
    result = Scheduler.sort_by_priority([low, high])
    assert result[0].priority == "high"
    assert result[1].priority == "low"


def test_sort_by_priority_same_priority_shortest_first():
    """Within the same priority tier, shorter tasks must come before longer ones."""
    short = make_task("Short", duration=5,  priority="high")
    long_ = make_task("Long",  duration=30, priority="high")
    result = Scheduler.sort_by_priority([long_, short])
    assert result[0].duration_minutes == 5
    assert result[1].duration_minutes == 30


def test_sort_by_priority_three_tiers():
    """Tasks across all three priority tiers must be ordered high → medium → low."""
    low    = make_task("L", duration=5, priority="low")
    medium = make_task("M", duration=5, priority="medium")
    high   = make_task("H", duration=5, priority="high")
    result = Scheduler.sort_by_priority([low, medium, high])
    assert [t.priority for t in result] == ["high", "medium", "low"]


# ---------------------------------------------------------------------------
# 4. Sorting — chronological time order
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological():
    """sort_by_time must return tasks ordered earliest to latest by HH:MM."""
    t1 = make_task("A"); t1.scheduled_time = "09:00"
    t2 = make_task("B"); t2.scheduled_time = "08:00"
    t3 = make_task("C"); t3.scheduled_time = "10:30"
    result = Scheduler.sort_by_time([t1, t2, t3])
    assert [t.scheduled_time for t in result] == ["08:00", "09:00", "10:30"]


def test_sort_by_time_unscheduled_tasks_go_last():
    """Tasks with no scheduled_time must sort after all timed tasks."""
    timed    = make_task("Timed");    timed.scheduled_time = "08:00"
    untimed  = make_task("Untimed");  untimed.scheduled_time = None
    result = Scheduler.sort_by_time([untimed, timed])
    assert result[0].scheduled_time == "08:00"
    assert result[1].scheduled_time is None


def test_sort_by_time_all_unscheduled():
    """sort_by_time on a list where no task has a time must not raise an error."""
    tasks = [make_task(f"T{i}") for i in range(3)]   # all scheduled_time=None
    result = Scheduler.sort_by_time(tasks)
    assert len(result) == 3   # returned without crashing


# ---------------------------------------------------------------------------
# 5. Filtering
# ---------------------------------------------------------------------------

def test_filter_pending_excludes_completed():
    """filter_pending must not include tasks where completed=True."""
    done    = make_task("Done");    done.mark_complete()
    pending = make_task("Pending")
    result = Scheduler.filter_pending([done, pending])
    assert len(result) == 1
    assert result[0].title == "Pending"


def test_filter_completed_excludes_pending():
    """filter_completed must not include tasks where completed=False."""
    done    = make_task("Done");    done.mark_complete()
    pending = make_task("Pending")
    result = Scheduler.filter_completed([done, pending])
    assert len(result) == 1
    assert result[0].title == "Done"


def test_filter_by_pet_returns_correct_tasks():
    """filter_by_pet must return only tasks belonging to the named pet."""
    owner = make_owner()
    mochi = make_pet("Mochi")
    luna  = make_pet("Luna")
    mochi.add_task(make_task("Walk"))
    luna.add_task(make_task("Feed"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    result = Scheduler.filter_by_pet(owner, "Mochi")
    assert len(result) == 1
    assert result[0].title == "Walk"


def test_filter_by_pet_unknown_name_returns_empty():
    """filter_by_pet with a name that does not exist must return an empty list."""
    owner = make_owner()
    owner.add_pet(make_pet("Mochi"))
    result = Scheduler.filter_by_pet(owner, "Rex")
    assert result == []


# ---------------------------------------------------------------------------
# 6. Recurring tasks
# ---------------------------------------------------------------------------

def test_daily_task_next_occurrence_due_tomorrow():
    """A daily task's next_occurrence must have due_date = today + 1 day."""
    task = make_task(frequency="daily")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == str(date.today() + timedelta(days=1))


def test_weekly_task_next_occurrence_due_in_seven_days():
    """A weekly task's next_occurrence must have due_date = today + 7 days."""
    task = make_task(frequency="weekly")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == str(date.today() + timedelta(weeks=1))


def test_as_needed_task_has_no_next_occurrence():
    """An as_needed task's next_occurrence must return None."""
    task = make_task(frequency="as_needed")
    assert task.next_occurrence() is None


def test_next_occurrence_is_not_completed():
    """The new task returned by next_occurrence must start as incomplete."""
    task = make_task(frequency="daily")
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task.completed is False


def test_next_occurrence_copies_attributes():
    """next_occurrence must preserve the original task's title, duration, and priority."""
    task = make_task(title="Med", duration=10, priority="high", frequency="daily")
    next_task = task.next_occurrence()
    assert next_task.title == "Med"
    assert next_task.duration_minutes == 10
    assert next_task.priority == "high"


def test_complete_task_adds_next_occurrence_to_pet():
    """Scheduler.complete_task must append the next occurrence to the pet's task list."""
    owner = make_owner()
    pet   = make_pet()
    task  = make_task(frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    before = len(pet.tasks)
    scheduler.complete_task(task, pet)
    assert len(pet.tasks) == before + 1


def test_complete_task_as_needed_does_not_add_to_pet():
    """Scheduler.complete_task on an as_needed task must not add anything to the pet."""
    owner = make_owner()
    pet   = make_pet()
    task  = make_task(frequency="as_needed")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    before = len(pet.tasks)
    scheduler.complete_task(task, pet)
    assert len(pet.tasks) == before   # no new task added


# ---------------------------------------------------------------------------
# 7. Scheduler — plan generation
# ---------------------------------------------------------------------------

def test_generate_plan_schedules_pending_tasks():
    """generate_plan must schedule all pending tasks that fit in the time budget."""
    owner = make_owner(minutes=60)
    pet   = make_pet()
    pet.add_task(make_task("A", duration=20, priority="high"))
    pet.add_task(make_task("B", duration=20, priority="medium"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert len(plan.scheduled_tasks) == 2


def test_generate_plan_skips_completed_tasks():
    """generate_plan must not include tasks where completed=True."""
    owner = make_owner()
    pet   = make_pet()
    done  = make_task("Done", duration=10, priority="high")
    done.mark_complete()
    pet.add_task(done)
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert len(plan.scheduled_tasks) == 0


def test_generate_plan_task_too_long_goes_to_unscheduled():
    """A task whose duration exceeds the time budget must land in unscheduled_tasks."""
    owner = make_owner(minutes=10)
    pet   = make_pet()
    pet.add_task(make_task("Marathon", duration=120, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert len(plan.scheduled_tasks) == 0
    assert len(plan.unscheduled_tasks) == 1


def test_generate_plan_assigns_time_slots():
    """Every scheduled task must have a non-None scheduled_time after generate_plan."""
    owner = make_owner()
    pet   = make_pet()
    pet.add_task(make_task("Walk", duration=30, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert all(t.scheduled_time is not None for t in plan.scheduled_tasks)


def test_generate_plan_time_slots_do_not_overlap():
    """Scheduled time slots must be sequential with no overlap."""
    owner = make_owner(minutes=90)
    pet   = make_pet()
    pet.add_task(make_task("A", duration=30, priority="high"))
    pet.add_task(make_task("B", duration=20, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    # Sort by time and verify each task starts exactly where the previous one ended
    sorted_tasks = Scheduler.sort_by_time(plan.scheduled_tasks)
    for i in range(1, len(sorted_tasks)):
        prev = sorted_tasks[i - 1]
        curr = sorted_tasks[i]
        prev_end = prev.scheduled_time  # HH:MM string comparison is sufficient here
        assert curr.scheduled_time > prev_end


def test_generate_plan_total_duration_matches_sum():
    """ActivityPlan.total_duration must equal the sum of all scheduled task durations."""
    owner = make_owner(minutes=90)
    pet   = make_pet()
    pet.add_task(make_task("A", duration=30, priority="high"))
    pet.add_task(make_task("B", duration=15, priority="medium"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    expected = sum(t.duration_minutes for t in plan.scheduled_tasks)
    assert plan.total_duration == expected


# ---------------------------------------------------------------------------
# 8. Edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_pet_with_no_tasks():
    """generate_plan must return an empty plan when a pet has no tasks."""
    owner = make_owner()
    owner.add_pet(make_pet())
    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.unscheduled_tasks == []


def test_generate_plan_owner_with_no_pets():
    """generate_plan must return an empty plan when the owner has no pets."""
    plan = Scheduler(make_owner()).generate_plan()
    assert plan.scheduled_tasks == []


def test_generate_plan_all_tasks_completed():
    """generate_plan must produce an empty scheduled list when all tasks are done."""
    owner = make_owner()
    pet   = make_pet()
    for _ in range(3):
        t = make_task(); t.mark_complete(); pet.add_task(t)
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks == []


def test_task_edit_invalid_field_raises():
    """Task.edit with an unrecognised field name must raise ValueError."""
    task = make_task()
    with pytest.raises(ValueError):
        task.edit("nonexistent_field", "oops")


def test_task_edit_valid_field_updates_value():
    """Task.edit with a valid field must update that attribute."""
    task = make_task(priority="low")
    task.edit("priority", "high")
    assert task.priority == "high"


# ---------------------------------------------------------------------------
# 9. Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_overlapping_tasks():
    """Two tasks whose time intervals overlap must be returned as a conflicting pair.

    Example:  Task A runs 08:00 → 08:30 (30 min)
              Task B runs 08:15 → 08:45 (30 min)
    B starts before A finishes, so they conflict.
    """
    a = make_task("A", duration=30); a.scheduled_time = "08:00"
    b = make_task("B", duration=30); b.scheduled_time = "08:15"   # starts 15 min into A
    conflicts = Scheduler.detect_conflicts([a, b])
    assert len(conflicts) == 1
    assert (a, b) in conflicts


def test_detect_conflicts_adjacent_tasks_do_not_conflict():
    """Tasks that are back-to-back (one ends exactly when the next starts) must NOT conflict.

    Example:  Task A runs 08:00 → 08:30
              Task B runs 08:30 → 09:00
    They share the boundary but do not overlap.
    """
    a = make_task("A", duration=30); a.scheduled_time = "08:00"
    b = make_task("B", duration=30); b.scheduled_time = "08:30"
    conflicts = Scheduler.detect_conflicts([a, b])
    assert conflicts == []


def test_detect_conflicts_no_overlap():
    """Tasks with clearly separate time slots must produce no conflicts."""
    a = make_task("A", duration=20); a.scheduled_time = "08:00"
    b = make_task("B", duration=20); b.scheduled_time = "09:00"
    assert Scheduler.detect_conflicts([a, b]) == []


def test_detect_conflicts_exact_same_start_time():
    """Two tasks starting at exactly the same time are a conflict."""
    a = make_task("A", duration=15); a.scheduled_time = "09:00"
    b = make_task("B", duration=10); b.scheduled_time = "09:00"
    conflicts = Scheduler.detect_conflicts([a, b])
    assert len(conflicts) == 1


def test_detect_conflicts_skips_unscheduled_tasks():
    """Tasks with no scheduled_time must be ignored by detect_conflicts."""
    a = make_task("A", duration=30); a.scheduled_time = "08:00"
    b = make_task("B", duration=30); b.scheduled_time = None    # no time assigned
    conflicts = Scheduler.detect_conflicts([a, b])
    assert conflicts == []


def test_detect_conflicts_generate_plan_produces_no_conflicts():
    """A plan built by generate_plan must never contain conflicting time slots."""
    owner = make_owner(minutes=120)
    pet   = make_pet()
    pet.add_task(make_task("A", duration=30, priority="high"))
    pet.add_task(make_task("B", duration=20, priority="high"))
    pet.add_task(make_task("C", duration=15, priority="medium"))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert Scheduler.detect_conflicts(plan.scheduled_tasks) == []
