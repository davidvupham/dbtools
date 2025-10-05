"""
Enum Exercises - SOLUTIONS
===========================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 02_enum_exercises_SOLUTIONS.py
"""

from enum import Enum, auto

# ============================================================================
# EXERCISE 1: Create Your First Enum (Easy)
# ============================================================================

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Create Your First Enum")
    print("="*60)

    try:
        # Test enum values
        print(f"✓ RED: {Color.RED}")
        print(f"✓ GREEN: {Color.GREEN}")
        print(f"✓ BLUE: {Color.BLUE}")

        # Test value access
        assert Color.RED.value == "red"
        assert Color.GREEN.value == "green"
        print("✓ Values are correct!")

        # Test comparison
        assert Color.RED == Color.RED
        assert Color.RED != Color.BLUE
        print("✓ Comparison works!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Enum from Codebase (Easy)
# ============================================================================

class AlertSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Enum from Codebase")
    print("="*60)

    try:
        # Test all severity levels
        print(f"✓ INFO: {AlertSeverity.INFO}")
        print(f"✓ WARNING: {AlertSeverity.WARNING}")
        print(f"✓ CRITICAL: {AlertSeverity.CRITICAL}")

        # Test in conditional
        severity = AlertSeverity.CRITICAL
        if severity == AlertSeverity.CRITICAL:
            print("✓ Critical alert detected!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Using Enums in Functions (Medium)
# ============================================================================

class Environment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


def get_database_url(env: Environment) -> str:
    urls = {
        Environment.DEVELOPMENT: "localhost:5432",
        Environment.STAGING: "staging-db.company.com",
        Environment.PRODUCTION: "prod-db.company.com"
    }
    return urls[env]


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Using Enums in Functions")
    print("="*60)

    try:
        # Test each environment
        dev_url = get_database_url(Environment.DEVELOPMENT)
        print(f"✓ Development URL: {dev_url}")
        assert dev_url == "localhost:5432"

        staging_url = get_database_url(Environment.STAGING)
        print(f"✓ Staging URL: {staging_url}")
        assert staging_url == "staging-db.company.com"

        prod_url = get_database_url(Environment.PRODUCTION)
        print(f"✓ Production URL: {prod_url}")
        assert prod_url == "prod-db.company.com"

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Auto-numbering Enums (Medium)
# ============================================================================

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


def is_terminal_status(status: Status) -> bool:
    return status in (Status.COMPLETED, Status.FAILED)


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Auto-numbering Enums")
    print("="*60)

    try:
        # Test auto values
        print(f"✓ PENDING value: {Status.PENDING.value}")
        print(f"✓ RUNNING value: {Status.RUNNING.value}")
        print(f"✓ COMPLETED value: {Status.COMPLETED.value}")
        print(f"✓ FAILED value: {Status.FAILED.value}")

        # Test terminal status
        assert not is_terminal_status(Status.PENDING)
        assert not is_terminal_status(Status.RUNNING)
        assert is_terminal_status(Status.COMPLETED)
        assert is_terminal_status(Status.FAILED)
        print("✓ Terminal status detection works!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Iterating Over Enums (Medium)
# ============================================================================

class DayOfWeek(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


def is_weekend(day: DayOfWeek) -> bool:
    return day in (DayOfWeek.SATURDAY, DayOfWeek.SUNDAY)


def get_all_weekdays() -> list:
    return [day.name for day in DayOfWeek if not is_weekend(day)]


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Iterating Over Enums")
    print("="*60)

    try:
        # Test weekend detection
        assert not is_weekend(DayOfWeek.MONDAY)
        assert not is_weekend(DayOfWeek.FRIDAY)
        assert is_weekend(DayOfWeek.SATURDAY)
        assert is_weekend(DayOfWeek.SUNDAY)
        print("✓ Weekend detection works!")

        # Test weekdays list
        weekdays = get_all_weekdays()
        print(f"✓ Weekdays: {weekdays}")
        assert len(weekdays) == 5
        assert "MONDAY" in weekdays
        assert "FRIDAY" in weekdays
        assert "SATURDAY" not in weekdays
        print("✓ Weekdays list correct!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Enum with Methods (Hard)
# ============================================================================

class HttpStatus(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    SERVER_ERROR = 500

    def is_success(self) -> bool:
        return 200 <= self.value < 300

    def is_client_error(self) -> bool:
        return 400 <= self.value < 500

    def is_server_error(self) -> bool:
        return 500 <= self.value < 600

    def get_category(self) -> str:
        if self.is_success():
            return "Success"
        if self.is_client_error():
            return "Client Error"
        if self.is_server_error():
            return "Server Error"
        return "Unknown"


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Enum with Methods")
    print("="*60)

    try:
        # Test success statuses
        assert HttpStatus.OK.is_success()
        assert HttpStatus.CREATED.is_success()
        assert not HttpStatus.NOT_FOUND.is_success()
        print("✓ is_success() works!")

        # Test client errors
        assert HttpStatus.BAD_REQUEST.is_client_error()
        assert HttpStatus.NOT_FOUND.is_client_error()
        assert not HttpStatus.OK.is_client_error()
        print("✓ is_client_error() works!")

        # Test server errors
        assert HttpStatus.SERVER_ERROR.is_server_error()
        assert not HttpStatus.NOT_FOUND.is_server_error()
        print("✓ is_server_error() works!")

        # Test categories
        assert HttpStatus.OK.get_category() == "Success"
        assert HttpStatus.NOT_FOUND.get_category() == "Client Error"
        assert HttpStatus.SERVER_ERROR.get_category() == "Server Error"
        print("✓ get_category() works!")

        print("\n✅ Exercise 6 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 6 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 7: Real-World Application (Hard)
# ============================================================================

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task:
    def __init__(self, title: str, priority: Priority, status: TaskStatus = TaskStatus.TODO):
        self.title = title
        self.priority = priority
        self.status = status


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title: str, priority: Priority):
        task = Task(title, priority)
        self.tasks.append(task)

    def get_high_priority_tasks(self) -> list:
        return [task for task in self.tasks if task.priority in (Priority.HIGH, Priority.URGENT)]

    def get_tasks_by_status(self, status: TaskStatus) -> list:
        return [task for task in self.tasks if task.status == status]

    def complete_task(self, title: str):
        for task in self.tasks:
            if task.title == title:
                task.status = TaskStatus.DONE
                break


def test_exercise_7():
    """Test Exercise 7"""
    print("\n" + "="*60)
    print("EXERCISE 7: Real-World Application")
    print("="*60)

    try:
        manager = TaskManager()

        # Add tasks
        manager.add_task("Fix bug in login", Priority.URGENT)
        manager.add_task("Update documentation", Priority.LOW)
        manager.add_task("Implement new feature", Priority.HIGH)
        manager.add_task("Code review", Priority.MEDIUM)

        print(f"✓ Added {len(manager.tasks)} tasks")

        # Get high priority tasks
        high_priority = manager.get_high_priority_tasks()
        print(f"✓ Found {len(high_priority)} high priority tasks")
        assert len(high_priority) == 2  # URGENT and HIGH

        # Get tasks by status
        todo_tasks = manager.get_tasks_by_status(TaskStatus.TODO)
        print(f"✓ Found {len(todo_tasks)} TODO tasks")
        assert len(todo_tasks) == 4

        # Complete a task
        manager.complete_task("Fix bug in login")
        done_tasks = manager.get_tasks_by_status(TaskStatus.DONE)
        print(f"✓ Completed task, {len(done_tasks)} tasks done")
        assert len(done_tasks) == 1

        # Verify task details
        for task in high_priority:
            print(f"  - {task.title} [{task.priority.name}] - {task.status.value}")

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
    print("ENUM EXERCISES - SOLUTIONS")
    print("="*60)
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
        print("\n🎉 All exercises validated successfully!")
        print("✅ Exercises are correct and can be solved!")
        return True
    print(f"\n⚠️  {total - passed} exercises failed validation.")
    return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
