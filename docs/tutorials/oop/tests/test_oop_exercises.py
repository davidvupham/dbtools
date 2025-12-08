# OOP Exercise Test Suite

"""
Test suite for OOP tutorial exercises.
Run with: pytest test_oop_exercises.py -v
"""

import json
import math
import threading
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

import pytest

# ============================================================================
# Exercise 1: SafeCounter
# ============================================================================


class SafeCounter:
    """Counter that never goes below zero."""

    def __init__(self):
        self._value = 0

    @property
    def value(self) -> int:
        """Read-only value property."""
        return self._value

    def increment(self) -> None:
        """Increase counter by 1."""
        self._value += 1

    def decrement(self) -> None:
        """Decrease counter by 1, but never below 0."""
        if self._value > 0:
            self._value -= 1


class TestSafeCounter:
    def test_initial_value_is_zero(self):
        counter = SafeCounter()
        assert counter.value == 0

    def test_increment(self):
        counter = SafeCounter()
        counter.increment()
        counter.increment()
        assert counter.value == 2

    def test_decrement(self):
        counter = SafeCounter()
        counter.increment()
        counter.increment()
        counter.decrement()
        assert counter.value == 1

    def test_never_goes_negative(self):
        counter = SafeCounter()
        counter.decrement()  # Should stay at 0
        counter.decrement()  # Should still be 0
        assert counter.value == 0

    def test_value_is_read_only(self):
        counter = SafeCounter()
        with pytest.raises(AttributeError):
            counter.value = 10  # Should fail - read-only property


# ============================================================================
# Exercise 2: Shapes (Inheritance & Polymorphism)
# ============================================================================


class Shape(ABC):
    """Abstract base class for shapes."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def area(self) -> float:
        """Calculate area of the shape."""
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("Circle")
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2


def print_areas(shapes: list[Shape]) -> None:
    """Print area of each shape."""
    for shape in shapes:
        print(f"{shape.name} area: {shape.area():.2f}")


class TestShapes:
    def test_rectangle_area(self):
        rect = Rectangle(5, 3)
        assert rect.area() == 15.0

    def test_circle_area(self):
        circle = Circle(2)
        assert abs(circle.area() - 12.566370614359172) < 0.01

    def test_polymorphism(self):
        shapes = [Rectangle(5, 3), Circle(2), Rectangle(10, 4)]
        areas = [shape.area() for shape in shapes]
        assert len(areas) == 3
        assert areas[0] == 15.0
        assert areas[2] == 40.0

    def test_shape_is_abstract(self):
        with pytest.raises(TypeError):
            Shape("test")  # Cannot instantiate abstract class


# ============================================================================
# Exercise 3: Car Composition
# ============================================================================


class Engine:
    def __init__(self, horsepower: int):
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        self.running = True
        return "Engine started"

    def stop(self) -> str:
        self.running = False
        return "Engine stopped"


class GPS:
    def __init__(self):
        self.current_location = "Unknown"

    def navigate_to(self, destination: str) -> str:
        return f"Navigating to {destination}"


class Car:
    def __init__(self, make: str, model: str, engine_hp: int):
        self.make = make
        self.model = model
        self.engine = Engine(engine_hp)
        self.gps = GPS()
        self.speed = 0

    def start(self) -> str:
        return self.engine.start()

    def accelerate(self) -> str:
        if not self.engine.running:
            return "Can't accelerate - engine not running"
        self.speed += 10
        return f"Accelerating to {self.speed} mph"

    def navigate_to(self, destination: str) -> str:
        return self.gps.navigate_to(destination)


class TestCar:
    def test_car_starts(self):
        car = Car("Toyota", "Camry", 200)
        result = car.start()
        assert result == "Engine started"
        assert car.engine.running

    def test_accelerate_when_started(self):
        car = Car("Toyota", "Camry", 200)
        car.start()
        result = car.accelerate()
        assert "Accelerating to 10 mph" in result
        assert car.speed == 10

    def test_cannot_accelerate_when_stopped(self):
        car = Car("Honda", "Civic", 180)
        result = car.accelerate()
        assert "Can't accelerate" in result
        assert car.speed == 0

    def test_gps_navigation(self):
        car = Car("Toyota", "Camry", 200)
        result = car.navigate_to("Home")
        assert "Navigating to Home" in result


# ============================================================================
# Exercise 4: Notifier ABC
# ============================================================================


class Notifier(ABC):
    """Abstract base class for notifiers."""

    @abstractmethod
    def send(self, message: str, recipient: str) -> str:
        """Send a notification."""
        pass


class EmailNotifier(Notifier):
    def send(self, message: str, recipient: str) -> str:
        return f"[EMAIL] Sent to {recipient}: {message}"


class SMSNotifier(Notifier):
    def send(self, message: str, recipient: str) -> str:
        return f"[SMS] Sent to {recipient}: {message}"


def send_notification(notifier: Notifier, message: str, recipient: str) -> str:
    """Send notification using any notifier."""
    return notifier.send(message, recipient)


class TestNotifier:
    def test_email_notifier(self):
        email = EmailNotifier()
        result = send_notification(email, "Hello!", "user@example.com")
        assert "[EMAIL]" in result
        assert "user@example.com" in result
        assert "Hello!" in result

    def test_sms_notifier(self):
        sms = SMSNotifier()
        result = send_notification(sms, "Alert!", "+1234567890")
        assert "[SMS]" in result
        assert "+1234567890" in result

    def test_notifier_is_abstract(self):
        with pytest.raises(TypeError):
            Notifier()  # Cannot instantiate abstract class


# ============================================================================
# Exercise 5: Dataclasses and Serialization
# ============================================================================


@dataclass(slots=True)
class User:
    """User with id and name."""

    id: int
    name: str


class TestUser:
    def test_user_creation(self):
        user = User(id=1, name="Alice")
        assert user.id == 1
        assert user.name == "Alice"

    def test_user_repr(self):
        user = User(id=1, name="Alice")
        assert "User" in repr(user)
        assert "Alice" in repr(user)

    def test_user_equality(self):
        user1 = User(id=1, name="Alice")
        user2 = User(id=1, name="Alice")
        user3 = User(id=2, name="Bob")
        assert user1 == user2
        assert user1 != user3

    def test_json_serialization(self):
        user = User(id=1, name="Alice")
        json_str = json.dumps(asdict(user))
        data = json.loads(json_str)
        user2 = User(**data)
        assert user == user2


# ============================================================================
# Exercise 6: Vector with Dunder Methods
# ============================================================================


class Vector:
    """2D vector with operator overloading."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector(x={self.x}, y={self.y})"

    def __str__(self) -> str:
        return f"<{self.x}, {self.y}>"

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __abs__(self) -> float:
        """Return magnitude of vector."""
        return math.sqrt(self.x**2 + self.y**2)


class TestVector:
    def test_vector_creation(self):
        v = Vector(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_vector_repr(self):
        v = Vector(3, 4)
        assert repr(v) == "Vector(x=3, y=4)"

    def test_vector_str(self):
        v = Vector(3, 4)
        assert str(v) == "<3, 4>"

    def test_vector_addition(self):
        v1 = Vector(3, 4)
        v2 = Vector(1, 2)
        v3 = v1 + v2
        assert v3.x == 4
        assert v3.y == 6

    def test_vector_equality(self):
        v1 = Vector(3, 4)
        v2 = Vector(3, 4)
        v3 = Vector(1, 2)
        assert v1 == v2
        assert v1 != v3

    def test_vector_magnitude(self):
        v = Vector(3, 4)
        assert abs(v) == 5.0  # 3-4-5 triangle


# ============================================================================
# Exercise 7: Thread-Safe Bank Account
# ============================================================================


class BankAccount:
    """Thread-safe bank account."""

    def __init__(self, initial_balance: float = 0):
        self._balance = initial_balance
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        """Deposit money (thread-safe)."""
        with self._lock:
            self._balance += amount

    def withdraw(self, amount: float) -> None:
        """Withdraw money (thread-safe)."""
        with self._lock:
            self._balance -= amount

    @property
    def balance(self) -> float:
        """Get current balance (thread-safe)."""
        with self._lock:
            return self._balance


class TestBankAccount:
    def test_initial_balance(self):
        account = BankAccount(1000)
        assert account.balance == 1000

    def test_deposit(self):
        account = BankAccount(1000)
        account.deposit(500)
        assert account.balance == 1500

    def test_withdraw(self):
        account = BankAccount(1000)
        account.withdraw(200)
        assert account.balance == 800

    def test_thread_safety(self):
        """Test concurrent deposits and withdrawals."""
        account = BankAccount(1000)

        def deposit_money():
            for _ in range(100):
                account.deposit(10)

        def withdraw_money():
            for _ in range(100):
                account.withdraw(5)

        threads = [
            threading.Thread(target=deposit_money),
            threading.Thread(target=deposit_money),
            threading.Thread(target=withdraw_money),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Expected: 1000 + 2*100*10 - 100*5 = 2500
        assert account.balance == 2500


# ============================================================================
# Run all tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
