from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90, preferences={"prefers_morning": True})

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3, energy_level="high")
luna = Pet(name="Luna", species="cat", breed="Domestic Shorthair", age=5, energy_level="low")

owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks added intentionally out of priority/time order to test sorting
mochi.add_task(Task("Fetch / play session", duration_minutes=20, priority="medium", category="enrichment"))
mochi.add_task(Task("Morning walk",         duration_minutes=30, priority="high",   category="exercise"))
mochi.add_task(Task("Administer flea medicine", duration_minutes=10, priority="high", category="medical"))

luna.add_task(Task("Laser pointer play",    duration_minutes=10, priority="medium", category="enrichment"))
luna.add_task(Task("Brushing",              duration_minutes=15, priority="low",    category="grooming"))
luna.add_task(Task("Breakfast feeding",     duration_minutes=5,  priority="high",   category="feeding"))

# Mark one task complete so generate_plan() skips it (improvement D)
mochi.tasks[0].mark_complete()   # "Fetch / play session" already done

# --- Generate plan (starts at 08:00 by default) ---
scheduler = Scheduler(owner, start_time="08:00")
plan = scheduler.generate_plan()

# --- Helper for printing task rows ---
def print_tasks(tasks):
    if not tasks:
        print("    (none)")
        return
    print(f"    {'TIME':<8} {'TASK':<30} {'DUR':>5}  {'PRI':<8}  {'DONE'}")
    print("    " + "-" * 62)
    for t in tasks:
        time_label = t.scheduled_time or "--:--"
        done = "yes" if t.completed else "no"
        print(f"    {time_label:<8} {t.title:<30} {t.duration_minutes:>4}m  {t.priority:<8}  {done}")

# --- Display schedule ---
print("\n" + "=" * 60)
print(f"  TODAY'S SCHEDULE  --  {plan.date}")
print(f"  Owner: {owner.name}  |  Budget: {owner.available_minutes} min")
print("=" * 60)
print_tasks(plan.scheduled_tasks)
summary = plan.get_summary()
print(f"\n  Scheduled: {summary['scheduled_count']} tasks  |  "
      f"Used: {summary['total_duration_minutes']} min  |  "
      f"Remaining: {summary['remaining_minutes']} min")

if plan.unscheduled_tasks:
    print("\n  SKIPPED:")
    for t in plan.unscheduled_tasks:
        print(f"    - {t.title} ({t.duration_minutes} min)")

# --- sort_by_time demo ---
print("\n" + "=" * 60)
print("  SORT BY TIME (scheduled tasks in chronological order)")
print("=" * 60)
sorted_by_time = Scheduler.sort_by_time(plan.scheduled_tasks)
print_tasks(sorted_by_time)

# --- filter_by_pet demo ---
print("\n" + "=" * 60)
print("  FILTER BY PET: Mochi only")
print("=" * 60)
mochi_tasks = Scheduler.filter_by_pet(owner, "Mochi")
print_tasks(mochi_tasks)

print("\n" + "=" * 60)
print("  FILTER BY PET: Luna only")
print("=" * 60)
luna_tasks = Scheduler.filter_by_pet(owner, "Luna")
print_tasks(luna_tasks)

# --- filter_pending / filter_completed demo ---
print("\n" + "=" * 60)
print("  FILTER: Pending tasks only (across all pets)")
print("=" * 60)
pending = Scheduler.filter_pending(owner.get_all_tasks())
print_tasks(pending)

print("\n" + "=" * 60)
print("  FILTER: Completed tasks only (across all pets)")
print("=" * 60)
done = Scheduler.filter_completed(owner.get_all_tasks())
print_tasks(done)

print("\n" + "=" * 60)
print("  PLAN EXPLANATION")
print("=" * 60)
for line in scheduler.explain_plan().splitlines()[2:]:
    print(f"  {line}")
print("=" * 60 + "\n")

# --- Recurring task demo ---
print("=" * 60)
print("  RECURRING TASK DEMO")
print("=" * 60)

walk = next(t for t in mochi.get_tasks() if t.title == "Morning walk")
flea = next(t for t in mochi.get_tasks() if t.title == "Administer flea medicine")
flea.edit("frequency", "weekly")   # make flea medicine weekly instead of daily

print(f"  Completing '{walk.title}' (frequency: {walk.frequency})")
next_walk = scheduler.complete_task(walk, mochi)
if next_walk:
    print(f"  --> Next occurrence created: '{next_walk.title}' due {next_walk.due_date}")

print(f"\n  Completing '{flea.title}' (frequency: {flea.frequency})")
next_flea = scheduler.complete_task(flea, mochi)
if next_flea:
    print(f"  --> Next occurrence created: '{next_flea.title}' due {next_flea.due_date}")

print(f"\n  Completing 'Breakfast feeding' (frequency: as_needed)")
feeding = next(t for t in luna.get_tasks() if t.title == "Breakfast feeding")
feeding.edit("frequency", "as_needed")
next_feeding = scheduler.complete_task(feeding, luna)
if next_feeding is None:
    print(f"  --> No next occurrence (as_needed tasks are not auto-rescheduled)")

print(f"\n  Mochi's tasks after completions ({len(mochi.get_tasks())} total):")
print_tasks(mochi.get_tasks())
print("=" * 60 + "\n")
