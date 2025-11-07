"""
F-String Exercises - SOLUTIONS
===============================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 08_fstrings_exercises_SOLUTIONS.py
"""

# ============================================================================
# EXERCISE 1: Basic F-String Usage (Easy)
# ============================================================================

name = "Alice"
age = 30
greeting = f"Hello, {name}! You are {age} years old."


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Basic F-String Usage")
    print("="*60)

    try:
        assert greeting is not None
        print(f"✓ Created greeting: {greeting}")
        assert greeting == "Hello, Alice! You are 30 years old."
        print("✓ F-string formatted correctly!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Expressions in F-Strings (Easy)
# ============================================================================

width = 10
height = 5
message = f"Area: {width * height} square units"


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Expressions in F-Strings")
    print("="*60)

    try:
        assert message is not None
        print(f"✓ Width: {width}, Height: {height}")
        print(f"✓ Message: {message}")
        assert message == "Area: 50 square units"
        print("✓ Expression evaluated correctly!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Number Formatting (Easy-Medium)
# ============================================================================

pi = 3.14159265359
formatted_pi = f"Pi: {pi:.2f}"

large_num = 1234567
formatted_num = f"{large_num:,}"


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Number Formatting")
    print("="*60)

    try:
        assert formatted_pi is not None
        print(f"✓ Original pi: {pi}")
        print(f"✓ Formatted: {formatted_pi}")
        assert formatted_pi == "Pi: 3.14"
        print("✓ Decimal precision correct!")

        assert formatted_num is not None
        print(f"✓ Original number: {large_num}")
        print(f"✓ Formatted: {formatted_num}")
        assert formatted_num == "1,234,567"
        print("✓ Thousand separators correct!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: String Alignment and Padding (Medium)
# ============================================================================

def format_table_row(name, value):
    """
    Format a table row with:
    - name left-aligned in 15 characters
    - value right-aligned in 10 characters
    """
    return f"{name:<15}{value:>10}"


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: String Alignment and Padding")
    print("="*60)

    try:
        row1 = format_table_row("Product", "$99.99")
        row2 = format_table_row("Tax", "$8.50")
        print("✓ Formatted table:")
        print(f"  {row1}")
        print(f"  {row2}")

        assert len(row1) == 25  # 15 + 10
        assert len(row2) == 25
        assert row1 == "Product        $    99.99"
        assert row2 == "Tax            $      8.50"
        print("✓ Alignment and padding correct!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: Debugging with F-Strings (Medium)
# ============================================================================

def debug_variables(x, y, z):
    """
    Return a string showing variable names and values
    Use f"{x=}, {y=}, {z=}" syntax
    """
    return f"{x=}, {y=}, {z=}"


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: Debugging with F-Strings")
    print("="*60)

    try:
        result = debug_variables(10, 20, 30)
        print(f"✓ Debug output: {result}")
        assert "x=10" in result
        assert "y=20" in result
        assert "z=30" in result
        print("✓ Debug syntax works!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Real-World Example - Report Generation (Medium-Hard)
# ============================================================================

def generate_report(name, transactions, balance):
    """
    Generate a bank statement report
    """
    status = "Positive" if balance >= 0 else "Negative"
    separator = "=" * 50

    report = f"""{separator}
{"Account: " + name:^50}
{separator}
Transactions: {transactions}
Balance: ${balance:,.2f}
Status: {status}
{separator}"""

    return report


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Real-World Example - Report Generation")
    print("="*60)

    try:
        report = generate_report("Alice", 5, 1234.56)
        print("✓ Generated report:")
        print(report)

        # Verify report contains required elements
        assert "Alice" in report
        assert "5" in report
        assert "1,234.56" in report
        assert "Positive" in report
        print("✓ Report contains all required information!")

        # Test negative balance
        report2 = generate_report("Bob", 3, -500.25)
        assert "Negative" in report2
        assert "-500.25" in report2
        print("✓ Handles negative balance correctly!")

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
    print("F-STRING EXERCISES - TEST RUNNER")
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
        print("  • Basic f-string syntax")
        print("  • Expressions in f-strings")
        print("  • Number formatting")
        print("  • String alignment and padding")
        print("  • Debug syntax (f'{var=}')")
        print("  • Real-world report generation")
        print("\n💡 F-strings are the modern way to format strings in Python!")
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

