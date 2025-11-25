# OOP Tutorials

This directory contains the Object-Oriented Programming guides for this project.

**✨ Recently Enhanced (Nov 2025)**: All exercises now include expected outputs, comprehensive test suite added, and Python 3.10+ pattern matching coverage included. See [validation document](./OOP_TUTORIAL_VALIDATION_2025-11-22_Gemini.md) for details.

## 📚 Guides Available

### 🎯 OOP Guide (Start Here!)
**File:** [oop_guide.md](./oop_guide.md)

Perfect for beginners! Learn OOP from scratch with simple examples and exercises.

**What you'll learn:**
- Core OOP: classes, objects, encapsulation, inheritance, polymorphism
- ABCs, SOLID principles, composition vs inheritance
- Common design patterns (Factory, Singleton, Observer, Decorator, Composite)
- Modern features: dataclasses, protocols, type hints with generics, dunder methods
- Context managers and descriptors
- Class decorators and when to use them vs metaclasses
- Quick reference section with common patterns and mistakes to avoid

**Includes:**
- Clear explanations with real-world analogies
- Self-contained, runnable examples
- Practice exercises throughout
- Quick reference at the end

### 💪 Intermediate Exercises
**File:** [oop_intermediate_exercises.md](./oop_intermediate_exercises.md)

**NEW!** Bridge the gap between basics and advanced concepts with 10 practical exercises:
- Shopping Cart System (Encapsulation, Composition)
- Plugin System (ABCs, Factory Pattern)
- Notification Service (Strategy Pattern, DI)
- Caching Layer (Descriptors, Decorators)
- Task Queue System (Observer, State Patterns)
- Configuration Manager (Singleton, Validation)
- Logging Framework (Class Decorators, Mixins)
- Data Validation Framework (Descriptors, Type Hints)
- State Machine (State Pattern, Type Safety)
- Event System (Observer with Weak References)

**Includes:**
- Detailed requirements for each exercise
- Starter code to guide you
- Complete solutions with explanations
- Difficulty ratings

### 🗓️ 30-Day OOP Lesson Plan
**File:** [oop_30_day_lesson_plan.md](./oop_30_day_lesson_plan.md)

Daily 15–20 minute lessons from beginner to advanced with quick recaps, exercises, and quizzes. Every day links directly to the relevant sections of `oop_guide.md` and `advanced_oop_concepts.md`.

Companions:
- Quiz answers: [oop_30_day_quiz_answers.md](./oop_30_day_quiz_answers.md)
- Exercise solutions: [oop_30_day_exercise_solutions.md](./oop_30_day_exercise_solutions.md)

## 📎 Appendices

- Appendix A: [OOP Anti‑Patterns and Refactoring](./appendix_oop_antipatterns.md)
- Appendix B: [Pattern Picker (Problem → Approaches)](./appendix_oop_pattern_picker.md)
- Appendix C: [Packaging & Public API Design](./appendix_oop_packaging_public_api.md)

## 🧪 Testing & Verification

**File:** [tests/test_oop_exercises.py](./tests/test_oop_exercises.py)

Comprehensive test suite for all practice exercises! Verify your solutions automatically.

**To run**:
```bash
pytest tests/test_oop_exercises.py -v
```

**Includes**:
- Reference implementations for all 7 exercises
- 30+ test cases covering normal operation and edge cases
- Thread safety verification
- ABC enforcement checks

## 🆕 Modern Python Features

**File:** [pattern_matching_with_oop.md](./pattern_matching_with_oop.md)

**NEW!** Learn Python 3.10+ pattern matching with OOP:
- Structural pattern matching basics
- Pattern matching vs traditional polymorphism
- Real-world examples (event handlers, API responses, robot commands)
- Best practices and when to use which approach

## 📎 Appendices
**File:** [advanced_oop_concepts.md](./advanced_oop_concepts.md)

⚠️ **Read the OOP Guide first!** These are advanced topics for experienced developers.

**What you'll learn:**
- Async/await with classes, cooperative multiple inheritance, MRO
- Monkey patching, descriptors, metaclasses (pragmatic usage)
- Serialization strategies, performance profiling, memory/weakrefs

## 🎓 Suggested Learning Path

1. **Complete Beginners**: Start with [oop_guide.md](./oop_guide.md) from the beginning
2. **Some Python experience**: Skim the basics, focus on SOLID principles and design patterns
3. **Comfortable with OOP**: Move to [advanced_oop_concepts.md](./advanced_oop_concepts.md) for deeper knowledge

Prerequisites:
- Comfortable with Python fundamentals from [../python/](../python/)

Tip:
- Looking for general Python basics (functions, data structures, decorators, context managers)? Go to [../python/](../python/).
