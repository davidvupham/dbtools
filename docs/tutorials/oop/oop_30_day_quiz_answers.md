# 30-Day OOP Plan — Quiz Answers

Each day in the lesson plan has two quick questions. Answers are concise to support retrieval practice.

## Week 1 — Foundations

### Day 1
1) A class is a blueprint; an object is an instance created from that blueprint.
2) Modularity, reusability, maintainability, and better real‑world modeling.

### Day 2
1) When an object is instantiated (right after allocation).
2) It’s the instance reference used to access instance data/methods.

### Day 3
1) Class variables are shared by all instances; instance variables are per object.
2) For stateless utilities that don’t use `self` or `cls`.

### Day 4
1) Encapsulation/validation with simple attribute access syntax.
2) It rewrites `__attr` to `_ClassName__attr` to reduce accidental access.

### Day 5
1) Smaller memory footprint and faster attribute access via fixed slots.
2) When you want immutability and hashability (careful with mutating fields).

### Day 6
1) Tests enable safe changes and catch regressions.
2) Unit: tests one unit in isolation. Integration: tests components together.

### Day 7
1) Providing a new implementation of a method defined in a base class.
2) Unoverridden attributes/methods remain inherited.

## Week 2 — Polymorphism, ABCs, Composition, Typing

### Day 8
1) Same interface used across different types with different implementations.
2) Fewer explicit hierarchies; flexible, interface‑oriented code.

### Day 9
1) Instantiation fails with `TypeError` if abstract methods aren’t implemented.
2) ABCs enforce contracts programmatically.

### Day 10
1) Lower coupling, better testability, easier substitution of behaviors.
2) True “is‑a” relationships with shared invariants.

### Day 11
1) Structural: based on shape (methods/attrs). Nominal: based on declared type.
2) Protocols enable duck typing with static checking.

### Day 12
1) Each class has exactly one reason to change.
2) New features added without modifying tested code reduces breakage risk.

### Day 13
1) Subtype changing pre/postconditions in incompatible ways.
2) DIP enables swapping fakes/mocks and reduces coupling to low‑level details.

### Day 14
1) Clear module/class boundaries reduce ripple effects.
2) Too many responsibilities; unrelated concerns crammed into one class.

## Week 3 — Patterns and Python Data Model

### Day 15
1) Complex creation logic, multiple implementations, config‑driven creation.
2) Factory adds indirection/boilerplate but centralizes creation.

### Day 16
1) Removes branching; isolates change; enables runtime selection.
2) Add a new class that conforms to the strategy interface.

### Day 17
1) Push sends updates; pull queries state. Observer usually pushes events.
2) Near the subject/publisher, during initialization/config.

### Day 18
1) Subclassing increases tight coupling; decorators are compositional.
2) Leaf: single component; Composite: holds children and implements same interface.

### Day 19
1) Implement both if immutable and used in hashed collections.
2) `__repr__` is unambiguous/debug‑oriented; should aid debugging.

### Day 20
1) Leaked resources, incomplete cleanup, inconsistent state on error.
2) Cleanup belongs in `__exit__` (or finally‑blocks) for determinism.

### Day 21
1) Any improvement that simplified API, reduced duplication, or clarified roles.
2) E.g., long parameter lists, god object, feature envy, excessive comments.

## Week 4 — Advanced OOP, Testing, Error Handling

### Day 22
1) Descriptor for reusable cross‑cutting attribute semantics; property for local/simple cases.
2) In `instance.__dict__` with a distinct private key (e.g., `self._name`).

### Day 23
1) When simple transformation/registration can be done after class creation.
2) Multiple metas conflict; high cognitive load; complicated debugging.

### Day 24
1) Usually bad—mixins should be light; state invites conflicts.
2) D → B → C → A (C3 linearization in Python).

### Day 25
1) Patching hides design issues and couples tests to internals.
2) Brittle tests, hidden global side effects, missed restoration.

### Day 26
1) Organized handling and clear intent; easier catching of specific errors.
2) Catch when you can add context or handle; otherwise allow to propagate.

### Day 27
1) Fakes implement behavior; mocks assert interactions/expectations.
2) DI allows replacing dependencies without patching.

### Day 28
1) Arbitrary code execution; untrusted data must not be unpickled.
2) Version payloads; ignore/record unknown fields; validate types.

### Day 29
1) It blocks the event loop, killing concurrency.
2) Deterministic acquisition/cleanup and safer resource handling.

### Day 30
1) Any technical debt area posing risk or complexity.
2) Answers vary; common wins: composition, protocols, tests, SRP.
