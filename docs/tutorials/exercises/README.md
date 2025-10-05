# Python Exercises
## Progressive Learning with Hands-On Practice

Welcome to the Python exercises! These exercises are designed to reinforce the concepts you learned in the tutorials through hands-on practice.

---

## 📚 Exercise Structure

Each exercise file focuses on one concept and progresses from **easy** to **hard**:

1. **Easy**: Basic usage and syntax
2. **Medium**: Practical applications
3. **Hard**: Real-world scenarios from the codebase

---

## 🎯 Available Exercises

### Part 3 Concepts (Missing from Parts 1 & 2)

| File | Concept | Exercises | Difficulty |
|------|---------|-----------|------------|
| `01_dataclass_exercises.py` | @dataclass decorator | 7 | Easy → Hard |
| `02_enum_exercises.py` | Enum classes | 7 | Easy → Hard |
| `03_classmethod_exercises.py` | @classmethod decorator | 6 | Easy → Hard |
| `04_super_exercises.py` | super() function | 6 | Easy → Hard |
| `05_comprehension_exercises.py` | List comprehensions | 7 | Easy → Hard |
| `06_enumerate_exercises.py` | enumerate() function | 6 | Easy → Hard |
| `07_sets_exercises.py` | Sets | 6 | Easy → Hard |
| `08_fstrings_exercises.py` | Advanced f-strings | 6 | Easy → Hard |

### Comprehensive Exercises

| File | Concept | Description |
|------|---------|-------------|
| `09_oop_comprehensive.py` | All OOP concepts | Combines classes, inheritance, ABCs |
| `10_final_project.py` | Complete application | Build a mini monitoring system |

---

## 🚀 How to Use These Exercises

### Step 1: Read the Tutorial

Before starting exercises, read the corresponding tutorial section:
- Dataclasses → [Part 3: Dataclasses](../01_PYTHON_BASICS_PART3.md#dataclasses)
- Enums → [Part 3: Enumerations](../01_PYTHON_BASICS_PART3.md#enumerations-enum)
- etc.

### Step 2: Open the Exercise File

```bash
cd docs/tutorials/exercises
code 01_dataclass_exercises.py  # or your preferred editor
```

### Step 3: Complete the Exercises

Each exercise has:
- **Clear instructions** in comments
- **TODO markers** showing where to write code
- **Test functions** to verify your solution
- **Progressive difficulty** from easy to hard

Example:
```python
# ============================================================================
# EXERCISE 1: Create Your First Dataclass (Easy)
# ============================================================================
# TODO: Create a dataclass called 'Book' with these fields:
#   - title (str)
#   - author (str)
#   - pages (int)
#
# Your code here:

# @dataclass
# class Book:
#     pass
```

### Step 4: Run the Tests

```bash
python 01_dataclass_exercises.py
```

You'll see which exercises passed and which need more work:
```
============================================================
EXERCISE 1: Create Your First Dataclass
============================================================
✓ Created book: Book(title='Python Basics', author='John Doe', pages=350)
✓ Automatic __repr__ works!
✓ Automatic __eq__ works!

✅ Exercise 1 PASSED!
```

### Step 5: Iterate

- If an exercise fails, review the tutorial
- Try different approaches
- Test incrementally
- Move to the next exercise when ready

---

## 📖 Exercise Progression

### Beginner Path (Start Here!)

1. **01_dataclass_exercises.py** - Learn modern Python classes
2. **02_enum_exercises.py** - Type-safe constants
3. **06_enumerate_exercises.py** - Pythonic iteration
4. **07_sets_exercises.py** - Unique collections

### Intermediate Path

5. **03_classmethod_exercises.py** - Alternative constructors
6. **04_super_exercises.py** - Proper inheritance
7. **05_comprehension_exercises.py** - Concise list creation
8. **08_fstrings_exercises.py** - String formatting

### Advanced Path

9. **09_oop_comprehensive.py** - Combine all OOP concepts
10. **10_final_project.py** - Build complete application

---

## 💡 Tips for Success

### 1. Start Simple

Don't skip the easy exercises! They build the foundation for harder ones.

### 2. Type the Code

Don't copy-paste. Typing helps you remember and understand.

### 3. Experiment

Try modifying the examples:
- Change parameters
- Add features
- Break things (on purpose!)
- Fix the errors

### 4. Read Error Messages

Error messages tell you what's wrong. Learn to read them!

```python
AttributeError: 'Book' object has no attribute 'title'
# This means: You forgot to define 'title' in your dataclass
```

### 5. Use the REPL

Test small pieces of code in Python's interactive shell:
```bash
python
>>> from dataclasses import dataclass
>>> @dataclass
... class Point:
...     x: int
...     y: int
...
>>> p = Point(10, 20)
>>> print(p)
Point(x=10, y=20)
```

### 6. Reference the Codebase

See how these concepts are used in real code:
- Dataclasses: `gds_snowflake/monitor.py`
- Enums: `gds_snowflake/monitor.py`
- @classmethod: `gds_snowflake/base.py`
- super(): `gds_snowflake/monitor.py`

### 7. Take Breaks

If stuck, take a break! Come back with fresh eyes.

---

## 🎓 Learning Objectives

By completing these exercises, you will be able to:

### Dataclasses
- ✅ Create dataclasses with proper type hints
- ✅ Use default values and default_factory
- ✅ Create immutable dataclasses with frozen=True
- ✅ Understand when to use dataclasses vs regular classes

### Enums
- ✅ Create type-safe enumerations
- ✅ Use enums in functions and conditionals
- ✅ Iterate over enum values
- ✅ Add methods to enums

### @classmethod
- ✅ Create alternative constructors
- ✅ Implement factory methods
- ✅ Understand cls vs self
- ✅ Use @classmethod with inheritance

### super()
- ✅ Call parent class methods
- ✅ Properly initialize parent classes
- ✅ Work with multiple inheritance
- ✅ Understand Method Resolution Order (MRO)

### List Comprehensions
- ✅ Create lists concisely
- ✅ Filter and transform data
- ✅ Use nested comprehensions
- ✅ Know when NOT to use comprehensions

### enumerate()
- ✅ Get index and item together
- ✅ Start from custom index
- ✅ Write Pythonic loops
- ✅ Avoid range(len()) anti-pattern

### Sets
- ✅ Create and manipulate sets
- ✅ Use set operations (union, intersection)
- ✅ Remove duplicates efficiently
- ✅ Fast membership testing

### f-strings
- ✅ Format strings with variables
- ✅ Format numbers and dates
- ✅ Align and pad strings
- ✅ Use expressions in f-strings

---

## 📊 Progress Tracking

Track your progress through the exercises:

### Part 3 Concepts
- [ ] Dataclasses (7 exercises)
- [ ] Enums (7 exercises)
- [ ] @classmethod (6 exercises)
- [ ] super() (6 exercises)
- [ ] List Comprehensions (7 exercises)
- [ ] enumerate() (6 exercises)
- [ ] Sets (6 exercises)
- [ ] f-strings (6 exercises)

### Advanced
- [ ] OOP Comprehensive (5 exercises)
- [ ] Final Project (1 project)

**Total: 57 exercises**

---

## 🔧 Troubleshooting

### "NameError: name 'Book' is not defined"

You need to uncomment and complete the class definition:
```python
# Before (commented out):
# @dataclass
# class Book:
#     pass

# After (completed):
@dataclass
class Book:
    title: str
    author: str
    pages: int
```

### "TypeError: missing required positional argument"

You forgot a required field:
```python
# Wrong:
book = Book("Python Basics")  # Missing author and pages

# Right:
book = Book("Python Basics", "John Doe", 350)
```

### "AttributeError: 'X' object has no attribute 'Y'"

You forgot to define an attribute or method:
```python
# Wrong:
@dataclass
class Book:
    title: str
    # Forgot author and pages!

# Right:
@dataclass
class Book:
    title: str
    author: str
    pages: int
```

### Tests Still Failing?

1. Read the error message carefully
2. Check the tutorial for examples
3. Look at the test code to see what's expected
4. Try printing intermediate values
5. Test one piece at a time

---

## 🎯 Exercise Solutions

Solutions are NOT provided intentionally! Here's why:

1. **Learning by doing**: Struggling is part of learning
2. **Problem-solving skills**: Figure it out yourself
3. **Real-world preparation**: No solutions in production code
4. **Deeper understanding**: You'll remember what you figured out

### But I'm Really Stuck!

If you're stuck:

1. **Re-read the tutorial** - The answer is there!
2. **Check the codebase** - See real examples
3. **Break it down** - Solve one piece at a time
4. **Use print()** - See what your code is doing
5. **Start over** - Sometimes a fresh start helps

### Hints Available

Each exercise includes hints in the comments:
```python
# Hint: Use field(default_factory=list) for mutable defaults!
```

---

## 📚 Additional Resources

### Official Documentation
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Enum](https://docs.python.org/3/library/enum.html)
- [Python super()](https://docs.python.org/3/library/functions.html#super)

### Tutorials
- [Part 1: Python Fundamentals](../01_PYTHON_BASICS_FOR_THIS_PROJECT.md)
- [Part 2: Advanced Concepts](../01_PYTHON_BASICS_PART2.md)
- [Part 3: Missing Concepts](../01_PYTHON_BASICS_PART3.md)

### Codebase Examples
- `gds_snowflake/monitor.py` - Dataclasses and Enums
- `gds_snowflake/base.py` - @classmethod and ABCs
- `gds_snowflake/connection.py` - super() and inheritance

---

## 🎉 Completion Certificate

When you complete all exercises, you'll have:

✅ Mastered all Python concepts used in the codebase
✅ Written 50+ working Python programs
✅ Solved real-world programming problems
✅ Built a complete monitoring system
✅ Gained confidence in Python programming

**You're ready to contribute to the codebase!**

---

## 🤝 Contributing

Found a typo? Have a suggestion? Want to add more exercises?

The exercises are designed to be:
- **Progressive**: Easy to hard
- **Practical**: Real-world applications
- **Testable**: Automatic verification
- **Educational**: Clear learning objectives

---

## 📝 Quick Reference

### Running Exercises
```bash
# Run single exercise
python 01_dataclass_exercises.py

# Run all exercises (if you create a runner)
python run_all_exercises.py
```

### Exercise Structure
```python
# 1. Instructions
# TODO: Create a class...

# 2. Your code
# class MyClass:
#     pass

# 3. Test function
def test_exercise_1():
    # Tests your code
    pass

# 4. Test runner
if __name__ == "__main__":
    run_all_tests()
```

### Getting Help
1. Read the tutorial
2. Check the codebase
3. Read error messages
4. Use print() for debugging
5. Break problem into smaller pieces

---

**Ready to start? Begin with `01_dataclass_exercises.py`!**

Good luck, and happy coding! 🐍
