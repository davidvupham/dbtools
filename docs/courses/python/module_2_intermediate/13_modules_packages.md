# Modules and Packages

Professional Python developers think about **structure first**, not last. Clean structure reduces bugs, speeds onboarding, makes testing trivial, and turns hacky scripts into maintainable systems.

## Modules

A **module** is simply a Python file (`.py`).

```python
# my_module.py
def greet():
    print("Hello")
```

Importing:

```python
import my_module
my_module.greet()

from my_module import greet
greet()
```

## Packages

A **package** is a directory of modules containing a special `__init__.py` file.

```
my_package/
    __init__.py
    module1.py
    module2.py
```

### The `__init__.py` file

This file is executed when the package is imported. It's often used to export key functions.

```python
# __init__.py
from .module1 import func1
from .module2 import func2

__all__ = ['func1', 'func2']
```

---

## Think in Packages, Not Files

Beginners think in files. Professionals think in **packages**.

### The Problem

If your project looks like this, you have a design problem:

```
project/
├── app.py
├── utils.py
├── helpers.py
├── logic.py
└── db.py
```

File names like `_utils` or `_helpers` often hide unclear responsibilities.

### The Solution

Group code by **domain**, not by function type:

```
project/
├── users/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── repository.py
├── payments/
│   ├── __init__.py
│   ├── gateway.py
│   └── services.py
└── core/
    ├── __init__.py
    └── exceptions.py
```

This structure mirrors how you **think** about the problem. When someone asks "where's the payment logic?", the answer is obvious.

---

## Use a Predictable Layout

Professionals love boring, predictable code. A solid, widely accepted structure:

```
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── config.py
│       ├── core/
│       ├── services/
│       └── models/
├── tests/
│   ├── conftest.py
│   └── test_services.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── .gitignore
```

Why this works:

- `src/` prevents accidental imports from the root
- `__main__.py` enables `python -m project_name` execution
- Tests are isolated from source code
- Configuration is explicit
- Imports are predictable

> See [Python Package Structure](../../../reference/python-package-structure.md) for detailed guidance on the src-layout pattern.

---

## Separate Application Logic from Infrastructure

One of the biggest mistakes is mixing **business logic** with **infrastructure** (databases, email, external services).

### Bad Example

```python
def create_user(data):
    user = User(**data)
    db.session.add(user)      # Infrastructure
    db.session.commit()       # Infrastructure
    send_email(user.email)    # Infrastructure
```

This function does too much. Testing it requires a database and email service.

### Good Example

```python
# services.py - Pure business logic
def create_user(data):
    return User(**data)

# main.py - Orchestration wires things together
user = create_user(data)
user_repo.save(user)
email_service.send_welcome(user)
```

This separation makes:

- **Testing easier**: Test business logic without infrastructure
- **Refactoring safer**: Change database without touching logic
- **Logic reusable**: Same logic, different infrastructure

If your business logic *knows* how emails or databases work, it's doing too much.

---

## Keep `main.py` Boring

Your entry point should **orchestrate**, not think.

### Good `main.py`

```python
def main():
    config = load_config()
    app = create_app(config)
    app.run()

if __name__ == "__main__":
    main()
```

### Bad `main.py`

```python
# 300 lines of logic, imports, conditionals, and setup
```

Think of `main.py` like a conductor:

- It doesn't play instruments
- It tells others when to play

If logic lives in `main.py`, you'll regret it during testing and maintenance.

---

## Make Packages Executable with `__main__.py`

Add a `__main__.py` file to make your package runnable with `python -m`:

```
src/my_package/
    __init__.py
    __main__.py    # Enables: python -m my_package
    cli.py
```

### Example `__main__.py`

```python
# __main__.py
from .cli import main

if __name__ == "__main__":
    main()
```

Now users can run your package directly:

```bash
python -m my_package --help
```

This is cleaner than asking users to find and run a specific script. It also works consistently whether the package is installed or run from source.

---

## Relative vs Absolute Imports

**Within the same package**, use relative imports:

```python
# users/services.py
from .models import User           # Same package
from .repository import UserRepo   # Same package
from ..core import exceptions      # Parent package
```

**Between different packages**, use absolute imports:

```python
# users/services.py
from payments.gateway import process_payment  # Different package
```

### Why This Matters

| Import Type | Use Case | Example |
|-------------|----------|---------|
| Relative (`.`) | Same package | `from .models import User` |
| Relative (`..`) | Parent package | `from ..core import BaseError` |
| Absolute | External packages | `from payments import Gateway` |

Relative imports make packages **self-contained** and easier to rename or move. If you use absolute imports everywhere within a package, renaming the package means updating every import.

---

## Use `__init__.py` Intentionally

Don't treat `__init__.py` as magic. Use it to:

1. **Define public APIs** - What should consumers import?
2. **Simplify imports** - Hide internal module structure
3. **Hide internals** - Keep implementation details private

### Example

```python
# users/__init__.py
from .services import create_user, delete_user
from .models import User

__all__ = ['create_user', 'delete_user', 'User']
```

Now consumers import cleanly:

```python
from users import create_user, User
```

Instead of:

```python
from users.services import create_user
from users.models import User
```

**Rule**: If everything is importable, nothing is designed.

---

## Avoid Circular Imports

Circular imports aren't just annoying—they're structural debt.

### Symptoms

- Import errors only at runtime
- Weird dependency chains
- "Moving this line fixes it" hacks

### Solutions

1. **Introduce a `core/` layer**: Put shared types and interfaces here

```
project/
├── core/
│   ├── __init__.py
│   ├── types.py      # Shared types
│   └── interfaces.py # Abstract base classes
├── users/
└── payments/
```

2. **Extract shared abstractions**: If two modules need the same thing, it belongs in `core/`

3. **Invert dependencies**: Instead of A importing B and B importing A, both import from `core/`

4. **Use `TYPE_CHECKING` for type hints**:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .other_module import SomeClass  # Only imported for type checking

def process(item: "SomeClass") -> None:
    pass
```

**Rule**: If two modules depend on each other, your boundaries are wrong.

---

## Namespace Packages (Advanced)

Python 3.3+ supports **namespace packages**—packages without an `__init__.py` file. These allow a single logical package to be split across multiple directories or distributions.

### When to Use Namespace Packages

- **Plugin systems**: Multiple packages contribute to the same namespace
- **Large organizations**: Different teams own different sub-packages
- **Distributed packages**: Parts of a package installed separately

### Example Structure

```
# Installed from package-a
site-packages/
    mycompany/
        tools/
            parser.py

# Installed from package-b
site-packages/
    mycompany/
        tools/
            formatter.py
```

Both contribute to `mycompany.tools` without conflict.

### When NOT to Use Namespace Packages

For most projects, **use regular packages with `__init__.py`**. Namespace packages add complexity and have limitations:

- No package-level initialization code
- Slower imports (Python must search multiple paths)
- Harder to reason about package contents

**Rule**: If you're not building a plugin system or organizational namespace, use regular packages.

---

## Tests Mirror Your App Structure

Tests are not an afterthought. Mirror your application structure:

```
src/project_name/          tests/
├── users/                 ├── users/
│   ├── services.py        │   └── test_services.py
│   └── models.py          │   └── test_models.py
├── payments/              ├── payments/
│   └── gateway.py         │   └── test_gateway.py
└── core/                  └── conftest.py
```

### Good Tests

- Import **public interfaces** only
- Avoid mocking everything
- Test **behavior**, not implementation

If testing feels painful, that's a **signal** your structure needs work. Clean architecture makes testing boring—and boring is good.

---

## Document Structure in README

Most READMEs explain *what* the project does—not *how it's organized*.

Add a short section:

```markdown
## Project Structure

- `users/`: User domain logic (registration, authentication)
- `payments/`: Payment processing and gateway integration
- `core/`: Shared abstractions, base classes, exceptions
```

This saves hours for:

- New teammates
- Future you
- Open-source contributors

Documentation is part of structure.

---

## Refactor Structure Early

Structure has inertia. The longer a project lives:

- The harder it is to move files
- The scarier refactors become
- The more people depend on it

Refactor structure when:

- The project is small
- Tests are fast
- Changes are cheap

Waiting for "later" is how messy projects are born.

---

## A Simple Mental Model

When in doubt, ask:

1. Can I explain this structure in 30 seconds?
2. Can someone new find code without asking me?
3. Can I test logic without spinning everything up?

If the answer is "no" to any of these—simplify.

---

## Best Practices Summary

1. **Use relative imports within packages**: `from .core import utils`
2. **Use absolute imports between packages**: `from other_package import module`
3. **Avoid `import *`**: It pollutes the namespace
4. **Group by domain**: Not by function type
5. **Separate concerns**: Business logic vs infrastructure
6. **Boring entry points**: `main.py` orchestrates, doesn't think
7. **Intentional `__init__.py`**: Define your public API
8. **No circular imports**: Use `core/` layer and dependency inversion
9. **Mirror tests to source**: Same structure, different directory
10. **Document structure**: Help future developers navigate

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Debugging](12a_debugging.md) | [Module 2](../README.md) | [Dependencies](13a_dependencies.md) |
