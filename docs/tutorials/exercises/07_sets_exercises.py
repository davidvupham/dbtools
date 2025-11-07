"""
Sets Exercises - Progressive Difficulty
========================================

Complete these exercises to master Python sets.
Start with Exercise 1 and work your way up!

Run this file to test your solutions:
    python 07_sets_exercises.py
"""

# ============================================================================
# EXERCISE 1: Create and Manipulate Sets (Easy)
# ============================================================================
# TODO: Create a set of unique numbers from a list
#
# Your code here:

numbers = [1, 2, 2, 3, 4, 4, 4, 5, 5]
# Create 'unique_numbers' set
unique_numbers = None


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Create and Manipulate Sets")
    print("="*60)

    try:
        assert unique_numbers is not None
        print(f"✓ Input list: {numbers}")
        print(f"✓ Unique set: {sorted(unique_numbers)}")
        assert unique_numbers == {1, 2, 3, 4, 5}
        print("✓ Duplicates removed!")
        assert isinstance(unique_numbers, set)
        print("✓ Created a set!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Set Operations - Union (Easy)
# ============================================================================
# TODO: Find all unique items from two sets using union
#
# Your code here:

set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
# Create 'all_items' using union
all_items = None


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Set Operations - Union")
    print("="*60)

    try:
        assert all_items is not None
        print(f"✓ Set A: {sorted(set_a)}")
        print(f"✓ Set B: {sorted(set_b)}")
        print(f"✓ Union: {sorted(all_items)}")
        assert all_items == {1, 2, 3, 4, 5, 6}
        print("✓ Union is correct!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Set Operations - Intersection (Easy-Medium)
# ============================================================================
# TODO: Find common items between two sets using intersection
#
# Your code here:

users_a = {"Alice", "Bob", "Charlie", "David"}
users_b = {"Charlie", "David", "Eve", "Frank"}
# Create 'common_users' using intersection
common_users = None


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Set Operations - Intersection")
    print("="*60)

    try:
        assert common_users is not None
        print(f"✓ Users A: {sorted(users_a)}")
        print(f"✓ Users B: {sorted(users_b)}")
        print(f"✓ Common users: {sorted(common_users)}")
        assert common_users == {"Charlie", "David"}
        print("✓ Intersection is correct!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Set Operations - Difference (Medium)
# ============================================================================
# TODO: Find items that are in set A but not in set B
#
# Your code here:

completed_tasks = {"task1", "task2", "task3", "task4", "task5"}
pending_tasks = {"task3", "task4", "task6", "task7"}
# Find tasks that are completed but not pending
# Create 'truly_completed' using difference
truly_completed = None


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Set Operations - Difference")
    print("="*60)

    try:
        assert truly_completed is not None
        print(f"✓ Completed: {sorted(completed_tasks)}")
        print(f"✓ Pending: {sorted(pending_tasks)}")
        print(f"✓ Truly completed: {sorted(truly_completed)}")
        assert truly_completed == {"task1", "task2", "task5"}
        print("✓ Difference is correct!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Fast Membership Testing (Medium)
# ============================================================================
# TODO: Write a function that checks if a user is in a large dataset
#       Use sets for O(1) lookup instead of lists O(n)
#
# Your code here:

def is_user_active(username, active_users_set):
    """Check if username is in active_users_set (should be O(1))"""
    # Your code here
    pass


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Fast Membership Testing")
    print("="*60)

    try:
        # Create large set for performance
        active_users = set(f"user{i}" for i in range(10000))

        # Test existing user
        assert is_user_active("user5000", active_users) == True
        print("✓ Found existing user!")

        # Test non-existing user
        assert is_user_active("user99999", active_users) == False
        print("✓ Correctly identified non-existing user!")

        # Verify it's fast (should be instant even for large sets)
        import time
        start = time.time()
        for _ in range(1000):
            is_user_active("user5000", active_users)
        elapsed = time.time() - start
        print(f"✓ 1000 lookups took {elapsed:.4f} seconds (should be < 0.01s)")
        assert elapsed < 0.1  # Should be nearly instant

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Real-World Example - Data Analysis (Medium-Hard)
# ============================================================================
# TODO: Analyze database query results using sets
#       Given lists of user IDs from different sources, find:
#       1. Users active on both days
#       2. Users active only on day 1
#       3. Users active only on day 2
#       4. Total unique users across both days
#
# Your code here:

def analyze_user_activity(day1_users, day2_users):
    """
    Analyze user activity across two days.
    Returns tuple: (both_days, only_day1, only_day2, total_unique)
    """
    # Convert lists to sets
    # Use set operations to find:
    # - both_days: intersection
    # - only_day1: difference (day1 - day2)
    # - only_day2: difference (day2 - day1)
    # - total_unique: union
    # Your code here
    pass


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Real-World Example - Data Analysis")
    print("="*60)

    try:
        day1 = [101, 102, 103, 104, 105, 103, 101]  # Has duplicates
        day2 = [103, 104, 106, 107, 108, 106]       # Has duplicates

        both, only1, only2, total = analyze_user_activity(day1, day2)

        print(f"✓ Day 1 users (with duplicates): {day1}")
        print(f"✓ Day 2 users (with duplicates): {day2}")
        print(f"✓ Active both days: {sorted(both)}")
        print(f"✓ Active only day 1: {sorted(only1)}")
        print(f"✓ Active only day 2: {sorted(only2)}")
        print(f"✓ Total unique users: {sorted(total)}")

        assert both == {103, 104}
        assert only1 == {101, 102, 105}
        assert only2 == {106, 107, 108}
        assert total == {101, 102, 103, 104, 105, 106, 107, 108}
        print("✓ Analysis is correct!")

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
    print("SETS EXERCISES - TEST RUNNER")
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
        print("You now master:")
        print("  • Creating and manipulating sets")
        print("  • Set operations (union, intersection, difference)")
        print("  • Fast membership testing (O(1))")
        print("  • Removing duplicates")
        print("  • Real-world data analysis")
        print("\n💡 Use sets when you need unique items or fast lookups!")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

