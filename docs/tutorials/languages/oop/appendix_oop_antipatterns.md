# Appendix A — OOP Anti‑Patterns and Refactoring (Python)

Purpose: help you spot design smells early and apply small, safe refactors. Favor composition, clear boundaries, and tests.

## God Object
- Symptoms: one class knows/does too much; long files; many unrelated methods.
- Consequences: tight coupling, low cohesion, hard to test.
- Refactors: Extract Class/Module; Introduce Facade; push behavior to domain objects.

## Feature Envy
- Symptoms: a method spends more time with another object’s data than its own.
- Consequences: hidden coupling, poor cohesion.
- Refactors: Move Method to the data owner; introduce service with clear API.

## Inappropriate Intimacy
- Symptoms: modules poke at each other’s internals; many "_private" accesses.
- Consequences: brittle changes; circular dependencies.
- Refactors: Define small interfaces/Protocols; hide internals; use composition.

## Long Parameter List / Data Clumps
- Symptoms: repeated groups of params everywhere.
- Consequences: call‑site noise, mismatch errors.
- Refactors: Introduce Parameter Object (dataclass); pass domain objects instead.

## Refused Bequest (LSP Violation)
- Symptoms: subclass overrides to disable base behavior; raises NotImplemented in concrete paths.
- Consequences: surprising runtime errors; broken polymorphism.
- Refactors: Prefer composition; split base into smaller ABCs/Protocols.

## Shotgun Surgery
- Symptoms: small change requires edits across many files.
- Consequences: fragile code, high change cost.
- Refactors: Centralize via Factory/Strategy; align boundaries; improve cohesion.

## Primitive Obsession
- Symptoms: domain concepts modeled as strings/ints.
- Consequences: duplicated validation, unclear intent.
- Refactors: Introduce tiny types (dataclasses) or descriptors/properties for validation.

## Anemic Domain Model
- Symptoms: objects with only data; behavior lives elsewhere.
- Consequences: scattered logic; weak invariants.
- Refactors: Move behavior into domain objects; enforce invariants close to data.

## Cyclic Dependencies
- Symptoms: import loops, delayed imports.
- Consequences: brittle startup; hidden ordering.
- Refactors: Split modules; invert dependency with interfaces; move shared types to a core module.

---

## Python‑Specific Do/Don’t
- Do
  - Use `@property`/descriptors for validation, not ad‑hoc checks everywhere.
  - Favor `Protocol`/ABCs for boundaries and DIP; inject dependencies.
  - Keep mixins small/behavioral; use cooperative `super()`.
- Don’t
  - Don’t hide heavy I/O in `__get__` or dunders; keep surprises minimal.
  - Don’t use multiple inheritance to “share code” when a helper or composition suffices.
  - Don’t expose internals; prefer module‑private helpers (`_name`) and clear public APIs.

---

## Small Refactor Playbook
- Extract Class/Function → raise cohesion, shrink responsibilities.
- Move Method → reduce feature envy; align behavior with data.
- Introduce Parameter Object (dataclass) → simplify signatures.
- Apply Strategy/Factory → remove branching; centralize creation.
- Add Tests → lock behavior and enable safe refactors.
