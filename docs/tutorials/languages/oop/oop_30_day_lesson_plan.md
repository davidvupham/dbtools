# 30-Day Python OOP Lesson Plan (15–20 min/day)

Spend 15–20 minutes each day. This plan references the tutorials:

- Beginner tutorial: [oop_guide.md](./oop_guide.md)
- Advanced tutorial: [advanced_oop_concepts.md](./advanced_oop_concepts.md)

Answers and solutions:
- Quiz answers: [oop_30_day_quiz_answers.md](./oop_30_day_quiz_answers.md)
- Exercise solutions: [oop_30_day_exercise_solutions.md](./oop_30_day_exercise_solutions.md)

Capstone project (threaded through exercises): a small Library system with `Item` types (`Book`, `EBook`, `AudioBook`), `Library`, `Inventory`, `Member`, `Loan`, and a `Notification` subsystem.

Format per day:
- Yesterday recap
- Today you’ll learn (bullets)
- Read (links into the tutorials)
- Exercise (capstone‑linked)
- Quiz (2 quick questions for retrieval practice)

Tip: If you have more time, do the optional stretch at the end of the day.

---

## Week 1 — Foundations

### Day 1 — Objects and Classes
- Yesterday recap: N/A
- Today you’ll learn: What classes and objects are; attributes vs methods
- Read: [oop_guide.md — Introduction to OOP](./oop_guide.md#introduction-to-oop), [Classes and Objects](./oop_guide.md#classes-and-objects)
- Exercise: Create a minimal `Book(title, author)` and instantiate two books; print them.
- Quiz: 1) Define a class vs an object. 2) Give two benefits of OOP.

### Day 2 — `__init__`, `self`, instance state
- Yesterday recap: Classes and objects
- Today you’ll learn: Constructors; storing per‑instance state
- Read: [Understanding `self`](./oop_guide.md#understanding-self)
- Exercise: Add `pages`, `isbn` to `Book`; implement `describe()`.
- Quiz: 1) When is `__init__` called? 2) Why is `self` the first parameter?

### Day 3 — Class vs instance variables, class/staticmethods
- Yesterday recap: Constructors & instance attributes
- Today you’ll learn: Shared vs per‑object data; factories & utilities
- Read: [Class vs Instance Variables](./oop_guide.md#classes-and-objects) (section within), [The Python Data Model → class/staticmethods](./oop_guide.md#the-python-data-model-dunder-methods)
- Exercise: Add `Book.total_created` and a `@classmethod from_dict` to create a book from a dict.
- Quiz: 1) Class var vs instance var? 2) When use `@staticmethod`?

### Day 4 — Encapsulation & properties
- Yesterday recap: Class vs instance members
- Today you’ll learn: Public/private conventions; `@property` for validation
- Read: [Encapsulation and Data Hiding](./oop_guide.md#encapsulation-and-data-hiding)
- Exercise: Make `isbn` read‑only; validate its format in a setter.
- Quiz: 1) Why use properties? 2) What does name‑mangling do for `__attr`?

### Day 5 — Dataclasses
- Yesterday recap: Encapsulation
- Today you'll learn: `@dataclass`, defaults, `slots`, `frozen`
- Read: [Modern Python OOP Features → Dataclasses](./oop_guide.md#dataclasses)
- Optional reading: [Performance Considerations → `__slots__`](./oop_guide.md#1-use-__slots__-for-memory-efficiency) for benchmarks and memory comparisons
- Exercise: Convert `Book` to a dataclass; add `slots=True`; compare memory using `__sizeof__()`.
- Quiz: 1) Benefit of `slots`? 2) When use `frozen` dataclasses?

### Day 6 — Review + quick tests
- Yesterday recap: Dataclasses
- Today you’ll learn: Light refactor; basic testing mindset
- Read: [Testing OOP Code](./oop_guide.md#testing-oop-code)
- Exercise: Add a simple test for `Book.describe()` using `pytest`.
- Quiz: 1) Why tests help refactoring? 2) Unit vs integration test?

### Day 7 — Inheritance basics
- Yesterday recap: Tests & refactor
- Today you’ll learn: Base/derived classes; overriding
- Read: [Inheritance](./oop_guide.md#inheritance)
- Exercise: Create `Item` base; derive `Book(Item)`.
- Quiz: 1) What is overriding? 2) What remains inherited after override?

---

## Week 2 — Polymorphism, ABCs, Composition, Typing

### Day 8 — Polymorphism & duck typing
- Yesterday recap: Inheritance
- Today you’ll learn: Same interface; different implementations; duck typing
- Read: [Polymorphism](./oop_guide.md#polymorphism)
- Exercise: Add `EBook` with `format`; both `Book` and `EBook` implement `get_size()` differently.
- Quiz: 1) Define polymorphism. 2) Why is duck typing powerful in Python?

### Day 9 — Abstract Base Classes (ABCs)
- Yesterday recap: Polymorphism
- Today you’ll learn: `abc.ABC`, `@abstractmethod`, enforcements
- Read: [Abstract Base Classes](./oop_guide.md#abstract-base-classes)
- Exercise: Create `Borrowable` ABC with `borrow()/return_()`; have `Item` implement it.
- Quiz: 1) What happens if you instantiate an ABC missing required methods? 2) Why prefer ABCs over comments?

### Day 10 — Composition over inheritance
- Yesterday recap: ABCs
- Today you’ll learn: “Has‑a” vs “Is‑a”; swappable behaviors
- Read: [Composition vs Inheritance](./oop_guide.md#composition-vs-inheritance)
- Exercise: Create `NotificationService` and compose it into `Library`.
- Quiz: 1) One reason to prefer composition? 2) A case where inheritance is appropriate?

### Day 11 — Protocols & type hints
- Yesterday recap: Composition
- Today you'll learn: `typing.Protocol`, structural subtyping, Generic classes
- Read: [Type Hints and Protocols](./oop_guide.md#type-hints-and-protocols)
- Optional reading: [Generic Classes](./oop_guide.md#generic-classes-type-parameters), [The `Self` Type](./oop_guide.md#the-self-type-python-311)
- Exercise: Define `Notifier` protocol; implement `EmailNotifier`, `SMSNotifier`.
- Quiz: 1) Structural vs nominal typing? 2) Advantage of Protocols?

### Day 12 — SOLID: SRP & OCP
- Yesterday recap: Protocols
- Today you’ll learn: Single Responsibility; Open/Closed
- Read: [SOLID Principles → SRP, OCP](./oop_guide.md#solid-principles)
- Exercise: Extract `Inventory` (SRP). Add new `AudioBook` without changing consumers (OCP).
- Quiz: 1) Define SRP. 2) How does OCP reduce regressions?

### Day 13 — SOLID: LSP, ISP, DIP
- Yesterday recap: SRP & OCP
- Today you’ll learn: Substitutability; small interfaces; dependency inversion
- Read: [SOLID Principles → LSP, ISP, DIP](./oop_guide.md#solid-principles)
- Exercise: Ensure `EBook` respects `Item` invariants (LSP). Split a fat interface (ISP). Inject `Notifier` into `Library` (DIP).
- Quiz: 1) Give an LSP violation example. 2) DIP’s testing benefit?

### Day 14 — Review & mini‑project integration
- Yesterday recap: LSP/ISP/DIP
- Today you’ll learn: Integrating pieces coherently
- Read: [Best Practices Summary](./oop_guide.md#best-practices-summary)
- Exercise: Wire `Library` + `Inventory` + `Notifier` + `Item` types; run a tiny demo.
- Quiz: 1) Why boundaries matter? 2) Two signs of a “god object”?

---

## Week 3 — Patterns and Python Data Model

### Day 15 — Factory pattern
- Yesterday recap: Integration
- Today you’ll learn: Centralizing creation
- Read: [Design Patterns → Factory](./oop_guide.md#design-patterns)
- Exercise: `ItemFactory` creates `Book`, `EBook`, `AudioBook` from payloads.
- Quiz: 1) When use factories? 2) Tradeoffs vs direct constructors?

### Day 16 — Strategy via composition
- Yesterday recap: Factory
- Today you’ll learn: Pluggable algorithms
- Read: [Composition vs Inheritance → Strategy example](./oop_guide.md#composition-vs-inheritance)
- Exercise: Pricing strategies: `StandardPricing`, `StudentPricing`, applied in `Library`.
- Quiz: 1) Benefit over `if/elif`? 2) How to add a new strategy safely?

### Day 17 — Observer and events
- Yesterday recap: Strategy
- Today you’ll learn: One‑to‑many notifications
- Read: [Design Patterns → Observer](./oop_guide.md#design-patterns)
- Exercise: Notify on overdue items; observers subscribe to events.
- Quiz: 1) Push vs pull? 2) Where to place observer registration?

### Day 18 — Decorator & Composite
- Yesterday recap: Observer
- Today you’ll learn: Behavior extension; tree structures
- Read: [Design Patterns → Decorator, Composite](./oop_guide.md#design-patterns)
- Exercise: `DiscountedItem` decorator; `Collection` composite of items.
- Quiz: 1) Decorator vs subclass? 2) Composite leaf vs composite node?

### Day 19 — Dunder methods and containers
- Yesterday recap: Patterns
- Today you'll learn: `__repr__`, equality, ordering, iterables, callable objects, attribute access control
- Read: [The Python Data Model (Dunder Methods)](./oop_guide.md#the-python-data-model-dunder-methods)
- Optional reading: [Making Objects Callable (`__call__`)](./oop_guide.md#making-objects-callable-__call__), [Attribute Access Control (`__getattr__`, `__setattr__`)](./oop_guide.md#attribute-access-control-__getattr__-__setattr__-__delattr__)
- Exercise: Make `Catalog` iterable; provide meaningful `__repr__` for domain objects.
- Quiz: 1) When implement `__eq__` + `__hash__`? 2) Why `__repr__` is for devs?

### Day 20 — Context managers
- Yesterday recap: Data model
- Today you'll learn: `__enter__`/`__exit__` resource safety, exception handling, nested contexts
- Read: [Advanced OOP Concepts → Context Managers](./oop_guide.md#context-managers)
- Note: This section has been significantly expanded with 9 subsections including suppressing exceptions, nested context managers, and atomic operations
- Exercise: `LoanSession` context manager for borrow/return atomicity.
- Quiz: 1) Common pitfalls without context managers? 2) Where to place cleanup?

### Day 21 — Review & refactor
- Yesterday recap: Context managers
- Today you’ll learn: Consolidate and simplify
- Read: [Best Practices Summary](./oop_guide.md#best-practices-summary)
- Exercise: Refactor capstone for clarity; add missing tests.
- Quiz: 1) One refactor you made and why. 2) A smell you addressed?

---

## Week 4 — Advanced OOP Topics, Testing, Error Handling

### Day 22 — Descriptors
- Yesterday recap: Review & refactor
- Today you'll learn: Reusable attribute semantics, validation, lazy loading, caching
- Read: [oop_guide.md → Descriptors](./oop_guide.md#descriptors) (comprehensive coverage with 8 descriptor types)
- Alternate reading: [advanced_oop_concepts.md → The Descriptor Protocol](./advanced_oop_concepts.md#the-descriptor-protocol)
- Exercise: `Validated` descriptor for `isbn` and `email` with type/value checks.
- Quiz: 1) When prefer descriptor vs property? 2) Where to store backing value?

### Day 23 — Metaclasses & class decorators
- Yesterday recap: Descriptors
- Today you'll learn: Class creation control; registries; when to use decorators vs metaclasses
- Read: [oop_guide.md → Class Decorators](./oop_guide.md#class-decorators)
- Read: [When to Use Class Decorators vs Metaclasses](./oop_guide.md#when-to-use-class-decorators-vs-metaclasses)
- Advanced reading: [advanced_oop_concepts.md → Advanced Metaclass Usage](./advanced_oop_concepts.md#advanced-metaclass-usage)
- Exercise: Implement a registry using BOTH a class decorator AND a metaclass; compare the approaches.
- Quiz: 1) When a class decorator is sufficient? 2) One metaclass pitfall?

### Day 24 — Multiple inheritance & MRO; mixin design
- Yesterday recap: Metaclasses
- Today you’ll learn: Cooperative `super()`, safe mixins, MRO
- Read: [advanced_oop_concepts.md → Multiple Inheritance and the Diamond Problem](./advanced_oop_concepts.md#multiple-inheritance-and-the-diamond-problem)
- Exercise: `TimestampedMixin`, `SerializableMixin` added to items; verify MRO works.
- Quiz: 1) State in mixins: good or bad and why? 2) What is MRO order for a diamond?

### Day 25 — Safe monkey patching (for tests)
- Yesterday recap: MI & mixins
- Today you’ll learn: Temporary overrides with restoration
- Read: [advanced_oop_concepts.md → Monkey Patching and Dynamic Class Modification](./advanced_oop_concepts.md#monkey-patching-and-dynamic-class-modification)
- Exercise: Patch a slow function in tests using a context manager; ensure restoration.
- Quiz: 1) Why prefer DI over patching in production? 2) One risk of patching?

### Day 26 — Error handling in OOP; custom exceptions
- Yesterday recap: Monkey patching
- Today you’ll learn: Exception hierarchies; defensive programming
- Read: [Error Handling in OOP](./oop_guide.md#error-handling-in-oop)
- Exercise: Add `LibraryError`, `LoanError`; ensure error flows are tested.
- Quiz: 1) Exception hierarchy benefit? 2) When catch vs let bubble?

### Day 27 — Testing OOP systems
- Yesterday recap: Error handling
- Today you’ll learn: Unit tests, fakes/mocks, integration seams
- Read: [Testing OOP Code](./oop_guide.md#testing-oop-code)
- Exercise: Test `Library` with a fake `Notifier`; parametrize cases.
- Quiz: 1) Fake vs mock difference? 2) What does DI buy you in tests?

### Day 28 — Serialization (JSON, versioning); security notes
- Yesterday recap: Testing
- Today you’ll learn: Stable schemas; versioned payloads; safe decoding
- Read: [advanced_oop_concepts.md → Protocol Buffers and Serialization](./advanced_oop_concepts.md#protocol-buffers-and-serialization), [JSON tips](./oop_guide.md#json-serialization-tips)
- Exercise: Serialize `Loan` to JSON with a `version` field; write `from_json` that validates.
- Quiz: 1) Why avoid pickle for untrusted data? 2) How to handle unknown fields?

### Day 29 — Async boundaries (I/O), context managers, resource pools
- Yesterday recap: Serialization
- Today you’ll learn: Async service classes; timeouts; cleanup
- Read: [advanced_oop_concepts.md → Async/Await with Classes](./advanced_oop_concepts.md#asyncawait-with-classes)
- Exercise: Async `ReminderService` that batches overdue reminders with timeouts.
- Quiz: 1) Why not block in async code? 2) Benefit of async context managers?

### Day 30 — Capstone polish & retrospective
- Yesterday recap: Async
- Today you’ll learn: Tie everything together; reflect
- Read: [Best Practices Summary](./oop_guide.md#best-practices-summary)
- Exercise: Demo script showing borrowing/returning, notifications, serialization, and one test run.
- Quiz: 1) What would you refactor next and why? 2) Which concepts most improved your design?

---

## Stretch and Follow‑Ups

### Practice More
- Work through [Intermediate Exercises](./oop_intermediate_exercises.md) — 10 practical exercises bridging basics to advanced (Shopping Cart, Plugin System, Notification Service, Caching Layer, Task Queue, Configuration Manager, Logging Framework, Data Validation, State Machine, Event System)
- Review [Performance Considerations](./oop_guide.md#performance-considerations) when optimizing — includes 6 real benchmarks and best practices

### Expand Your Project
- Add CLI or minimal web API over the Library services.
- Add persistence (SQLite) behind `Inventory` via a repository interface (DIP), then swap an in‑memory version for tests.
- Explore additional patterns: State, Proxy, Visitor (see [Design Patterns](./oop_guide.md#design-patterns)).

### Go Deeper
- Read Appendix A: [Anti‑Patterns and Refactoring](./appendix_oop_antipatterns.md)
- Use Appendix B: [Pattern Picker](./appendix_oop_pattern_picker.md) when making design choices.
- Follow Appendix C: [Packaging & Public API](./appendix_oop_packaging_public_api.md) to structure your project.

### Master Advanced Topics
- Dive into [advanced_oop_concepts.md](./advanced_oop_concepts.md) for async/await, multiple inheritance, monkey patching, and more
- Study the visual diagrams: [SOLID at a Glance](./oop_guide.md#solid-at-a-glance), [Composition vs Inheritance Decision Tree](./oop_guide.md#visual-decision-tree)

## How to Use This Plan
- Follow day by day; if you miss a day, continue and use review days to catch up.
- Keep code runnable and small; prefer simplicity.
- Commit daily; write at least one small test each week.
