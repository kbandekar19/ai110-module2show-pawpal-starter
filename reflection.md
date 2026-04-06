# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Core User Actions**

The three core actions a user can perform in PawPal+:

1. **Enter pet and owner information** — The user provides details about their pet (species, breed, age, energy level, health needs) and themselves (name, contact info, availability preferences). This data forms the foundation for all scheduling decisions.

2. **Generate an activity plan** — Based on the user's available time, task priorities, and owner preferences, the system automatically creates a personalized activity schedule for the pet. The scheduler balances constraints like duration, frequency, and priority to produce a realistic, optimized plan.

3. **Add or edit tasks** — The user can manually add new tasks (e.g., a vet appointment, a grooming session) or edit existing ones in the activity plan, giving them direct control to adjust, reprioritize, or customize what the scheduler produces.

**UML Class Diagram**

```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes
        +dict preferences
        +get_available_time() int
        +update_preferences(prefs) None
    }

    class Pet {
        +String name
        +String species
        +String breed
        +int age
        +String energy_level
        +String health_notes
        +get_profile() dict
        +needs_medication() bool
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String scheduled_time
        +String notes
        +is_high_priority() bool
        +to_dict() dict
        +edit(field, value) None
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +List~Task~ tasks
        +ActivityPlan plan
        +generate_plan() ActivityPlan
        +fits_in_time(task) bool
        +explain_plan() str
    }

    class ActivityPlan {
        +String date
        +List~Task~ scheduled_tasks
        +int total_duration
        +List~Task~ unscheduled_tasks
        +display() str
        +add_task(task) None
        +remove_task(task) None
        +get_summary() dict
    }

    Owner "1" --> "1" Pet : owns
    Owner "1" --> "1" Scheduler : uses
    Scheduler "1" --> "many" Task : schedules
    Scheduler "1" --> "1" ActivityPlan : produces
    ActivityPlan "1" --> "many" Task : contains
```

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
