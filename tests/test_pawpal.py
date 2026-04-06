from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high", category="exercise")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3, energy_level="high")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Fetch", duration_minutes=20, priority="medium", category="enrichment"))
    assert len(pet.tasks) == 1
