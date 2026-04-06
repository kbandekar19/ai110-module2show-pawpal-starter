# PawPal+

A smart daily pet care planner built with Python and Streamlit. PawPal+ helps busy pet owners stay consistent with pet care by generating a prioritized, time-slotted schedule and automatically managing recurring tasks.

---

## Features

### Core user actions
- **Enter owner & pet information** — capture the owner's daily time budget and pet profile (species, breed, age, energy level)
- **Add and edit tasks** — create care tasks with title, duration, priority, category, and recurrence frequency; filter the task list by status (All / Pending / Completed)
- **Generate a daily schedule** — one click produces a fully sorted, time-slotted activity plan based on constraints

### Scheduling algorithms
- **Priority + duration sorting** — tasks are sorted high → medium → low priority; within the same tier, shorter tasks are scheduled first so more tasks fit inside the available time window (`Scheduler.sort_by_priority`)
- **Real time-slot assignment** — the scheduler walks a clock forward from a configurable start time (default `08:00`), stamping each accepted task with an `HH:MM` start time (`Scheduler.generate_plan`)
- **Chronological display** — the generated plan is re-sorted by `HH:MM` before display so the UI always reads top-to-bottom as an actual timeline (`Scheduler.sort_by_time`)
- **Conflict detection** — after plan generation, the app checks every pair of scheduled tasks for overlapping intervals and surfaces a named, actionable `st.error` if any are found (`Scheduler.detect_conflicts`)
- **Completed-task filtering** — already-done tasks are automatically excluded from plan generation; pending and completed views are available in the task list (`Scheduler.filter_pending`, `filter_completed`)
- **Recurring task automation** — marking a daily task complete auto-creates the next occurrence due tomorrow; weekly tasks create one due in 7 days; `as_needed` tasks are not rescheduled (`Task.next_occurrence`, `Scheduler.complete_task`)
- **Medication alert** — if any pending task is categorised as `medical`, a persistent amber banner reminds the owner before they leave the schedule view (`Scheduler.needs_medication`)

### System design
- Five classes with clear responsibilities: `Task`, `Pet`, `Owner`, `Scheduler`, `ActivityPlan`
- `Owner` is the single data hub — `Scheduler` retrieves all tasks via `owner.get_all_tasks()` without reaching into `Pet` directly
- 39 automated tests covering sorting, filtering, recurrence, plan generation, conflict detection, and edge cases

---

## Demo

![PawPal+ Dashboard](images/pawpal_screenshot.png)

## System Design (UML)

![PawPal+ UML Class Diagram](images/uml_final.png)

---

## Smarter Scheduling

The scheduling logic in `pawpal_system.py` goes beyond a simple sorted list. Four algorithmic improvements make it more useful for real pet care:

**Priority + duration sorting**
Tasks are sorted high-to-low by priority. Within the same priority tier, shorter tasks are scheduled first so more tasks fit inside the available time budget. This is handled by `Scheduler.sort_by_priority()` using a two-key lambda: `(-priority_rank, duration_minutes)`.

**Real time slots**
`Scheduler.generate_plan()` walks a clock forward from a configurable start time (default `08:00`). Each accepted task is stamped with an `HH:MM` start time so the output reads as an actual schedule rather than an ordered list. `Scheduler.sort_by_time()` can then re-sort any task list chronologically using string comparison on the `HH:MM` format.

**Filtering**
`Scheduler.filter_pending()` and `Scheduler.filter_completed()` split tasks by completion status. `Scheduler.filter_by_pet()` and `Owner.get_tasks_for(pet_name)` isolate tasks for a specific pet. Completed tasks are automatically excluded from plan generation.

**Recurring tasks**
`Task.next_occurrence()` uses Python's `timedelta` to compute the next due date — `+1 day` for daily tasks, `+7 days` for weekly tasks, and `None` for `as_needed` tasks. `Scheduler.complete_task(task, pet)` marks a task done and immediately registers the next occurrence on the pet, so it appears in the following day's generated plan with no manual intervention.

---

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

39 automated tests across 9 areas:

| Area | What is verified |
|---|---|
| Task completion | `mark_complete()` flips status; new tasks start incomplete |
| Pet task management | `add_task`, `remove_task`, and `get_tasks()` returns a safe copy |
| Priority sorting | High before low; same-priority tasks ordered shortest-first; all 3 tiers correct |
| Time sorting | Chronological HH:MM order; unscheduled tasks sort to end; all-None list does not crash |
| Filtering | Pending/completed split; filter by pet name; unknown pet name returns `[]` |
| Recurring tasks | Daily +1 day, weekly +7 days, `as_needed` → None; fresh copy starts incomplete; attributes preserved |
| Plan generation | Pending tasks scheduled; completed skipped; overlong tasks go to unscheduled; time slots assigned; `total_duration` stays in sync |
| Conflict detection | Overlapping intervals flagged; adjacent tasks not flagged; same start time caught; unscheduled tasks ignored; scheduler output is always conflict-free |
| Edge cases | No tasks, no pets, all done → empty plan; invalid `edit` field raises `ValueError` |

### Confidence level

**4 / 5 stars**

The core scheduling logic — priority sorting, time-slot assignment, recurring task creation, and conflict detection — is fully covered by automated tests and all 39 pass. The one star withheld reflects areas not yet tested: owner preference handling has no tests, the Streamlit UI layer is untested (no browser automation), and recurring task behaviour across multiple days has not been exercised. These would be the next tests to write.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run tests

```bash
python -m pytest
```

### Project structure

```
pawpal_system.py   — all classes and scheduling logic
app.py             — Streamlit UI
main.py            — CLI demo script
tests/
  test_pawpal.py   — 39 automated tests
uml_final.md       — final Mermaid.js class diagram
reflection.md      — design decisions and project reflection
```
