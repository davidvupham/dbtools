# Python data model reference

**🔗 [← Back to Python Reference](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Reference-purple)

> [!IMPORTANT]
> **Related Docs:** [Control Flow](./control_flow.md) | [Pattern Matching](./pattern-matching.md) | [Glossary](../glossary.md)

---

## Objects and types

Everything in Python is an object. Every object has:

1. **Identity** (memory address, `id()`)
2. **Type** (class, `type()`)
3. **Value** (content)

## Special ("magic") methods

Classes can define special methods to integrate with Python syntax.

### Initialization and representation

* `__init__(self, ...)`: Constructor, initializes the object.
* `__new__(cls, ...)`: Creator, creates the object (advanced).
* `__repr__(self)`: Unambiguous string representation (for devs/debugging).
* `__str__(self)`: Readable string representation (for users/`print`).

### Comparison

* `__eq__(self, other)`: `==`
* `__lt__(self, other)`: `<`
* `__le__(self, other)`: `<=`
* `__bool__(self)`: Boolean truth value (`if obj:`).

### Container types

* `__len__(self)`: `len(obj)`
* `__getitem__(self, key)`: `obj[key]`
* `__setitem__(self, key, value)`: `obj[key] = value`
* `__iter__(self)`: `for x in obj:`
* `__contains__(self, item)`: `item in obj`

### Callable objects

* `__call__(self, ...)`: Makes the object callable like a function (`obj()`).

### Context managers

* `__enter__(self)`: `with obj:`
* `__exit__(self, exc_type, exc_val, traceback)`: Exiting `with` block.

## Example

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def __repr__(self):
        return f"BankAccount(owner='{self.owner}', balance={self.balance})"

    def __str__(self):
        return f"${self.balance} ({self.owner})"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return BankAccount(self.owner, self.balance + other)
        return NotImplemented

    def __bool__(self):
        return self.balance > 0

acct = BankAccount("Alice", 100)
print(acct)          # $100 (Alice)
print(acct + 50)     # BankAccount(owner='Alice', balance=150)
if acct:             # True
    print("Has funds")
```
