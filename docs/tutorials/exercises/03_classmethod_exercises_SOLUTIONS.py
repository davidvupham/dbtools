"""
@classmethod Exercises - SOLUTIONS
===================================

This file contains complete solutions to validate the exercises work correctly.
DO NOT share this with students - let them learn by solving!

Run this file to verify all exercises pass:
    python 03_classmethod_exercises_SOLUTIONS.py
"""

from datetime import datetime
from typing import Optional
import os

# ============================================================================
# EXERCISE 1: Create an Alternative Constructor (Easy)
# ============================================================================

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @classmethod
    def from_birth_year(cls, name: str, birth_year: int):
        age = datetime.now().year - birth_year
        return cls(name, age)


def test_exercise_1():
    """Test Exercise 1"""
    print("\n" + "="*60)
    print("EXERCISE 1: Create an Alternative Constructor")
    print("="*60)

    try:
        # Test regular constructor
        person1 = Person("Alice", 30)
        print(f"✓ Created person: {person1.name}, age {person1.age}")

        # Test classmethod constructor
        person2 = Person.from_birth_year("Bob", 1990)
        print(f"✓ Created from birth year: {person2.name}, age {person2.age}")
        assert person2.age == datetime.now().year - 1990
        print("✓ Age calculation is correct!")

        print("\n✅ Exercise 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 1 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 2: Parse from String (Easy-Medium)
# ============================================================================

class Product:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    @classmethod
    def from_string(cls, product_string: str):
        name, price, stock = product_string.split(',')
        return cls(name, float(price), int(stock))


def test_exercise_2():
    """Test Exercise 2"""
    print("\n" + "="*60)
    print("EXERCISE 2: Parse from String")
    print("="*60)

    try:
        # Test regular constructor
        p1 = Product("Mouse", 29.99, 100)
        print(f"✓ Created product: {p1.name}, ${p1.price}, stock={p1.stock}")

        # Test from_string
        p2 = Product.from_string("Laptop,999.99,5")
        print(f"✓ Parsed from string: {p2.name}, ${p2.price}, stock={p2.stock}")
        assert p2.name == "Laptop"
        assert p2.price == 999.99
        assert p2.stock == 5
        print("✓ Parsing is correct!")

        print("\n✅ Exercise 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 2 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 3: Factory Method with Validation (Medium)
# ============================================================================

class BankAccount:
    def __init__(self, account_number: str, balance: float):
        if len(account_number) != 8 or not account_number.isdigit():
            raise ValueError("Account number must be exactly 8 digits")
        self.account_number = account_number
        self.balance = balance

    @classmethod
    def create_savings(cls, account_number: str):
        return cls(account_number, 0.0)

    @classmethod
    def create_checking(cls, account_number: str):
        return cls(account_number, 100.0)


def test_exercise_3():
    """Test Exercise 3"""
    print("\n" + "="*60)
    print("EXERCISE 3: Factory Method with Validation")
    print("="*60)

    try:
        # Test create_savings
        savings = BankAccount.create_savings("12345678")
        print(f"✓ Created savings: {savings.account_number}, balance=${savings.balance}")
        assert savings.balance == 0.0
        print("✓ Savings starts with $0")

        # Test create_checking
        checking = BankAccount.create_checking("87654321")
        print(f"✓ Created checking: {checking.account_number}, balance=${checking.balance}")
        assert checking.balance == 100.0
        print("✓ Checking starts with $100")

        # Test validation
        try:
            invalid = BankAccount.create_savings("123")  # Too short
            print("❌ Should have raised ValueError for invalid account number")
            return False
        except ValueError:
            print("✓ Validation works correctly!")

        print("\n✅ Exercise 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 3 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 4: Understanding cls vs self (Medium)
# ============================================================================

class Counter:
    total_instances = 0

    def __init__(self):
        Counter.total_instances += 1
        self.count = 0

    def increment(self):
        self.count += 1

    @classmethod
    def get_total_instances(cls):
        return cls.total_instances

    @classmethod
    def reset_all(cls):
        cls.total_instances = 0


def test_exercise_4():
    """Test Exercise 4"""
    print("\n" + "="*60)
    print("EXERCISE 4: Understanding cls vs self")
    print("="*60)

    try:
        # Reset before testing
        Counter.reset_all()

        # Create instances
        c1 = Counter()
        c2 = Counter()
        c3 = Counter()
        print(f"✓ Created 3 counters")
        assert Counter.get_total_instances() == 3
        print(f"✓ Total instances: {Counter.get_total_instances()}")

        # Test instance methods
        c1.increment()
        c1.increment()
        c2.increment()
        print(f"✓ c1 count: {c1.count}, c2 count: {c2.count}, c3 count: {c3.count}")
        assert c1.count == 2
        assert c2.count == 1
        assert c3.count == 0
        print("✓ Instance counts are independent!")

        # Test class method
        Counter.reset_all()
        assert Counter.get_total_instances() == 0
        print("✓ Class method can reset class attribute!")

        print("\n✅ Exercise 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 4 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 5: @classmethod with Inheritance (Medium-Hard)
# ============================================================================

class Animal:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species

    @classmethod
    def create(cls, name: str):
        species = cls.__name__
        return cls(name, species)


class Dog(Animal):
    def __init__(self, name: str, species: str, breed: str = "Mixed"):
        super().__init__(name, species)
        self.breed = breed

    @classmethod
    def create(cls, name: str, breed: str):
        species = cls.__name__
        return cls(name, species, breed)


def test_exercise_5():
    """Test Exercise 5"""
    print("\n" + "="*60)
    print("EXERCISE 5: @classmethod with Inheritance")
    print("="*60)

    try:
        # Test Animal.create
        animal = Animal.create("Generic")
        print(f"✓ Created animal: {animal.name}, species={animal.species}")
        assert animal.species == "Animal"
        print("✓ Animal species is correct!")

        # Test Dog.create
        dog = Dog.create("Buddy", "Golden Retriever")
        print(f"✓ Created dog: {dog.name}, species={dog.species}, breed={dog.breed}")
        assert dog.species == "Dog"
        assert dog.breed == "Golden Retriever"
        print("✓ Dog species and breed are correct!")
        print("✓ @classmethod works with inheritance!")

        print("\n✅ Exercise 5 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Exercise 5 FAILED: {e}")
        return False


# ============================================================================
# EXERCISE 6: Real-World Example - Configuration Loader (Hard)
# ============================================================================

class DatabaseConfig:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @classmethod
    def from_env(cls):
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        username = os.getenv("DB_USER", "dev_user")
        password = os.getenv("DB_PASS", "dev_pass")
        return cls(host, port, username, password)

    @classmethod
    def from_dict(cls, config: dict):
        return cls(
            config["host"],
            config["port"],
            config["username"],
            config["password"]
        )

    @classmethod
    def development(cls):
        return cls("localhost", 5432, "dev_user", "dev_pass")

    @classmethod
    def production(cls):
        return cls("prod.db.company.com", 5432, "prod_user", "secure_pass")

    def connection_string(self):
        return f"postgresql://{self.username}@{self.host}:{self.port}"


def test_exercise_6():
    """Test Exercise 6"""
    print("\n" + "="*60)
    print("EXERCISE 6: Real-World Example - Configuration Loader")
    print("="*60)

    try:
        # Test development config
        dev = DatabaseConfig.development()
        print(f"✓ Development config: {dev.host}:{dev.port}")
        assert dev.host == "localhost"
        print("✓ Development uses localhost!")

        # Test production config
        prod = DatabaseConfig.production()
        print(f"✓ Production config: {prod.host}:{prod.port}")
        assert prod.host != "localhost"
        print("✓ Production uses different host!")

        # Test from_dict
        config_dict = {
            "host": "test.db.com",
            "port": 3306,
            "username": "test_user",
            "password": "test_pass"
        }
        test_config = DatabaseConfig.from_dict(config_dict)
        print(f"✓ Created from dict: {test_config.host}:{test_config.port}")
        assert test_config.host == "test.db.com"
        print("✓ from_dict works correctly!")

        # Test connection string
        conn_str = test_config.connection_string()
        print(f"✓ Connection string: {conn_str}")
        assert "test_user" in conn_str
        assert "test.db.com" in conn_str
        print("✓ Connection string is formatted correctly!")

        # Test from_env (with fallbacks)
        env_config = DatabaseConfig.from_env()
        print(f"✓ Created from env: {env_config.host}:{env_config.port}")
        print("✓ from_env works with defaults!")

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
    print("CLASSMETHOD EXERCISES - TEST RUNNER")
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
    else:
        print(f"\n📚 Keep practicing! {total - passed} exercise(s) need work.")


if __name__ == "__main__":
    run_all_tests()

