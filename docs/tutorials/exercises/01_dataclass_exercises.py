"""
Dataclass Exercises - Progressive Difficulty
============================================

Complete these exercises to master @dataclass decorator.
Start with Exercise 1 and work your way up!

Run this file to test your solutions:
    python 01_dataclass_exercises.py
"""

from datetime import datetime

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


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Create Your First Dataclass")
    print("="*60)

    try:
        book = Book("Python Basics", "John Doe", 350)
        print(f"✓ Created book: {book}")
        print(f"✓ Title: {book.title}")
        print(f"✓ Author: {book.author}")
        print(f"✓ Pages: {book.pages}")

        # Test automatic __repr__
        assert "Python Basics" in str(book)
        print("✓ Automatic __repr__ works!")

        # Test automatic __eq__
        book2 = Book("Python Basics", "John Doe", 350)
        assert book == book2
        print("✓ Automatic __eq__ works!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Default Values (Easy)
# ============================================================================
# TODO: Create a dataclass called 'Product' with:
#   - name (str)
#   - price (float)
#   - quantity (int) with default value 0
#   - in_stock (bool) with default value True
#
# Your code here:

# @dataclass
# class Product:
#     pass


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Default Values")
    print("="*60)

    try:
        # Test with defaults
        product1 = Product("Laptop", 999.99)
        print(f"✓ Created product with defaults: {product1}")
        assert product1.quantity == 0
        assert product1.in_stock == True
        print("✓ Default values work!")

        # Test with explicit values
        product2 = Product("Mouse", 29.99, quantity=50, in_stock=True)
        print(f"✓ Created product with explicit values: {product2}")
        assert product2.quantity == 50

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Dataclass from Codebase (Medium)
# ============================================================================
# TODO: Recreate the MonitoringResult dataclass from our codebase.
# It should have:
#   - success (bool)
#   - timestamp (datetime)
#   - account (str)
#   - message (str)
#   - details (dict)
#   - severity (str) with default value "INFO"
#
# Your code here:

# @dataclass
# class MonitoringResult:
#     pass


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Dataclass from Codebase")
    print("="*60)

    try:
        result = MonitoringResult(
            success=True,
            timestamp=datetime.now(),
            account="prod",
            message="All checks passed",
            details={"checks": 5, "failures": 0}
        )
        print(f"✓ Created monitoring result: {result}")
        assert result.severity == "INFO"
        print("✓ Default severity works!")

        # Test with custom severity
        result2 = MonitoringResult(
            success=False,
            timestamp=datetime.now(),
            account="prod",
            message="Connection failed",
            details={},
            severity="CRITICAL"
        )
        print(f"✓ Created critical result: {result2}")
        assert result2.severity == "CRITICAL"

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Mutable Defaults (Medium)
# ============================================================================
# TODO: Create a dataclass called 'ShoppingCart' with:
#   - customer (str)
#   - items (list) - Use field(default_factory=list) for mutable default!
#   - total (float) with default value 0.0
#
# Add a method called 'add_item' that takes item_name and price,
# adds the item to the list, and updates the total.
#
# Your code here:

# @dataclass
# class ShoppingCart:
#     pass


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Mutable Defaults")
    print("="*60)

    try:
        cart1 = ShoppingCart("Alice")
        cart2 = ShoppingCart("Bob")

        cart1.add_item("Book", 15.99)
        cart1.add_item("Pen", 2.99)

        cart2.add_item("Laptop", 999.99)

        print(f"✓ Alice's cart: {cart1}")
        print(f"✓ Bob's cart: {cart2}")

        # Verify carts are independent
        assert len(cart1.items) == 2
        assert len(cart2.items) == 1
        print("✓ Carts are independent!")

        # Verify totals
        assert abs(cart1.total - 18.98) < 0.01
        assert abs(cart2.total - 999.99) < 0.01
        print("✓ Totals calculated correctly!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Frozen Dataclass (Medium)
# ============================================================================
# TODO: Create an immutable dataclass called 'Point' with:
#   - x (float)
#   - y (float)
#   - Use frozen=True to make it immutable
#
# Add a method called 'distance_from_origin' that returns the distance
# from (0, 0) using the formula: sqrt(x^2 + y^2)
#
# Your code here:

# @dataclass(frozen=True)
# class Point:
#     pass


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Frozen Dataclass")
    print("="*60)

    try:
        point = Point(3.0, 4.0)
        print(f"✓ Created point: {point}")

        # Test distance calculation
        distance = point.distance_from_origin()
        print(f"✓ Distance from origin: {distance}")
        assert abs(distance - 5.0) < 0.01
        print("✓ Distance calculation correct!")

        # Test immutability
        try:
            point.x = 10.0
            print("❌ Point should be immutable!")
            return False
        except Exception:
            print("✓ Point is immutable!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Complex Dataclass (Hard)
# ============================================================================
# TODO: Create a dataclass called 'User' with:
#   - username (str)
#   - email (str)
#   - created_at (datetime) with default_factory=datetime.now
#   - is_active (bool) with default True
#   - roles (list) with default_factory=list
#
# Add these methods:
#   - add_role(role: str) - adds a role to the roles list
#   - has_role(role: str) -> bool - checks if user has a role
#   - deactivate() - sets is_active to False
#
# Your code here:

# @dataclass
# class User:
#     pass


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Complex Dataclass")
    print("="*60)

    try:
        user = User("alice", "alice@example.com")
        print(f"✓ Created user: {user}")

        # Test default created_at
        assert user.created_at is not None
        print(f"✓ Created at: {user.created_at}")

        # Test roles
        user.add_role("admin")
        user.add_role("developer")
        print(f"✓ Roles: {user.roles}")

        assert user.has_role("admin")
        assert user.has_role("developer")
        assert not user.has_role("manager")
        print("✓ Role management works!")

        # Test deactivate
        assert user.is_active
        user.deactivate()
        assert not user.is_active
        print("✓ Deactivation works!")

        print("\n✅ Exercise 6 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 6 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 7: Real-World Application (Hard)
# ============================================================================
# TODO: Create a complete monitoring system using dataclasses:
#
# 1. Create an Enum called 'AlertLevel' with: INFO, WARNING, CRITICAL
#
# 2. Create a dataclass called 'Alert' with:
#    - level (AlertLevel)
#    - message (str)
#    - timestamp (datetime) with default_factory=datetime.now
#
# 3. Create a dataclass called 'MonitoringSystem' with:
#    - name (str)
#    - alerts (list) with default_factory=list
#    - is_running (bool) with default True
#
# Add these methods to MonitoringSystem:
#    - add_alert(level: AlertLevel, message: str) - creates and adds an Alert
#    - get_critical_alerts() -> List[Alert] - returns only CRITICAL alerts
#    - get_alert_count() -> int - returns total number of alerts
#    - stop() - sets is_running to False
#
# Your code here:

# from enum import Enum
#
# class AlertLevel(Enum):
#     pass
#
# @dataclass
# class Alert:
#     pass
#
# @dataclass
# class MonitoringSystem:
#     pass


def test_exercise_7():
    """Test Exercise 7"""
    print("\n" + "="*60)
    print("EXERCISE 7: Real-World Application")
    print("="*60)

    try:
        system = MonitoringSystem("Production Monitor")
        print(f"✓ Created monitoring system: {system.name}")

        # Add alerts
        system.add_alert(AlertLevel.INFO, "System started")
        system.add_alert(AlertLevel.WARNING, "High memory usage")
        system.add_alert(AlertLevel.CRITICAL, "Database connection lost")
        system.add_alert(AlertLevel.CRITICAL, "Disk space critical")

        print(f"✓ Added {system.get_alert_count()} alerts")

        # Get critical alerts
        critical = system.get_critical_alerts()
        print(f"✓ Found {len(critical)} critical alerts")
        assert len(critical) == 2

        # Verify alert structure
        for alert in critical:
            print(f"  - {alert.level.name}: {alert.message}")
            assert alert.level == AlertLevel.CRITICAL

        # Test stop
        assert system.is_running
        system.stop()
        assert not system.is_running
        print("✓ System stopped successfully!")

        print("\n✅ Exercise 7 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 7 FAILED: {e}")
        return False


# ============================================================================
# Main Test Runner
# ============================================================================
def run_all_tests():
    """Run all exercises"""
    print("\n" + "="*60)
    print("DATACLASS EXERCISES")
    print("="*60)
    print("\nComplete each exercise by uncommenting and filling in the code.")
    print("Run this file to test your solutions.\n")

    results = []

    # Run each test
    results.append(("Exercise 1", test_exercise_1()))
    results.append(("Exercise 2", test_exercise_2()))
    results.append(("Exercise 3", test_exercise_3()))
    results.append(("Exercise 4", test_exercise_4()))
    results.append(("Exercise 5", test_exercise_5()))
    results.append(("Exercise 6", test_exercise_6()))
    results.append(("Exercise 7", test_exercise_7()))

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")

    print(f"\nTotal: {passed}/{total} exercises passed")

    if passed == total:
        print("\n🎉 Congratulations! You've mastered dataclasses!")
    else:
        print(f"\n💪 Keep practicing! {total - passed} exercises remaining.")


if __name__ == "__main__":
    run_all_tests()
