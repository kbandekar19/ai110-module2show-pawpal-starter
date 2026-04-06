from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90, preferences={"prefers_morning": True})

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3, energy_level="high")
luna = Pet(name="Luna", species="cat", breed="Domestic Shorthair", age=5, energy_level="low")

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks for Mochi ---
mochi.add_task(Task("Morning walk",      duration_minutes=30, priority="high",   category="exercise"))
mochi.add_task(Task("Administer flea medicine", duration_minutes=10, priority="high", category="medical"))
mochi.add_task(Task("Fetch / play session", duration_minutes=20, priority="medium", category="enrichment"))

# --- Tasks for Luna ---
luna.add_task(Task("Breakfast feeding",  duration_minutes=5,  priority="high",   category="feeding"))
luna.add_task(Task("Brushing",           duration_minutes=15, priority="low",    category="grooming"))
luna.add_task(Task("Laser pointer play", duration_minutes=10, priority="medium", category="enrichment"))

# --- Generate plan ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

# --- Display ---
print("\n" + "=" * 50)
print(f"  TODAY'S SCHEDULE  —  {plan.date}")
print(f"  Owner : {owner.name}  |  Time budget: {owner.available_minutes} min")
print("=" * 50)

if plan.scheduled_tasks:
    print(f"\n{'TASK':<30} {'DURATION':>10}  {'PRIORITY':<8}  {'CATEGORY'}")
    print("-" * 65)
    for task in plan.scheduled_tasks:
        print(f"  {task.title:<28} {task.duration_minutes:>7} min  {task.priority:<8}  {task.category}")
else:
    print("  No tasks could be scheduled.")

summary = plan.get_summary()
print("-" * 65)
print(f"  Scheduled: {summary['scheduled_count']} tasks  |  "
      f"Time used: {summary['total_duration_minutes']} min  |  "
      f"Time remaining: {summary['remaining_minutes']} min")

if plan.unscheduled_tasks:
    print("\n  SKIPPED (didn't fit in available time):")
    for task in plan.unscheduled_tasks:
        print(f"    ✗  {task.title} ({task.duration_minutes} min)")

print("\n  PLAN EXPLANATION:")
print("-" * 65)
for line in scheduler.explain_plan().splitlines()[2:]:
    print(f"  {line}")

print("=" * 50 + "\n")
