# Exercises — 05b: Regular Expressions

## Learning Objectives

After completing these exercises, you will be able to:
- Write basic regex patterns with metacharacters
- Use character classes and quantifiers effectively
- Apply the `re` module functions (match, search, findall, sub)
- Capture groups and extract data from text
- Validate common formats (email, phone, URL)
- Use regex flags for case-insensitive matching

---

## Exercise 1: Pattern Matching Basics (Warm-up)

**Bloom Level**: Apply

For each pattern, predict what strings it will match, then test with Python:

```python
import re

patterns = [
    r"cat",           # 1. What does this match?
    r"^cat",          # 2. What does this match?
    r"cat$",          # 3. What does this match?
    r"c.t",           # 4. What does this match?
    r"c.*t",          # 5. What does this match?
    r"c.+t",          # 6. What does this match?
    r"colou?r",       # 7. What does this match?
    r"a{3}",          # 8. What does this match?
]

test_strings = [
    "cat",
    "The cat sat",
    "concat",
    "cat sat on mat",
    "cot",
    "coat",
    "ct",
    "color",
    "colour",
    "aaa",
    "aaaa",
]

# Test each pattern against each string
for pattern in patterns:
    print(f"\nPattern: {pattern}")
    for s in test_strings:
        if re.search(pattern, s):
            print(f"  ✓ '{s}'")
```

Write down your predictions before running the code.

---

## Exercise 2: Character Classes (Practice)

**Bloom Level**: Apply

Write regex patterns to match:

1. Any digit (0-9)
2. Any lowercase letter
3. Any uppercase letter
4. Any alphanumeric character
5. Any whitespace character
6. Any non-digit character
7. Any vowel (case-insensitive)
8. Any hexadecimal digit (0-9, a-f, A-F)

```python
import re

# Write your patterns here
patterns = {
    "digit": r"",              # 1
    "lowercase": r"",          # 2
    "uppercase": r"",          # 3
    "alphanumeric": r"",       # 4
    "whitespace": r"",         # 5
    "non_digit": r"",          # 6
    "vowel": r"",              # 7
    "hex_digit": r"",          # 8
}

# Test strings
test = "Hello World 123 ABC xyz 0xDEAD"

for name, pattern in patterns.items():
    matches = re.findall(pattern, test)
    print(f"{name}: {matches}")
```

---

## Exercise 3: Quantifier Practice (Practice)

**Bloom Level**: Apply

Write patterns to match the following in a text:

```python
text = """
Prices: $5, $50, $500, $5000, $50.99, $500.00
Phone: 555-1234, 555-12-34, 5551234
Codes: A1, AB12, ABC123, ABCD1234
Dates: 2024-01-15, 2024/01/15, 01-15-2024
"""
```

1. Prices with exactly 2 digits after decimal (e.g., $50.99)
2. Phone numbers in format XXX-XXXX
3. Codes starting with 2-4 letters followed by 2-4 digits
4. Dates in YYYY-MM-DD format

```python
import re

# Your patterns here
price_pattern = r""
phone_pattern = r""
code_pattern = r""
date_pattern = r""

# Find all matches
print("Prices with decimals:", re.findall(price_pattern, text))
print("Phone numbers:", re.findall(phone_pattern, text))
print("Codes:", re.findall(code_pattern, text))
print("Dates (YYYY-MM-DD):", re.findall(date_pattern, text))
```

---

## Exercise 4: Capturing Groups (Practice)

**Bloom Level**: Apply

Extract information from log entries:

```python
log_entries = """
2024-01-15 10:23:45 INFO User alice logged in from 192.168.1.100
2024-01-15 10:24:12 ERROR Database connection failed: timeout
2024-01-15 10:25:33 WARNING Memory usage high: 85%
2024-01-15 10:26:01 INFO User bob logged in from 10.0.0.50
2024-01-15 10:27:45 ERROR File not found: /path/to/file.txt
"""
```

Write regex patterns with groups to extract:

1. **Date and time** from each line
2. **Log level** (INFO, ERROR, WARNING)
3. **IP addresses** from login entries
4. **Error messages** (text after "ERROR")

```python
import re

# Pattern with named groups for full log parsing
log_pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.+)"

for match in re.finditer(log_pattern, log_entries):
    print(f"Date: {match.group('date')}, Level: {match.group('level')}")
    print(f"  Message: {match.group('message')}\n")

# Extract just IP addresses
ip_pattern = r""  # Your pattern here
ips = re.findall(ip_pattern, log_entries)
print(f"IP addresses: {ips}")

# Extract error messages
error_pattern = r""  # Your pattern here
errors = re.findall(error_pattern, log_entries)
print(f"Errors: {errors}")
```

---

## Exercise 5: Substitution (Practice)

**Bloom Level**: Apply

Use `re.sub()` to transform text:

```python
import re

# 1. Censor phone numbers (replace digits with X)
text1 = "Call me at 555-123-4567 or 555-987-6543"
# Expected: "Call me at XXX-XXX-XXXX or XXX-XXX-XXXX"

# 2. Convert dates from MM/DD/YYYY to YYYY-MM-DD
text2 = "Meeting on 01/15/2024 and 02/20/2024"
# Expected: "Meeting on 2024-01-15 and 2024-02-20"

# 3. Remove extra whitespace (multiple spaces -> single space)
text3 = "Too    many     spaces   here"
# Expected: "Too many spaces here"

# 4. Convert snake_case to camelCase
text4 = "user_name, first_name, last_login_date"
# Expected: "userName, firstName, lastLoginDate"

# Your solutions:
result1 = re.sub(r"", "", text1)
result2 = re.sub(r"", "", text2)
result3 = re.sub(r"", "", text3)
# For #4, you'll need a function with re.sub

def to_camel_case(text):
    pass

result4 = to_camel_case(text4)

print(f"1. {result1}")
print(f"2. {result2}")
print(f"3. {result3}")
print(f"4. {result4}")
```

---

## Exercise 6: Validation Functions (Analyze)

**Bloom Level**: Analyze

Create validation functions for common formats:

```python
import re

def is_valid_email(email: str) -> bool:
    """
    Validate email address format.

    Valid: user@example.com, user.name@sub.domain.com
    Invalid: @example.com, user@, user@.com
    """
    pass

def is_valid_phone(phone: str) -> bool:
    """
    Validate US phone number formats.

    Valid: 555-123-4567, (555) 123-4567, 555.123.4567, 5551234567
    Invalid: 55-123-4567, 555-12-4567
    """
    pass

def is_valid_url(url: str) -> bool:
    """
    Validate basic URL format.

    Valid: http://example.com, https://sub.domain.com/path
    Invalid: example.com, htp://example.com
    """
    pass

def is_valid_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*()_+-=)

    Returns:
        Tuple of (is_valid, list of missing requirements)
    """
    pass

# Test cases
test_emails = ["user@example.com", "user.name@domain.co.uk", "@invalid.com", "no-at-sign"]
test_phones = ["555-123-4567", "(555) 123-4567", "555.123.4567", "12-34-5678"]
test_urls = ["https://example.com", "http://sub.domain.com/path", "example.com", "ftp://files.com"]
test_passwords = ["weak", "Stronger1!", "NoSpecial1", "no_uppercase_1!"]

for email in test_emails:
    print(f"Email '{email}': {is_valid_email(email)}")

for phone in test_phones:
    print(f"Phone '{phone}': {is_valid_phone(phone)}")

for url in test_urls:
    print(f"URL '{url}': {is_valid_url(url)}")

for pwd in test_passwords:
    valid, missing = is_valid_password(pwd)
    print(f"Password '{pwd}': {valid}, missing: {missing}")
```

---

## Exercise 7: Text Extraction (Analyze)

**Bloom Level**: Analyze

Extract structured data from unstructured text:

```python
html_text = """
<html>
<body>
    <a href="https://example.com">Example Site</a>
    <a href="https://python.org">Python</a>
    <img src="image1.jpg" alt="First image">
    <a href="mailto:contact@example.com">Contact Us</a>
    <img src="photos/image2.png" alt="Second image">
</body>
</html>
"""

# Extract:
# 1. All href URLs (not mailto)
# 2. All image sources (src attributes)
# 3. All link text (text between <a> tags)
# 4. All email addresses from mailto links

def extract_urls(html: str) -> list[str]:
    """Extract all http/https URLs from href attributes."""
    pass

def extract_images(html: str) -> list[str]:
    """Extract all image sources."""
    pass

def extract_link_text(html: str) -> list[str]:
    """Extract text from anchor tags."""
    pass

def extract_emails(html: str) -> list[str]:
    """Extract email addresses from mailto links."""
    pass

print("URLs:", extract_urls(html_text))
print("Images:", extract_images(html_text))
print("Link text:", extract_link_text(html_text))
print("Emails:", extract_emails(html_text))
```

---

## Exercise 8: Log Parser (Challenge)

**Bloom Level**: Create

Build a comprehensive log parser:

```python
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    logger: str
    message: str
    ip_address: Optional[str] = None
    user: Optional[str] = None
    error_code: Optional[int] = None

def parse_log_line(line: str) -> Optional[LogEntry]:
    """
    Parse a log line into a LogEntry.

    Log format:
    2024-01-15 10:23:45.123 [INFO] app.auth - User 'alice' logged in from 192.168.1.1
    2024-01-15 10:24:12.456 [ERROR] app.db - Connection failed (code: 5001)
    2024-01-15 10:25:33.789 [WARNING] app.memory - High usage: 85%
    """
    pass

def analyze_logs(logs: list[LogEntry]) -> dict:
    """
    Analyze logs and return statistics.

    Returns dict with:
    - total_entries: total number of entries
    - by_level: count per log level
    - unique_ips: set of unique IP addresses
    - unique_users: set of unique usernames
    - error_codes: list of error codes found
    """
    pass

# Test data
log_text = """
2024-01-15 10:23:45.123 [INFO] app.auth - User 'alice' logged in from 192.168.1.1
2024-01-15 10:24:12.456 [ERROR] app.db - Connection failed (code: 5001)
2024-01-15 10:25:33.789 [WARNING] app.memory - High usage: 85%
2024-01-15 10:26:01.234 [INFO] app.auth - User 'bob' logged in from 10.0.0.50
2024-01-15 10:27:45.567 [ERROR] app.file - File not found (code: 4004)
2024-01-15 10:28:00.890 [INFO] app.auth - User 'alice' logged out
"""

# Parse each line
entries = []
for line in log_text.strip().split("\n"):
    entry = parse_log_line(line)
    if entry:
        entries.append(entry)
        print(f"Parsed: {entry.level} - {entry.message[:50]}...")

# Analyze
stats = analyze_logs(entries)
print("\nAnalysis:")
print(f"Total entries: {stats['total_entries']}")
print(f"By level: {stats['by_level']}")
print(f"Unique IPs: {stats['unique_ips']}")
print(f"Unique users: {stats['unique_users']}")
print(f"Error codes: {stats['error_codes']}")
```

---

## Exercise 9: Search and Replace Tool (Challenge)

**Bloom Level**: Create

Build a flexible search and replace utility:

```python
import re
from typing import Callable

class TextProcessor:
    """Text processing with regex support."""

    def __init__(self, text: str):
        self.text = text
        self.history = [text]

    def find_all(self, pattern: str, flags: int = 0) -> list[str]:
        """Find all matches for pattern."""
        pass

    def replace(
        self,
        pattern: str,
        replacement: str | Callable,
        flags: int = 0
    ) -> "TextProcessor":
        """Replace matches with string or function result."""
        pass

    def highlight(self, pattern: str, before: str = ">>", after: str = "<<") -> str:
        """Return text with matches highlighted."""
        pass

    def extract_between(self, start: str, end: str) -> list[str]:
        """Extract text between start and end patterns."""
        pass

    def undo(self) -> "TextProcessor":
        """Undo last replacement."""
        pass

    def __str__(self) -> str:
        return self.text

# Test
text = """
The quick brown fox jumps over the lazy dog.
Email: contact@example.com
Phone: (555) 123-4567
Price: $99.99
Date: 2024-01-15
"""

processor = TextProcessor(text)

# Find all words starting with capital letters
capitals = processor.find_all(r"\b[A-Z][a-z]+\b")
print(f"Capitalized words: {capitals}")

# Replace email with [REDACTED]
processor.replace(r"[\w.]+@[\w.]+", "[EMAIL REDACTED]")
print(f"\nAfter redacting email:\n{processor}")

# Highlight phone numbers
highlighted = processor.highlight(r"\(\d{3}\) \d{3}-\d{4}")
print(f"\nWith phone highlighted:\n{highlighted}")

# Extract text between patterns
processor2 = TextProcessor("Name: John, Age: 25, City: Boston")
values = processor2.extract_between(r": ", r"(,|$)")
print(f"\nExtracted values: {values}")
```

---

## Deliverables

Submit your code for all exercises. Ensure all validation functions have comprehensive test cases.

---

[← Back to Chapter](../05b_regex.md) | [View Solutions](../solutions/sol_05b_regex.md) | [← Back to Module 1](../README.md)
