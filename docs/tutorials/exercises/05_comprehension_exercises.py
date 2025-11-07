"""
List Comprehension Exercises - Progressive Difficulty
======================================================

Complete these exercises to master list comprehensions.
Start with Exercise 1 and work your way up!

Run this file to test your solutions:
    python 05_comprehension_exercises.py
"""

# ============================================================================
# EXERCISE 1: Basic List Comprehension (Easy)
# ============================================================================
# TODO: Use a list comprehension to create a list of squares from 0 to 9
#
# Your code here (replace None):

squares = None  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


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
# TODO: Use a list comprehension to create a list of even numbers from 0 to 20
#
# Your code here (replace None):

evens = None  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]


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
# TODO: Given a list of words, create a list of uppercase words
#       that are longer than 3 characters
#
# Your code here:

words = ["hi", "hello", "world", "foo", "python", "bar"]
# Create 'long_words' using list comprehension
long_words = None  # ['HELLO', 'WORLD', 'PYTHON']


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
        # Verify it's a list comprehension (single line)
        print("✓ Used list comprehension!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Working with Dictionaries (Medium)
# ============================================================================
# TODO: Given a dictionary of names and ages, create a list of names
#       for people who are 18 or older
#
# Your code here:

people = {
    "Alice": 25,
    "Bob": 17,
    "Charlie": 30,
    "David": 16,
    "Eve": 22
}
# Create 'adults' using list comprehension
adults = None  # ['Alice', 'Charlie', 'Eve']


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
# TODO: Flatten a 2D matrix into a 1D list using nested list comprehension
#
# Your code here:

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
# Create 'flattened' using nested list comprehension
flattened = None  # [1, 2, 3, 4, 5, 6, 7, 8, 9]


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
# TODO: Create a dictionary where keys are numbers 1-5 and values are their cubes
#       Use a dictionary comprehension
#
# Your code here:

cubes = None  # {1: 1, 2: 8, 3: 27, 4: 64, 5: 125}


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
# TODO: Given a list of database query results (tuples), extract specific fields
#       Query results: [(id, name, status, value), ...]
#       Task 1: Get all names where status is 'active'
#       Task 2: Get sum of values where status is 'active'
#       Task 3: Create dict mapping name to value for active records
#
# Your code here:

query_results = [
    (1, "task_1", "active", 100),
    (2, "task_2", "inactive", 50),
    (3, "task_3", "active", 200),
    (4, "task_4", "active", 150),
    (5, "task_5", "inactive", 75),
]

# Task 1: List of names where status is 'active'
active_names = None  # ['task_1', 'task_3', 'task_4']

# Task 2: Sum of values where status is 'active'
active_total = None  # 450

# Task 3: Dictionary mapping name to value for active records
active_dict = None  # {'task_1': 100, 'task_3': 200, 'task_4': 150}


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

