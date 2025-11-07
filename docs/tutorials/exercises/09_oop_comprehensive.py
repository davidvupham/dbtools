"""
OOP Comprehensive Exercises - Combining All Concepts
=====================================================

These exercises combine multiple OOP concepts you've learned:
- Dataclasses
- Enums
- @classmethod
- super()
- Inheritance
- Abstract Base Classes
- Type hints

Complete these exercises to demonstrate mastery of OOP in Python!

Run this file to test your solutions:
    python 09_oop_comprehensive.py
"""

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

# ============================================================================
# EXERCISE 1: Build a Task Management System (Medium)
# ============================================================================
# TODO: Create a task management system with:
#   - TaskStatus enum (PENDING, IN_PROGRESS, COMPLETED)
#   - Task dataclass with: id, title, status, created_at
#   - TaskManager class with:
#     - add_task(title) -> Task
#     - complete_task(task_id) -> bool
#     - get_tasks_by_status(status) -> List[Task]
#     - get_statistics() -> dict with counts per status
#
# Your code here:

# class TaskStatus(Enum):
#     pass

# @dataclass
# class Task:
#     pass

# class TaskManager:
#     pass


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
# TODO: Create a shape hierarchy with:
#   - Shape (abstract base class) with:
#     - @abstractmethod area() -> float
#     - @abstractmethod perimeter() -> float
#   - Rectangle(Shape) with width, height
#   - Circle(Shape) with radius
#   - Square(Rectangle) with side (use super() to set width=height=side)
#
# Hint: import math for pi
#
# Your code here:

import math

# class Shape(ABC):
#     pass

# class Rectangle(Shape):
#     pass

# class Circle(Shape):
#     pass

# class Square(Rectangle):
#     pass


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
# TODO: Create a User system with:
#   - UserRole enum (GUEST, USER, ADMIN)
#   - User dataclass with: username, email, role, created_at
#   - User class methods:
#     - from_dict(data: dict) -> User
#     - create_admin(username, email) -> User
#     - create_guest() -> User (username="guest", email=None)
#   - Validation in __post_init__:
#     - Username must be 3-20 characters
#     - Email must contain '@' (if provided)
#
# Your code here:

# class UserRole(Enum):
#     pass

# @dataclass
# class User:
#     pass


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
# TODO: Create a library system with composition:
#   - Book dataclass (title, author, isbn)
#   - Member dataclass (name, member_id, borrowed_books: List[Book])
#   - Library class with:
#     - books: List[Book]
#     - members: List[Member]
#     - add_book(book)
#     - add_member(member)
#     - borrow_book(member_id, isbn) -> bool
#     - return_book(member_id, isbn) -> bool
#     - get_available_books() -> List[Book]
#
# Your code here:

# @dataclass
# class Book:
#     pass

# @dataclass
# class Member:
#     pass

# class Library:
#     pass


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
# TODO: Create an e-commerce order system:
#   - OrderStatus enum (PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED)
#   - Product dataclass (id, name, price, stock)
#   - OrderItem dataclass (product: Product, quantity: int)
#   - Order dataclass with:
#     - id, customer_name, items: List[OrderItem], status, created_at
#     - calculate_total() method
#     - add_item(product, quantity) method with stock validation
#     - @classmethod from_cart(customer_name, cart_items) -> Order
#   - Implement __str__ for nice formatting
#
# Your code here:

# class OrderStatus(Enum):
#     pass

# @dataclass
# class Product:
#     pass

# @dataclass
# class OrderItem:
#     pass

# @dataclass
# class Order:
#     pass


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

