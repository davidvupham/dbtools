"""
super() Function Exercises - Progressive Difficulty
====================================================

Complete these exercises to master super() and inheritance.
Start with Exercise 1 and work your way up!

Run this file to test your solutions:
    python 04_super_exercises.py
"""

# ============================================================================
# EXERCISE 1: Basic super() Usage (Easy)
# ============================================================================
# TODO: Create a base class 'Vehicle' and subclass 'Car':
#   Vehicle:
#     - __init__(self, brand: str, year: int)
#     - describe() returns "brand year"
#   Car:
#     - __init__(self, brand: str, year: int, doors: int)
#     - Use super() to call parent __init__
#     - Override describe() to add doors info
#
# Your code here:

# class Vehicle:
#     pass

# class Car(Vehicle):
#     pass


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Basic super() Usage")
    print("="*60)

    try:
        # Test Vehicle
        v = Vehicle("Toyota", 2020)
        print(f"✓ Created vehicle: {v.describe()}")
        assert "Toyota" in v.describe()
        print("✓ Vehicle describe works!")

        # Test Car
        c = Car("Honda", 2021, 4)
        print(f"✓ Created car: {c.describe()}")
        assert c.brand == "Honda"
        assert c.year == 2021
        assert c.doors == 4
        print("✓ Car uses super() correctly!")
        assert "doors" in c.describe().lower() or "4" in c.describe()
        print("✓ Car overrides describe!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: super() with Multiple Methods (Easy-Medium)
# ============================================================================
# TODO: Create a base class 'Employee' and subclass 'Manager':
#   Employee:
#     - __init__(self, name: str, salary: float)
#     - get_bonus() returns salary * 0.1
#   Manager:
#     - __init__(self, name: str, salary: float, team_size: int)
#     - Use super() in __init__
#     - Override get_bonus() to add team bonus (team_size * 500)
#     - Use super() to get base bonus first
#
# Your code here:

# class Employee:
#     pass

# class Manager(Employee):
#     pass


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: super() with Multiple Methods")
    print("="*60)

    try:
        # Test Employee
        emp = Employee("John", 50000)
        print(f"✓ Created employee: {emp.name}, salary=${emp.salary}")
        bonus = emp.get_bonus()
        print(f"✓ Employee bonus: ${bonus}")
        assert bonus == 5000  # 10% of 50000
        print("✓ Employee bonus calculation correct!")

        # Test Manager
        mgr = Manager("Jane", 80000, 5)
        print(f"✓ Created manager: {mgr.name}, team size={mgr.team_size}")
        mgr_bonus = mgr.get_bonus()
        print(f"✓ Manager bonus: ${mgr_bonus}")
        # Should be base bonus (8000) + team bonus (2500) = 10500
        assert mgr_bonus == 10500
        print("✓ Manager uses super() to get base bonus!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Three-Level Inheritance (Medium)
# ============================================================================
# TODO: Create three classes: Shape -> Rectangle -> Square
#   Shape:
#     - __init__(self, color: str)
#     - area() returns 0 (placeholder)
#   Rectangle (inherits from Shape):
#     - __init__(self, color: str, width: float, height: float)
#     - Use super() in __init__
#     - Override area() to return width * height
#   Square (inherits from Rectangle):
#     - __init__(self, color: str, side: float)
#     - Use super() in __init__ with side for both width and height
#
# Your code here:

# class Shape:
#     pass

# class Rectangle(Shape):
#     pass

# class Square(Rectangle):
#     pass


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Three-Level Inheritance")
    print("="*60)

    try:
        # Test Shape
        s = Shape("blue")
        print(f"✓ Created shape: color={s.color}")
        assert s.area() == 0
        print("✓ Shape base class works!")

        # Test Rectangle
        r = Rectangle("red", 10, 5)
        print(f"✓ Created rectangle: {r.width}x{r.height}, color={r.color}")
        assert r.area() == 50
        print("✓ Rectangle calculates area correctly!")

        # Test Square
        sq = Square("green", 7)
        print(f"✓ Created square: {sq.width}x{sq.height}, color={sq.color}")
        assert sq.width == sq.height == 7
        assert sq.area() == 49
        print("✓ Square uses super() through Rectangle!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Understanding Method Resolution Order (MRO) (Medium)
# ============================================================================
# TODO: Create a diamond inheritance pattern:
#   A (base):
#     - __init__(self, name: str)
#     - greet() returns f"Hello from {name}"
#   B (inherits from A):
#     - __init__(self, name: str, b_attr: str)
#     - Use super().__init__(name)
#   C (inherits from A):
#     - __init__(self, name: str, c_attr: str)
#     - Use super().__init__(name)
#   D (inherits from B and C):
#     - __init__(self, name: str, b_attr: str, c_attr: str, d_attr: str)
#     - Use super().__init__(name, b_attr) - MRO will handle C
#
# Hint: Use ClassName.__mro__ to see method resolution order
#
# Your code here:

# class A:
#     pass

# class B(A):
#     pass

# class C(A):
#     pass

# class D(B, C):
#     pass


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Understanding Method Resolution Order (MRO)")
    print("="*60)

    try:
        # Test A
        a = A("Base")
        print(f"✓ Created A: {a.greet()}")

        # Test B
        b = B("B_instance", "b_value")
        print(f"✓ Created B: {b.name}, {b.b_attr}")

        # Test C
        c = C("C_instance", "c_value")
        print(f"✓ Created C: {c.name}, {c.c_attr}")

        # Test D (diamond pattern)
        d = D("D_instance", "b_val", "c_val", "d_val")
        print(f"✓ Created D: {d.name}, b={d.b_attr}, c={d.c_attr}, d={d.d_attr}")
        assert d.b_attr == "b_val"
        assert d.c_attr == "c_val"
        assert d.d_attr == "d_val"
        print("✓ Diamond inheritance works with super()!")

        # Show MRO
        print(f"✓ MRO for D: {[cls.__name__ for cls in D.__mro__]}")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Cooperative Inheritance with Mixins (Medium-Hard)
# ============================================================================
# TODO: Create a mixin pattern for logging:
#   LoggerMixin:
#     - log(self, message: str) - prints "[ClassName]: message"
#   TimestampMixin:
#     - get_timestamp(self) - returns current time as string
#   Task:
#     - __init__(self, title: str, description: str)
#   LoggedTask (inherits from LoggerMixin, TimestampMixin, Task):
#     - __init__(self, title: str, description: str)
#     - Use super().__init__() properly
#     - create() method that logs creation with timestamp
#
# Your code here:

from datetime import datetime

# class LoggerMixin:
#     pass

# class TimestampMixin:
#     pass

# class Task:
#     pass

# class LoggedTask(LoggerMixin, TimestampMixin, Task):
#     pass


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Cooperative Inheritance with Mixins")
    print("="*60)

    try:
        # Test Task
        t = Task("Basic Task", "Do something")
        print(f"✓ Created task: {t.title}")

        # Test LoggedTask
        lt = LoggedTask("Important Task", "Critical work")
        print(f"✓ Created logged task: {lt.title}")
        assert lt.title == "Important Task"
        assert lt.description == "Critical work"
        print("✓ LoggedTask inherits from Task correctly!")

        # Test mixin methods
        print(f"✓ Logger: ", end="")
        lt.log("Testing logger")
        print(f"✓ Timestamp: {lt.get_timestamp()}")

        # Test create method
        print(f"✓ Create method: ", end="")
        lt.create()

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Real-World Example - Database Models (Hard)
# ============================================================================
# TODO: Create a database model hierarchy:
#   BaseModel:
#     - __init__(self, id: int)
#     - save() prints "Saving to database..."
#     - delete() prints "Deleting from database..."
#   TimestampModel (inherits from BaseModel):
#     - __init__(self, id: int, created_at: str, updated_at: str)
#     - Use super().__init__()
#     - Override save() to update updated_at, then call super().save()
#   User (inherits from TimestampModel):
#     - __init__(self, id: int, username: str, email: str)
#     - Set created_at and updated_at to current time
#     - Override save() to validate email, then call super().save()
#
# Your code here:

# class BaseModel:
#     pass

# class TimestampModel(BaseModel):
#     pass

# class User(TimestampModel):
#     pass


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Real-World Example - Database Models")
    print("="*60)

    try:
        # Test BaseModel
        base = BaseModel(1)
        print(f"✓ Created base model: id={base.id}")
        base.save()
        print("✓ BaseModel save works!")

        # Test TimestampModel
        ts = TimestampModel(2, "2024-01-01", "2024-01-01")
        print(f"✓ Created timestamp model: id={ts.id}, created={ts.created_at}")
        ts.save()
        print("✓ TimestampModel updates timestamp on save!")

        # Test User
        user = User(3, "john_doe", "john@example.com")
        print(f"✓ Created user: {user.username}, {user.email}")
        assert user.id == 3
        assert user.created_at is not None
        assert user.updated_at is not None
        print("✓ User has id and timestamps!")

        # Test cascading save
        print("✓ Testing cascading save:")
        user.save()
        print("✓ User save cascades through TimestampModel to BaseModel!")

        # Test validation
        try:
            invalid_user = User(4, "jane", "invalid-email")
            invalid_user.save()
            print("❌ Should have raised ValueError for invalid email")
            return False
        except ValueError:
            print("✓ Email validation works!")

        print("\n✅ Exercise 6 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 6 FAILED: {e}")
        return False


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all exercise tests"""
    print("\n" + "="*60)
    print("SUPER() EXERCISES - TEST RUNNER")
    print("="*60)

    results = [
        test_exercise_1(),
        test_exercise_2(),
        test_exercise_3(),
        test_exercise_4(),
        test_exercise_5(),
        test_exercise_6(),
    ]

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 Congratulations! All exercises passed!")
        print("You now understand:")
        print("  • Basic super() usage")
        print("  • Method resolution order (MRO)")
        print("  • Multiple inheritance")
        print("  • Diamond problem")
        print("  • Mixin patterns")
        print("  • Real-world inheritance hierarchies")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

