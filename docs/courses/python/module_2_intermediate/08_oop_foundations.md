# OOP Foundations

## Classes and Objects (Review)

```python
class Dog:
    def __init__(self, name):
        self.name = name  # Instance variable

    def bark(self):       # Instance method
        return "Woof!"
```

## Class Methods (`@classmethod`)

A class method works with the class itself (`cls`) rather than the instance (`self`).

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_string):
        """Alternative constructor: '2023-12-25'"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)

d = Date.from_string("2023-12-25")
```

## Inheritance and `super()`

`super()` allows you to call methods from the parent class.

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # Call parent init
        self.breed = breed
```

### Why use `super()`?

- Avoids hardcoding the parent class name (`Animal.__init__`).
- essential for multiple inheritance (MRO).
