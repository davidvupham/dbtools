"""
enumerate() Function Exercises - SOLUTIONS
===========================================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 06_enumerate_exercises_SOLUTIONS.py
"""

# ============================================================================
# EXERCISE 1: Basic enumerate() Usage (Easy)
# ============================================================================

fruits = ["apple", "banana", "cherry", "date"]


def format_fruits(fruit_list):
    return [f"{i}: {fruit}" for i, fruit in enumerate(fruit_list)]


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "=" * 60)
    print("EXERCISE 1: Basic enumerate() Usage")
    print("=" * 60)

    try:
        result = format_fruits(fruits)
        print(f"✓ Input: {fruits}")
        print("✓ Output:")
        for item in result:
            print(f"  {item}")
        expected = ["0: apple", "1: banana", "2: cherry", "3: date"]
        assert result == expected
        print("✓ Enumeration is correct!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Custom Start Index (Easy)
# ============================================================================


def create_numbered_list(items):
    """Create a numbered list starting from 1"""
    return [f"{i}. {item}" for i, item in enumerate(items, start=1)]


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "=" * 60)
    print("EXERCISE 2: Custom Start Index")
    print("=" * 60)

    try:
        tasks = ["Write code", "Test code", "Deploy code"]
        result = create_numbered_list(tasks)
        print("✓ Tasks:")
        for item in result:
            print(f"  {item}")
        expected = ["1. Write code", "2. Test code", "3. Deploy code"]
        assert result == expected
        print("✓ Numbering starts from 1!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Find Item Index (Easy-Medium)
# ============================================================================


def find_index(items, target):
    """Find the index of target in items, return -1 if not found"""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "=" * 60)
    print("EXERCISE 3: Find Item Index")
    print("=" * 60)

    try:
        colors = ["red", "green", "blue", "yellow"]
        idx = find_index(colors, "blue")
        print(f"✓ Colors: {colors}")
        print(f"✓ Index of 'blue': {idx}")
        assert idx == 2
        print("✓ Found correct index!")

        idx = find_index(colors, "purple")
        print(f"✓ Index of 'purple': {idx}")
        assert idx == -1
        print("✓ Returns -1 for missing item!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Modify List Elements (Medium)
# ============================================================================


def uppercase_even_indices(words):
    """Return new list with even-indexed words in uppercase"""
    return [word.upper() if i % 2 == 0 else word for i, word in enumerate(words)]


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "=" * 60)
    print("EXERCISE 4: Modify List Elements")
    print("=" * 60)

    try:
        words = ["hello", "world", "python", "code", "test"]
        result = uppercase_even_indices(words)
        print(f"✓ Input: {words}")
        print(f"✓ Output: {result}")
        expected = ["HELLO", "world", "PYTHON", "code", "TEST"]
        assert result == expected
        print("✓ Even indices are uppercase!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Compare Two Lists (Medium)
# ============================================================================


def find_differences(list1, list2):
    """Return list of indices where list1 and list2 differ"""
    return [i for i, (a, b) in enumerate(zip(list1, list2)) if a != b]


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "=" * 60)
    print("EXERCISE 5: Compare Two Lists")
    print("=" * 60)

    try:
        list1 = [1, 2, 3, 4, 5]
        list2 = [1, 2, 9, 4, 7]
        diffs = find_differences(list1, list2)
        print(f"✓ List 1: {list1}")
        print(f"✓ List 2: {list2}")
        print(f"✓ Differences at indices: {diffs}")
        assert diffs == [2, 4]
        print("✓ Found all differences!")

        # Test identical lists
        list3 = [1, 2, 3]
        list4 = [1, 2, 3]
        diffs2 = find_differences(list3, list4)
        assert diffs2 == []
        print("✓ Returns empty list for identical lists!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Real-World Example - Log Processing (Medium-Hard)
# ============================================================================


def find_errors_in_log(log_lines):
    """
    Find ERROR lines in log and return list of tuples: (line_number, message)
    Line numbers should start from 1
    """
    return [(i, line) for i, line in enumerate(log_lines, start=1) if "ERROR" in line]


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "=" * 60)
    print("EXERCISE 6: Real-World Example - Log Processing")
    print("=" * 60)

    try:
        log = [
            "INFO: Application started",
            "DEBUG: Loading configuration",
            "ERROR: Database connection failed",
            "INFO: Retrying connection",
            "ERROR: Max retries exceeded",
            "INFO: Shutting down",
        ]

        errors = find_errors_in_log(log)
        print(f"✓ Log has {len(log)} lines")
        print("✓ Found errors:")
        for line_num, message in errors:
            print(f"  Line {line_num}: {message}")

        expected = [
            (3, "ERROR: Database connection failed"),
            (5, "ERROR: Max retries exceeded"),
        ]
        assert errors == expected
        print("✓ Extracted errors with correct line numbers!")

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
    print("\n" + "=" * 60)
    print("ENUMERATE() EXERCISES - TEST RUNNER")
    print("=" * 60)

    results = [
        test_exercise_1(),
        test_exercise_2(),
        test_exercise_3(),
        test_exercise_4(),
        test_exercise_5(),
        test_exercise_6(),
    ]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 Congratulations! All exercises passed!")
        print("You now master:")
        print("  • Basic enumerate() usage")
        print("  • Custom start indices")
        print("  • Finding indices")
        print("  • List comparisons")
        print("  • Real-world log processing")
        print("\n💡 Remember: Never use range(len(items)) - use enumerate()!")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()
