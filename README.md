# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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
| Time sorting | Chronological HH:MM order; unscheduled tasks sort to end; all-None list doesn't crash |
| Filtering | Pending/completed split; filter by pet name; unknown pet name returns `[]` |
| Recurring tasks | Daily +1 day, weekly +7 days, `as_needed` → None; fresh copy starts incomplete; attributes preserved |
| Plan generation | Pending tasks scheduled; completed skipped; overlong tasks go to unscheduled; time slots assigned; `total_duration` stays in sync |
| Conflict detection | Overlapping intervals flagged; adjacent tasks not flagged; same start time caught; unscheduled tasks ignored; scheduler's own output is always conflict-free |
| Edge cases | No tasks, no pets, all done → empty plan; invalid `edit` field raises `ValueError` |

### Confidence level

**4 / 5 stars**

The core scheduling logic — priority sorting, time-slot assignment, recurring task creation, and conflict detection — is fully covered by automated tests and all 39 pass. The one star withheld reflects areas not yet tested: owner preference handling has no tests, the Streamlit UI layer is untested (no browser automation), and recurring task behaviour across multiple days (e.g. a weekly task completing twice in one week) has not been exercised. These would be the next tests to write.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
