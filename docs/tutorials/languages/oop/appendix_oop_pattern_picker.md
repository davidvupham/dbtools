# Appendix B — Pattern Picker (Problem → Approaches)

Use this as a decision aid. Prefer composition and simple helpers before heavy patterns.

| Problem / Smell | Consider | Why | When to avoid |
| --- | --- | --- | --- |
| Many ways to construct an object | Factory, Builder (rare in Python) | Centralize creation, isolate config parsing | If `__init__` is simple |
| Branchy behavior based on type/flags | Strategy (composition) | Remove `if/elif`; swap at runtime | If only 1–2 cases and unlikely to grow |
| Need to react to events | Observer | Decouple publishers/subscribers | Overkill for single consumer |
| Add cross‑cutting behavior | Decorator | Compose behaviors without subclassing | If stateful interactions are complex |
| Operate on tree structures | Composite | Uniform treatment of leaf/composite | If a simple list suffices |
| Stateful workflow with transitions | State | Encapsulate transitions | If state space is tiny |
| Enforce class registry / contracts | Metaclass, Class decorator | Auto‑register, inject APIs | Prefer class decorator unless meta is required |
| Attribute validation/caching | Property, Descriptor | Reusable attribute semantics | If simple, property likely enough |
| Shared, expensive resource | Proxy / Pool | Lazy init, caching, access control | If direct access is clear and cheap |
| Algorithm skeleton shared, steps vary | Template Method | Common flow + overridable hooks | Prefer composition if fits better |
| Externalizable configuration | Builder/Factory + Config schema | Separation of concerns | If config is trivial |

Quick picks in Python:
- Prefer `@property`/descriptors over custom setters.
- Prefer Protocols/ABCs for boundaries; inject dependencies (DIP).
- Default to composition for pluggable behavior (Strategy, Decorator).
- Reach for metaclasses last; start with class decorators.
