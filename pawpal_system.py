from datetime import date as _date, timedelta as _timedelta

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
EDITABLE_FIELDS = {"title", "duration_minutes", "priority", "category", "notes", "frequency"}

# Default time the day's schedule starts (08:00)
DEFAULT_START_TIME = "08:00"


def _time_to_minutes(hhmm: str) -> int:
    """Convert a 'HH:MM' string to total minutes since midnight."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _minutes_to_time(total: int) -> str:
    """Convert total minutes since midnight back to a 'HH:MM' string."""
    return f"{total // 60:02d}:{total % 60:02d}"


class Task:
    """A single pet care activity."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str,
        frequency: str = "daily",
        notes: str = "",
    ):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low" | "medium" | "high"
        self.category = category          # e.g. "exercise", "feeding", "medical", "grooming"
        self.frequency = frequency        # "daily" | "weekly" | "as_needed"
        self.notes = notes
        self.scheduled_time: str | None = None   # "HH:MM" once assigned by Scheduler
        self.completed: bool = False
        self.due_date: str = str(_date.today())   # "YYYY-MM-DD", defaults to today

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a new Task for the next occurrence, or None if frequency is 'as_needed'.

        Uses timedelta to calculate the next due date:
          - 'daily'  → today + 1 day
          - 'weekly' → today + 7 days
        The returned task is a fresh copy with completed=False and no scheduled_time,
        so it will be picked up naturally by the next call to generate_plan().
        """
        if self.frequency == "as_needed":
            return None
        delta = _timedelta(days=1) if self.frequency == "daily" else _timedelta(weeks=1)
        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            notes=self.notes,
        )
        next_task.due_date = str(_date.today() + delta)
        return next_task

    def edit(self, field: str, value) -> None:
        """Update a single editable field; raises ValueError for unknown fields."""
        if field not in EDITABLE_FIELDS:
            raise ValueError(f"'{field}' is not an editable field. Choose from: {EDITABLE_FIELDS}")
        setattr(self, field, value)

    def to_dict(self) -> dict:
        """Return all task attributes as a plain dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "frequency": self.frequency,
            "notes": self.notes,
            "due_date": self.due_date,
            "scheduled_time": self.scheduled_time,
            "completed": self.completed,
        }

    def __repr__(self) -> str:
        return f"Task('{self.title}', {self.duration_minutes}min, priority={self.priority})"


class Pet:
    """Stores a pet's profile and its associated care tasks."""

    def __init__(
        self,
        name: str,
        species: str,
        breed: str,
        age: int,
        energy_level: str,
        health_notes: str = "",
    ):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.energy_level = energy_level  # "low" | "medium" | "high"
        self.health_notes = health_notes
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)

    def get_profile(self) -> dict:
        """Return this pet's profile attributes as a plain dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "energy_level": self.energy_level,
            "health_notes": self.health_notes,
            "task_count": len(self.tasks),
        }

    def __repr__(self) -> str:
        return f"Pet('{self.name}', {self.species})"


class Owner:
    """Manages owner info and a collection of pets."""

    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's roster."""
        self.pets.remove(pet)

    def get_available_time(self) -> int:
        """Return the owner's total available minutes for the day."""
        return self.available_minutes

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preference key-value pairs into the existing preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_tasks_for(self, pet_name: str) -> list[Task]:
        """Return tasks belonging to a specific pet, matched by name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across every pet."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all completed tasks across every pet."""
        return [task for task in self.get_all_tasks() if task.completed]

    def __repr__(self) -> str:
        return f"Owner('{self.name}', pets={len(self.pets)})"


class ActivityPlan:
    """The output of the Scheduler — an ordered daily plan."""

    def __init__(self, date: str, owner: Owner):
        self.date = date
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.unscheduled_tasks: list[Task] = []
        self.total_duration: int = 0

    def add_task(self, task: Task) -> None:
        """Add a task to the plan and update the total duration."""
        self.scheduled_tasks.append(task)
        self.total_duration += task.duration_minutes

    def remove_task(self, task: Task) -> None:
        """Remove a task from the plan and update the total duration."""
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            self.total_duration -= task.duration_minutes
            task.scheduled_time = None

    def display(self) -> str:
        """Return a formatted string representation of the full daily plan."""
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.date}."
        lines = [f"Activity Plan for {self.owner.name} -- {self.date}", "=" * 45]
        for task in self.scheduled_tasks:
            time_label = task.scheduled_time or "unassigned"
            lines.append(f"  [{time_label}] {task.title} ({task.duration_minutes} min) [{task.priority}]")
        lines.append(f"\nTotal time: {self.total_duration} min")
        if self.unscheduled_tasks:
            lines.append("\nSkipped (didn't fit):")
            for task in self.unscheduled_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min)")
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return a summary dict with counts and time totals for the plan."""
        return {
            "date": self.date,
            "owner": self.owner.name,
            "scheduled_count": len(self.scheduled_tasks),
            "unscheduled_count": len(self.unscheduled_tasks),
            "total_duration_minutes": self.total_duration,
            "remaining_minutes": self.owner.available_minutes - self.total_duration,
        }

    def __repr__(self) -> str:
        return f"ActivityPlan(date={self.date}, tasks={len(self.scheduled_tasks)})"


class Scheduler:
    """Retrieves tasks from the owner's pets, sorts by priority, and builds a daily plan."""

    def __init__(self, owner: Owner, start_time: str = DEFAULT_START_TIME):
        self.owner = owner
        self.start_time = start_time
        self.remaining_minutes: int = owner.available_minutes
        self.plan: ActivityPlan | None = None

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Sort tasks by their scheduled_time ('HH:MM'); unscheduled tasks go last.

        Uses a lambda as the sort key so that string comparison works correctly
        on 'HH:MM' format — '08:00' < '09:30' < '14:00' lexicographically,
        which matches chronological order. Tasks with no time get '99:99' as a
        sentinel so they sort to the end rather than raising an error.
        """
        return sorted(tasks, key=lambda t: t.scheduled_time or "99:99")

    @staticmethod
    def sort_by_priority(tasks: list[Task]) -> list[Task]:
        """Sort tasks high-to-low by priority, breaking ties by duration (shortest first)."""
        return sorted(
            tasks,
            key=lambda t: (-PRIORITY_RANK.get(t.priority, 0), t.duration_minutes),
        )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def filter_by_pet(owner: "Owner", pet_name: str) -> list[Task]:
        """Return only the tasks that belong to a named pet."""
        return owner.get_tasks_for(pet_name)

    @staticmethod
    def filter_pending(tasks: list[Task]) -> list[Task]:
        """Return only tasks that have not been marked complete."""
        return [t for t in tasks if not t.completed]

    @staticmethod
    def filter_completed(tasks: list[Task]) -> list[Task]:
        """Return only tasks that have been marked complete."""
        return [t for t in tasks if t.completed]

    # ------------------------------------------------------------------
    # Recurring task completion
    # ------------------------------------------------------------------

    def complete_task(self, task: Task, pet: Pet) -> "Task | None":
        """Mark a task complete and auto-register its next occurrence on the pet.

        How it works:
          1. Calls task.mark_complete() to flag the current instance as done.
          2. Calls task.next_occurrence() which uses timedelta to compute the
             next due date (today+1 for daily, today+7 for weekly).
          3. If a next occurrence exists, adds it to the pet's task list so
             it will appear in the next call to generate_plan().
          4. Returns the new task (or None for as_needed tasks).
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    # ------------------------------------------------------------------
    # Core scheduling
    # ------------------------------------------------------------------

    def fits_in_time(self, task: Task) -> bool:
        """Return True if the task's duration fits within the remaining available minutes."""
        return task.duration_minutes <= self.remaining_minutes

    def needs_medication(self) -> bool:
        """Return True if any pending task across all pets has the 'medical' category."""
        return any(task.category == "medical" for task in self.owner.get_pending_tasks())

    def generate_plan(self, plan_date: str = None) -> ActivityPlan:
        """Build a daily plan: skip completed tasks, sort smarter, assign real time slots."""
        if plan_date is None:
            plan_date = str(_date.today())

        self.remaining_minutes = self.owner.available_minutes
        self.plan = ActivityPlan(date=plan_date, owner=self.owner)

        # Improvement D: skip already-completed tasks
        pending = self.owner.get_pending_tasks()

        # Improvement A: sort by priority desc; within same priority, shortest first
        # so more tasks can fit in the available window
        sorted_tasks = self.sort_by_priority(pending)

        # Improvement B: walk a clock forward and stamp each accepted task
        clock = _time_to_minutes(self.start_time)

        for task in sorted_tasks:
            if self.fits_in_time(task):
                task.scheduled_time = _minutes_to_time(clock)
                clock += task.duration_minutes
                self.remaining_minutes -= task.duration_minutes
                self.plan.add_task(task)
            else:
                self.plan.unscheduled_tasks.append(task)

        return self.plan

    def explain_plan(self) -> str:
        """Return a plain-language explanation of every scheduling decision made."""
        if self.plan is None:
            return "No plan has been generated yet. Call generate_plan() first."

        lines = ["Plan explanation:", "-" * 40]
        for task in self.plan.scheduled_tasks:
            lines.append(
                f"[+] '{task.title}' at {task.scheduled_time} -- "
                f"priority: {task.priority}, duration: {task.duration_minutes} min"
            )
        for task in self.plan.unscheduled_tasks:
            lines.append(
                f"[-] '{task.title}' skipped -- {task.duration_minutes} min didn't fit in remaining time"
            )
        lines.append(f"\n{self.remaining_minutes} min left unused after scheduling.")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Scheduler(owner='{self.owner.name}', remaining={self.remaining_minutes}min)"
