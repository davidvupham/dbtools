# Metaprogramming

> **Note:** This is an advanced topic.

## What is Metaprogramming?

Metaprogramming is code that writes or manipulates code.
In Python, this often means:

1. **Decorators** (Changing functions)
2. **Metaclasses** (Changing classes)
3. **Descriptors** (Changing attributes)

## Concepts

* `type()` is actually a class that creates classes.
* `__getattr__` and `__setattr__` intercept attribute access.
