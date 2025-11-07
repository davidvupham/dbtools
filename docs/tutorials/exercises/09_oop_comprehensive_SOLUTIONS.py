"""
OOP Comprehensive Exercises - SOLUTIONS
========================================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 09_oop_comprehensive_SOLUTIONS.py
"""

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import math

# ============================================================================
# EXERCISE 1: Build a Task Management System (Medium)
# ============================================================================

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)


class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
        self._next_id = 1

    def add_task(self, title: str) -> Task:
        task = Task(id=self._next_id, title=title)
        self.tasks.append(task)
        self._next_id += 1
        return task

    def complete_task(self, task_id: int) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return [task for task in self.tasks if task.status == status]

    def get_statistics(self) -> dict:
        stats = {status: 0 for status in TaskStatus}
        for task in self.tasks:
            stats[task.status] += 1
        return stats


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Build a Task Management System")
    print("="*60)

    try:
        manager = TaskManager()
        print("✓ Created TaskManager")

        # Add tasks
        task1 = manager.add_task("Write documentation")
        task2 = manager.add_task("Write tests")
        task3 = manager.add_task("Deploy code")
        print(f"✓ Added 3 tasks")

        # Check initial status
        assert task1.status == TaskStatus.PENDING
        print("✓ Tasks start as PENDING")

        # Complete a task
        manager.complete_task(task1.id)
        assert task1.status == TaskStatus.COMPLETED
        print("✓ Can complete tasks")

        # Get tasks by status
        pending = manager.get_tasks_by_status(TaskStatus.PENDING)
        assert len(pending) == 2
        print("✓ Can filter tasks by status")

        # Get statistics
        stats = manager.get_statistics()
        assert stats[TaskStatus.COMPLETED] == 1
        assert stats[TaskStatus.PENDING] == 2
        print("✓ Statistics are correct")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EXERCISE 2: Inheritance with Shapes (Medium)
# ============================================================================

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Inheritance with Shapes")
    print("="*60)

    try:
        # Test Rectangle
        rect = Rectangle(10, 5)
        assert rect.area() == 50
        assert rect.perimeter() == 30
        print(f"✓ Rectangle: area={rect.area()}, perimeter={rect.perimeter()}")

        # Test Circle
        circle = Circle(5)
        assert abs(circle.area() - 78.54) < 0.01
        assert abs(circle.perimeter() - 31.42) < 0.01
        print(f"✓ Circle: area={circle.area():.2f}, perimeter={circle.perimeter():.2f}")

        # Test Square
        square = Square(7)
        assert square.area() == 49
        assert square.perimeter() == 28
        assert square.width == square.height == 7
        print(f"✓ Square: area={square.area()}, perimeter={square.perimeter()}")
        print("✓ Square uses super() correctly!")

        # Test that Shape is abstract
        try:
            shape = Shape()
            print("❌ Should not be able to instantiate abstract Shape")
            return False
        except TypeError:
            print("✓ Cannot instantiate abstract Shape!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EXERCISE 3: Alternative Constructors and Validation (Medium-Hard)
# ============================================================================

class UserRole(Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    username: str
    email: Optional[str]
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Validate username
        if len(self.username) < 3 or len(self.username) > 20:
            raise ValueError("Username must be 3-20 characters")

        # Validate email (if provided)
        if self.email is not None and '@' not in self.email:
            raise ValueError("Email must contain '@'")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            username=data["username"],
            email=data["email"],
            role=data["role"]
        )

    @classmethod
    def create_admin(cls, username: str, email: str):
        return cls(username, email, UserRole.ADMIN)

    @classmethod
    def create_guest(cls):
        return cls("guest", None, UserRole.GUEST)


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Alternative Constructors and Validation")
    print("="*60)

    try:
        # Test regular constructor
        user1 = User("john_doe", "john@example.com", UserRole.USER)
        print(f"✓ Created user: {user1.username}, role={user1.role.name}")

        # Test from_dict
        user_data = {
            "username": "jane_smith",
            "email": "jane@example.com",
            "role": UserRole.ADMIN
        }
        user2 = User.from_dict(user_data)
        assert user2.username == "jane_smith"
        assert user2.role == UserRole.ADMIN
        print(f"✓ Created from dict: {user2.username}")

        # Test create_admin
        admin = User.create_admin("admin", "admin@example.com")
        assert admin.role == UserRole.ADMIN
        print(f"✓ Created admin: {admin.username}")

        # Test create_guest
        guest = User.create_guest()
        assert guest.username == "guest"
        assert guest.role == UserRole.GUEST
        assert guest.email is None
        print(f"✓ Created guest user")

        # Test validation - short username
        try:
            invalid_user = User("ab", "test@example.com", UserRole.USER)
            print("❌ Should have raised ValueError for short username")
            return False
        except ValueError:
            print("✓ Username validation works!")

        # Test validation - invalid email
        try:
            invalid_user = User("john", "invalid-email", UserRole.USER)
            print("❌ Should have raised ValueError for invalid email")
            return False
        except ValueError:
            print("✓ Email validation works!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EXERCISE 4: Composition and Aggregation (Hard)
# ============================================================================

@dataclass
class Book:
    title: str
    author: str
    isbn: str


@dataclass
class Member:
    name: str
    member_id: str
    borrowed_books: List[Book] = field(default_factory=list)


class Library:
    def __init__(self):
        self.books: List[Book] = []
        self.members: List[Member] = []

    def add_book(self, book: Book):
        self.books.append(book)

    def add_member(self, member: Member):
        self.members.append(member)

    def borrow_book(self, member_id: str, isbn: str) -> bool:
        # Find member
        member = next((m for m in self.members if m.member_id == member_id), None)
        if not member:
            return False

        # Find book
        book = next((b for b in self.books if b.isbn == isbn), None)
        if not book:
            return False

        # Check if book is already borrowed
        if book in [b for m in self.members for b in m.borrowed_books]:
            return False

        # Borrow book
        member.borrowed_books.append(book)
        return True

    def return_book(self, member_id: str, isbn: str) -> bool:
        # Find member
        member = next((m for m in self.members if m.member_id == member_id), None)
        if not member:
            return False

        # Find book in member's borrowed books
        book = next((b for b in member.borrowed_books if b.isbn == isbn), None)
        if not book:
            return False

        # Return book
        member.borrowed_books.remove(book)
        return True

    def get_available_books(self) -> List[Book]:
        borrowed_books = [b for m in self.members for b in m.borrowed_books]
        return [b for b in self.books if b not in borrowed_books]


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Composition and Aggregation")
    print("="*60)

    try:
        library = Library()
        print("✓ Created Library")

        # Add books
        book1 = Book("Python Basics", "John Doe", "978-1234567890")
        book2 = Book("Advanced Python", "Jane Smith", "978-0987654321")
        library.add_book(book1)
        library.add_book(book2)
        print("✓ Added books to library")

        # Add member
        member1 = Member("Alice", "M001", [])
        library.add_member(member1)
        print("✓ Added member to library")

        # Check available books
        available = library.get_available_books()
        assert len(available) == 2
        print("✓ Both books initially available")

        # Borrow book
        success = library.borrow_book("M001", "978-1234567890")
        assert success == True
        assert len(member1.borrowed_books) == 1
        print("✓ Member borrowed book")

        # Check available books again
        available = library.get_available_books()
        assert len(available) == 1
        print("✓ One book now unavailable")

        # Try to borrow same book again
        success = library.borrow_book("M001", "978-1234567890")
        assert success == False
        print("✓ Cannot borrow same book twice")

        # Return book
        success = library.return_book("M001", "978-1234567890")
        assert success == True
        assert len(member1.borrowed_books) == 0
        print("✓ Member returned book")

        # Check available books
        available = library.get_available_books()
        assert len(available) == 2
        print("✓ Book is available again")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EXERCISE 5: Bringing It All Together (Hard)
# ============================================================================

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Product:
    id: str
    name: str
    price: float
    stock: int


@dataclass
class OrderItem:
    product: Product
    quantity: int


@dataclass
class Order:
    id: str
    customer_name: str
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)

    def calculate_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

    def add_item(self, product: Product, quantity: int):
        if product.stock < quantity:
            raise ValueError(f"Insufficient stock for {product.name}")
        product.stock -= quantity
        self.items.append(OrderItem(product, quantity))

    @classmethod
    def from_cart(cls, customer_name: str, cart_items: List[OrderItem]):
        import uuid
        order_id = str(uuid.uuid4())[:8]
        return cls(id=order_id, customer_name=customer_name, items=cart_items)

    def __str__(self):
        items_str = "\n".join(f"  - {item.product.name} x{item.quantity}" for item in self.items)
        return f"""Order #{self.id}
Customer: {self.customer_name}
Status: {self.status.value}
Items:
{items_str}
Total: ${self.calculate_total():.2f}"""


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Bringing It All Together")
    print("="*60)

    try:
        # Create products
        laptop = Product("P001", "Laptop", 999.99, 10)
        mouse = Product("P002", "Mouse", 29.99, 50)
        print("✓ Created products")

        # Create order
        order = Order.from_cart("Alice", [])
        assert order.status == OrderStatus.PENDING
        print("✓ Created order from cart")

        # Add items
        order.add_item(laptop, 1)
        order.add_item(mouse, 2)
        print("✓ Added items to order")

        # Calculate total
        total = order.calculate_total()
        expected_total = 999.99 + (29.99 * 2)
        assert abs(total - expected_total) < 0.01
        print(f"✓ Total calculated: ${total:.2f}")

        # Check stock was reduced
        assert laptop.stock == 9
        assert mouse.stock == 48
        print("✓ Stock was reduced")

        # Try to add more than available stock
        try:
            order.add_item(laptop, 20)
            print("❌ Should have raised ValueError for insufficient stock")
            return False
        except ValueError:
            print("✓ Stock validation works!")

        # Test string representation
        order_str = str(order)
        assert "Alice" in order_str
        assert "PENDING" in order_str or "pending" in order_str.lower()
        print("✓ String representation works")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all exercise tests"""
    print("\n" + "="*60)
    print("OOP COMPREHENSIVE EXERCISES - TEST RUNNER")
    print("="*60)

    results = [
        test_exercise_1(),
        test_exercise_2(),
        test_exercise_3(),
        test_exercise_4(),
        test_exercise_5(),
    ]

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 Congratulations! You've mastered OOP in Python!")
        print("\nYou can now:")
        print("  • Design class hierarchies")
        print("  • Use dataclasses effectively")
        print("  • Apply inheritance and composition")
        print("  • Create alternative constructors")
        print("  • Validate data in __post_init__")
        print("  • Use abstract base classes")
        print("  • Build real-world systems")
        print("\n🚀 Ready for the final project!")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

