"""
List Comprehension Exercises - SOLUTIONS
=========================================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 05_comprehension_exercises_SOLUTIONS.py
"""

# ============================================================================
# EXERCISE 1: Basic List Comprehension (Easy)
# ============================================================================

squares = [x**2 for x in range(10)]


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Basic List Comprehension")
    print("="*60)

    try:
        assert squares is not None
        print(f"✓ Created list: {squares}")
        assert squares == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        print("✓ List of squares is correct!")
        assert isinstance(squares, list)
        print("✓ Used list comprehension!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Comprehension with Condition (Easy)
# ============================================================================

evens = [x for x in range(21) if x % 2 == 0]


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Comprehension with Condition")
    print("="*60)

    try:
        assert evens is not None
        print(f"✓ Created list: {evens}")
        assert evens == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        print("✓ List of evens is correct!")
        assert len(evens) == 11
        print("✓ Used conditional in comprehension!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Transform and Filter (Easy-Medium)
# ============================================================================

words = ["hi", "hello", "world", "foo", "python", "bar"]
long_words = [word.upper() for word in words if len(word) > 3]


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Transform and Filter")
    print("="*60)

    try:
        assert long_words is not None
        print(f"✓ Input: {words}")
        print(f"✓ Output: {long_words}")
        assert long_words == ['HELLO', 'WORLD', 'PYTHON']
        print("✓ Filtered and transformed correctly!")
        print("✓ Used list comprehension!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Working with Dictionaries (Medium)
# ============================================================================

people = {
    "Alice": 25,
    "Bob": 17,
    "Charlie": 30,
    "David": 16,
    "Eve": 22
}
adults = [name for name, age in people.items() if age >= 18]


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Working with Dictionaries")
    print("="*60)

    try:
        assert adults is not None
        print(f"✓ Input: {people}")
        print(f"✓ Adults: {adults}")
        assert set(adults) == {'Alice', 'Charlie', 'Eve'}
        print("✓ Filtered adults correctly!")
        assert len(adults) == 3
        print("✓ Correct number of adults!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Nested List Comprehension (Medium-Hard)
# ============================================================================

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
flattened = [num for row in matrix for num in row]


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Nested List Comprehension")
    print("="*60)

    try:
        assert flattened is not None
        print(f"✓ Input matrix:")
        for row in matrix:
            print(f"  {row}")
        print(f"✓ Flattened: {flattened}")
        assert flattened == [1, 2, 3, 4, 5, 6, 7, 8, 9]
        print("✓ Matrix flattened correctly!")
        assert len(flattened) == 9
        print("✓ All elements present!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Dictionary Comprehension (Medium)
# ============================================================================

cubes = {x: x**3 for x in range(1, 6)}


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Dictionary Comprehension")
    print("="*60)

    try:
        assert cubes is not None
        print(f"✓ Created dictionary: {cubes}")
        assert cubes == {1: 1, 2: 8, 3: 27, 4: 64, 5: 125}
        print("✓ Dictionary of cubes is correct!")
        assert isinstance(cubes, dict)
        print("✓ Used dictionary comprehension!")

        print("\n✅ Exercise 6 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 6 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 7: Real-World Example - Data Processing (Hard)
# ============================================================================

query_results = [
    (1, "task_1", "active", 100),
    (2, "task_2", "inactive", 50),
    (3, "task_3", "active", 200),
    (4, "task_4", "active", 150),
    (5, "task_5", "inactive", 75),
]

# Task 1: List of names where status is 'active'
active_names = [name for id, name, status, value in query_results if status == 'active']

# Task 2: Sum of values where status is 'active'
active_total = sum(value for id, name, status, value in query_results if status == 'active')

# Task 3: Dictionary mapping name to value for active records
active_dict = {name: value for id, name, status, value in query_results if status == 'active'}


def test_exercise_7():
    """Test Exercise 7"""
    print("\n" + "="*60)
    print("EXERCISE 7: Real-World Example - Data Processing")
    print("="*60)

    try:
        # Test Task 1
        assert active_names is not None
        print(f"✓ Active names: {active_names}")
        assert active_names == ['task_1', 'task_3', 'task_4']
        print("✓ Task 1 correct!")

        # Test Task 2
        assert active_total is not None
        print(f"✓ Active total: {active_total}")
        assert active_total == 450
        print("✓ Task 2 correct!")

        # Test Task 3
        assert active_dict is not None
        print(f"✓ Active dict: {active_dict}")
        assert active_dict == {'task_1': 100, 'task_3': 200, 'task_4': 150}
        print("✓ Task 3 correct!")

        print("\n✅ Exercise 7 PASSED!")
        print("You can now process data efficiently with comprehensions!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 7 FAILED: {e}")
        return False


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all exercise tests"""
    print("\n" + "="*60)
    print("LIST COMPREHENSION EXERCISES - TEST RUNNER")
    print("="*60)

    results = [
        test_exercise_1(),
        test_exercise_2(),
        test_exercise_3(),
        test_exercise_4(),
        test_exercise_5(),
        test_exercise_6(),
        test_exercise_7(),
    ]

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 Congratulations! All exercises passed!")
        print("You now master:")
        print("  • Basic list comprehensions")
        print("  • Conditional filtering")
        print("  • Nested comprehensions")
        print("  • Dictionary comprehensions")
        print("  • Real-world data processing")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

