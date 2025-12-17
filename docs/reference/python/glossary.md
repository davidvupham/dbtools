# Python Glossary

Definitions of common Python terminology.

## A

* **Argument**: Value passed to a function.
* **Async/Await**: Syntax for writing asynchronous code using coroutines.
* **Attribute**: A value associated with an object (`obj.attribute`).

## C

* **Callable**: Any object that can be called (functions, classes, objects with `__call__`).
* **Class**: A blueprint for creating objects.
* **Closure**: An inner function that remembers values from its enclosing scope.
* **Context Manager**: An object that controls the environment (`with` statement).
* **Coroutine**: A function that can pause and resume execution (`async def`).

## D

* **Decorator**: A function that modifies another function or class.
* **Descriptor**: An object that manages access to an attribute (used for properties).
* **Docstring**: String literal (`"""..."""`) used to document a module, class, or function.
* **Duck Typing**: "If it walks like a duck and quacks like a duck, it's a duck." Checking for behavior rather than type.

## G

* **Generator**: A function that returns an iterator using `yield`.
* **GIL (Global Interpreter Lock)**: A mutex that allows only one thread to control the Python interpreter, limiting CPU-bound concurrency.

## I

* **Immutable**: An object whose value cannot be changed (e.g., tuple, str, int).
* **Iterable**: An object capable of returning its members one at a time (e.g., list, str).
* **Iterator**: An object representing a stream of data.

## K

* **Kwargs (Keyword Arguments)**: Arguments passed by name (`func(a=1)`).

## L

* **Lambda**: An anonymous inline function (`lambda x: x + 1`).
* **LBYL (Look Before You Leap)**: Checking for preconditions before making a call (`if key in dict:`). Contrast with EAFP.

## M

* **Method**: A function defined inside a class.
* **Module**: A file containing Python definitions and statements.
* **MRO (Method Resolution Order)**: The order in which base classes are searched for a member.

## N

* **Namespace**: A mapping from names to objects.

## P

* **Package**: A Python module which can contain submodules.
* **Parameter**: A name used inside a function definition.
* **PEP (Python Enhancement Proposal)**: Design documents providing information to the Python community (e.g., PEP 8).

## R

* **REPL (Read-Eval-Print Loop)**: Interactive shell.

## S

* **Slice**: A subset of a sequence (`list[1:3]`).

## T

* **Type Hint**: Annotation specifying the expected type (`x: int`).

## V

* **Virtual Environment**: Isolated Python environment to manage dependencies.
