"""
Dataclass Exercises - SOLUTIONS
================================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 01_dataclass_exercises_SOLUTIONS.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# ============================================================================
# EXERCISE 1: Create Your First Dataclass (Easy)
# ============================================================================


@dataclass
class Book:
    title: str
    author: str
    pages: int


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "=" * 60)
    print("EXERCISE 1: Create Your First Dataclass")
    print("=" * 60)

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


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    in_stock: bool = True


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "=" * 60)
    print("EXERCISE 2: Default Values")
    print("=" * 60)

    try:
        # Test with defaults
        product1 = Product("Laptop", 999.99)
        print(f"✓ Created product with defaults: {product1}")
        assert product1.quantity == 0
        assert product1.in_stock
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


@dataclass
class MonitoringResult:
    success: bool
    timestamp: datetime
    account: str
    message: str
    details: dict
    severity: str = "INFO"


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "=" * 60)
    print("EXERCISE 3: Dataclass from Codebase")
    print("=" * 60)

    try:
        result = MonitoringResult(
            success=True,
            timestamp=datetime.now(),
            account="prod",
            message="All checks passed",
            details={"checks": 5, "failures": 0},
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
            severity="CRITICAL",
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


@dataclass
class ShoppingCart:
    customer: str
    items: list = field(default_factory=list)
    total: float = 0.0

    def add_item(self, item, price):
        self.items.append(item)
        self.total += price


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "=" * 60)
    print("EXERCISE 4: Mutable Defaults")
    print("=" * 60)

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


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_from_origin(self):
        return (self.x**2 + self.y**2) ** 0.5


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "=" * 60)
    print("EXERCISE 5: Frozen Dataclass")
    print("=" * 60)

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


@dataclass
class User:
    username: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    roles: list = field(default_factory=list)

    def add_role(self, role: str):
        self.roles.append(role)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def deactivate(self):
        self.is_active = False


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "=" * 60)
    print("EXERCISE 6: Complex Dataclass")
    print("=" * 60)

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


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MonitoringSystem:
    name: str
    alerts: list = field(default_factory=list)
    is_running: bool = True

    def add_alert(self, level: AlertLevel, message: str):
        alert = Alert(level=level, message=message)
        self.alerts.append(alert)

    def get_critical_alerts(self) -> list[Alert]:
        return [alert for alert in self.alerts if alert.level == AlertLevel.CRITICAL]

    def get_alert_count(self) -> int:
        return len(self.alerts)

    def stop(self):
        self.is_running = False


def test_exercise_7():
    """Test Exercise 7"""
    print("\n" + "=" * 60)
    print("EXERCISE 7: Real-World Application")
    print("=" * 60)

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
    print("\n" + "=" * 60)
    print("DATACLASS EXERCISES - SOLUTIONS")
    print("=" * 60)
    print("\nValidating that all exercises can be solved correctly.\n")

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
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")

    print(f"\nTotal: {passed}/{total} exercises passed")

    if passed == total:
        print("\n🎉 All exercises validated successfully!")
        print("✅ Exercises are correct and can be solved!")
        return True
    print(f"\n⚠️  {total - passed} exercises failed validation.")
    return False


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
