class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences

    def get_available_time(self) -> int:
        pass

    def update_preferences(self, prefs: dict) -> None:
        pass


class Pet:
    def __init__(self, name: str, species: str, breed: str, age: int, energy_level: str, health_notes: str):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.energy_level = energy_level
        self.health_notes = health_notes

    def get_profile(self) -> dict:
        pass

    def needs_medication(self) -> bool:
        pass


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str, category: str, notes: str = ""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.scheduled_time = None
        self.notes = notes

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass

    def edit(self, field: str, value) -> None:
        pass


class ActivityPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_tasks: list[Task] = []
        self.total_duration: int = 0
        self.unscheduled_tasks: list[Task] = []

    def display(self) -> str:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_summary(self) -> dict:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.plan: ActivityPlan = None

    def generate_plan(self) -> ActivityPlan:
        pass

    def fits_in_time(self, task: Task) -> bool:
        pass

    def explain_plan(self) -> str:
        pass
