# PawPal+ — Final UML Class Diagram

> Export this as `uml_final.png` using one of:
> - [mermaid.live](https://mermaid.live) — paste the code block, click Download PNG
> - VS Code: install the **Mermaid Preview** extension, open this file, right-click → Export PNG
> - GitHub: this renders automatically in any `.md` file

```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes
        +dict preferences
        +List~Pet~ pets
        +add_pet(pet) None
        +remove_pet(pet) None
        +get_available_time() int
        +update_preferences(prefs) None
        +get_all_tasks() List~Task~
        +get_tasks_for(pet_name) List~Task~
        +get_pending_tasks() List~Task~
        +get_completed_tasks() List~Task~
    }

    class Pet {
        +String name
        +String species
        +String breed
        +int age
        +String energy_level
        +String health_notes
        +List~Task~ tasks
        +add_task(task) None
        +remove_task(task) None
        +get_tasks() List~Task~
        +get_profile() dict
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String frequency
        +String notes
        +String scheduled_time
        +bool completed
        +String due_date
        +is_high_priority() bool
        +mark_complete() None
        +next_occurrence() Task
        +edit(field, value) None
        +to_dict() dict
    }

    class Scheduler {
        +Owner owner
        +String start_time
        +int remaining_minutes
        +ActivityPlan plan
        +sort_by_time(tasks)$ List~Task~
        +sort_by_priority(tasks)$ List~Task~
        +filter_by_pet(owner, pet_name)$ List~Task~
        +filter_pending(tasks)$ List~Task~
        +filter_completed(tasks)$ List~Task~
        +detect_conflicts(tasks)$ List~Tuple~
        +complete_task(task, pet) Task
        +fits_in_time(task) bool
        +needs_medication() bool
        +generate_plan(plan_date) ActivityPlan
        +explain_plan() str
    }

    class ActivityPlan {
        +String date
        +Owner owner
        +List~Task~ scheduled_tasks
        +List~Task~ unscheduled_tasks
        +int total_duration
        +add_task(task) None
        +remove_task(task) None
        +display() str
        +get_summary() dict
    }

    Owner "1" *-- "many" Pet : owns
    Pet "1" *-- "many" Task : holds
    Owner "1" --> "1" Scheduler : used by
    Scheduler "1" --> "1" ActivityPlan : produces
    ActivityPlan "1" o-- "many" Task : scheduled
    ActivityPlan "1" o-- "many" Task : unscheduled
    ActivityPlan "1" --> "1" Owner : references
```
