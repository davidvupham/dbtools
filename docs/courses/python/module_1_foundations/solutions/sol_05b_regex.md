# Solutions — 05b: Regular Expressions

## Key Concepts Demonstrated

- Pattern matching with metacharacters (`.`, `^`, `$`, `*`, `+`, `?`)
- Character classes (`\d`, `\w`, `\s`, `[...]`)
- Quantifiers (`{n}`, `{n,m}`, `*`, `+`, `?`)
- Groups and capturing (`()`, `(?P<name>...)`)
- The `re` module functions (match, search, findall, sub, finditer)
- Validation patterns for common formats
- Substitution with functions

## Common Mistakes to Avoid

- Forgetting to use raw strings (`r"pattern"`) for backslashes
- Using `match()` when you need `search()` (match only at start)
- Greedy vs non-greedy: `.*` vs `.*?`
- Not escaping metacharacters when matching literally (`\.` for a period)
- Over-complicated patterns when simple string methods work

---

## Exercise 1 Solution

```python
import re

# Pattern explanations:
# 1. r"cat"     - Matches "cat" anywhere in the string
# 2. r"^cat"    - Matches "cat" only at the start of string
# 3. r"cat$"    - Matches "cat" only at the end of string
# 4. r"c.t"     - Matches c + any single char + t (cat, cot, c9t, etc.)
# 5. r"c.*t"    - Matches c + any chars (0 or more) + t (ct, cat, coast, etc.)
# 6. r"c.+t"    - Matches c + any chars (1 or more) + t (cat, coast, but NOT ct)
# 7. r"colou?r" - Matches "color" or "colour" (u is optional)
# 8. r"a{3}"    - Matches exactly 3 consecutive 'a' characters

patterns = [
    (r"cat", "Matches 'cat' anywhere"),
    (r"^cat", "Matches 'cat' at start only"),
    (r"cat$", "Matches 'cat' at end only"),
    (r"c.t", "Matches c + any char + t"),
    (r"c.*t", "Matches c + zero or more chars + t"),
    (r"c.+t", "Matches c + one or more chars + t"),
    (r"colou?r", "Matches color or colour"),
    (r"a{3}", "Matches exactly 3 a's"),
]

test_strings = [
    "cat", "The cat sat", "concat", "cat sat on mat", "cot",
    "coat", "ct", "color", "colour", "aaa", "aaaa"
]

for pattern, description in patterns:
    print(f"\n{pattern}: {description}")
    matches = [s for s in test_strings if re.search(pattern, s)]
    print(f"  Matches: {matches}")
```

**Output**:
```
cat: Matches 'cat' anywhere
  Matches: ['cat', 'The cat sat', 'concat', 'cat sat on mat']

^cat: Matches 'cat' at start only
  Matches: ['cat', 'cat sat on mat']

cat$: Matches 'cat' at end only
  Matches: ['cat', 'concat']

c.t: Matches c + any char + t
  Matches: ['cat', 'The cat sat', 'concat', 'cat sat on mat', 'cot']

c.*t: Matches c + zero or more chars + t
  Matches: ['cat', 'The cat sat', 'concat', 'cat sat on mat', 'cot', 'coat', 'ct']

c.+t: Matches c + one or more chars + t
  Matches: ['cat', 'The cat sat', 'concat', 'cat sat on mat', 'cot', 'coat']

colou?r: Matches color or colour
  Matches: ['color', 'colour']

a{3}: Matches exactly 3 a's
  Matches: ['aaa', 'aaaa']
```

---

## Exercise 2 Solution

```python
import re

patterns = {
    "digit": r"\d",                    # Any digit
    "lowercase": r"[a-z]",             # Lowercase letter
    "uppercase": r"[A-Z]",             # Uppercase letter
    "alphanumeric": r"\w",             # Letter, digit, or underscore
    "whitespace": r"\s",               # Space, tab, newline
    "non_digit": r"\D",                # Any non-digit
    "vowel": r"[aeiouAEIOU]",          # Any vowel (case-insensitive)
    "hex_digit": r"[0-9a-fA-F]",       # Hex digit
}

test = "Hello World 123 ABC xyz 0xDEAD"

for name, pattern in patterns.items():
    matches = re.findall(pattern, test)
    print(f"{name}: {matches}")
```

**Output**:
```
digit: ['1', '2', '3', '0', '0']
lowercase: ['e', 'l', 'l', 'o', 'o', 'r', 'l', 'd', 'x', 'y', 'z', 'x']
uppercase: ['H', 'W', 'A', 'B', 'C', 'D', 'E', 'A', 'D']
alphanumeric: ['H', 'e', 'l', 'l', 'o', 'W', 'o', 'r', 'l', 'd', '1', '2', '3', 'A', 'B', 'C', 'x', 'y', 'z', '0', 'x', 'D', 'E', 'A', 'D']
whitespace: [' ', ' ', ' ', ' ', ' ']
non_digit: ['H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', ' ', ' ', 'A', 'B', 'C', ' ', 'x', 'y', 'z', ' ', 'x', 'D', 'E', 'A', 'D']
vowel: ['e', 'o', 'o', 'E', 'A']
hex_digit: ['e', '1', '2', '3', 'A', 'B', 'C', '0', 'D', 'E', 'A', 'D']
```

---

## Exercise 3 Solution

```python
import re

text = """
Prices: $5, $50, $500, $5000, $50.99, $500.00
Phone: 555-1234, 555-12-34, 5551234
Codes: A1, AB12, ABC123, ABCD1234
Dates: 2024-01-15, 2024/01/15, 01-15-2024
"""

# 1. Prices with exactly 2 digits after decimal
price_pattern = r"\$\d+\.\d{2}"
print("Prices with decimals:", re.findall(price_pattern, text))
# ['$50.99', '$500.00']

# 2. Phone numbers in format XXX-XXXX
phone_pattern = r"\d{3}-\d{4}"
print("Phone numbers:", re.findall(phone_pattern, text))
# ['555-1234']

# 3. Codes: 2-4 letters followed by 2-4 digits
code_pattern = r"\b[A-Z]{2,4}\d{2,4}\b"
print("Codes:", re.findall(code_pattern, text))
# ['AB12', 'ABC123', 'ABCD1234']

# 4. Dates in YYYY-MM-DD format
date_pattern = r"\d{4}-\d{2}-\d{2}"
print("Dates (YYYY-MM-DD):", re.findall(date_pattern, text))
# ['2024-01-15']
```

---

## Exercise 4 Solution

```python
import re

log_entries = """
2024-01-15 10:23:45 INFO User alice logged in from 192.168.1.100
2024-01-15 10:24:12 ERROR Database connection failed: timeout
2024-01-15 10:25:33 WARNING Memory usage high: 85%
2024-01-15 10:26:01 INFO User bob logged in from 10.0.0.50
2024-01-15 10:27:45 ERROR File not found: /path/to/file.txt
"""

# Full log parsing with named groups
log_pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.+)"

print("Parsed log entries:")
for match in re.finditer(log_pattern, log_entries):
    print(f"  [{match.group('level')}] {match.group('date')} - {match.group('message')[:40]}...")

# Extract IP addresses
ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
ips = re.findall(ip_pattern, log_entries)
print(f"\nIP addresses: {ips}")
# ['192.168.1.100', '10.0.0.50']

# Extract error messages (everything after "ERROR ")
error_pattern = r"ERROR (.+)"
errors = re.findall(error_pattern, log_entries)
print(f"Errors: {errors}")
# ['Database connection failed: timeout', 'File not found: /path/to/file.txt']

# Extract usernames (after "User ")
user_pattern = r"User (\w+)"
users = re.findall(user_pattern, log_entries)
print(f"Users: {users}")
# ['alice', 'bob']
```

---

## Exercise 5 Solution

```python
import re

# 1. Censor phone numbers
text1 = "Call me at 555-123-4567 or 555-987-6543"
result1 = re.sub(r"\d{3}-\d{3}-\d{4}", "XXX-XXX-XXXX", text1)
print(f"1. {result1}")
# "Call me at XXX-XXX-XXXX or XXX-XXX-XXXX"

# 2. Convert MM/DD/YYYY to YYYY-MM-DD
text2 = "Meeting on 01/15/2024 and 02/20/2024"
result2 = re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\1-\2", text2)
print(f"2. {result2}")
# "Meeting on 2024-01-15 and 2024-02-20"

# 3. Remove extra whitespace
text3 = "Too    many     spaces   here"
result3 = re.sub(r"\s+", " ", text3)
print(f"3. {result3}")
# "Too many spaces here"

# 4. Convert snake_case to camelCase
text4 = "user_name, first_name, last_login_date"

def snake_to_camel(match):
    """Convert _x to X."""
    return match.group(1).upper()

result4 = re.sub(r"_([a-z])", snake_to_camel, text4)
print(f"4. {result4}")
# "userName, firstName, lastLoginDate"

# Alternative using lambda
result4_alt = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text4)
```

---

## Exercise 6 Solution

```python
import re

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate US phone number formats."""
    # Remove common separators for consistent checking
    cleaned = re.sub(r"[\s\-\.\(\)]", "", phone)

    # Must be exactly 10 digits
    if not re.match(r"^\d{10}$", cleaned):
        return False

    return True


def is_valid_url(url: str) -> bool:
    """Validate basic URL format."""
    pattern = r"^https?://[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+(:\d+)?(/.*)?$"
    return bool(re.match(pattern, url))


def is_valid_password(password: str) -> tuple[bool, list[str]]:
    """Validate password strength."""
    missing = []

    if len(password) < 8:
        missing.append("at least 8 characters")
    if not re.search(r"[A-Z]", password):
        missing.append("uppercase letter")
    if not re.search(r"[a-z]", password):
        missing.append("lowercase letter")
    if not re.search(r"\d", password):
        missing.append("digit")
    if not re.search(r"[!@#$%^&*()_+\-=]", password):
        missing.append("special character")

    return (len(missing) == 0, missing)


# Test cases
print("Email validation:")
test_emails = ["user@example.com", "user.name@domain.co.uk", "@invalid.com", "no-at-sign"]
for email in test_emails:
    print(f"  '{email}': {is_valid_email(email)}")

print("\nPhone validation:")
test_phones = ["555-123-4567", "(555) 123-4567", "555.123.4567", "12-34-5678"]
for phone in test_phones:
    print(f"  '{phone}': {is_valid_phone(phone)}")

print("\nURL validation:")
test_urls = ["https://example.com", "http://sub.domain.com/path", "example.com", "ftp://files.com"]
for url in test_urls:
    print(f"  '{url}': {is_valid_url(url)}")

print("\nPassword validation:")
test_passwords = ["weak", "Stronger1!", "NoSpecial1", "no_uppercase_1!"]
for pwd in test_passwords:
    valid, missing = is_valid_password(pwd)
    status = "✓" if valid else f"✗ missing: {', '.join(missing)}"
    print(f"  '{pwd}': {status}")
```

**Output**:
```
Email validation:
  'user@example.com': True
  'user.name@domain.co.uk': True
  '@invalid.com': False
  'no-at-sign': False

Phone validation:
  '555-123-4567': True
  '(555) 123-4567': True
  '555.123.4567': True
  '12-34-5678': False

URL validation:
  'https://example.com': True
  'http://sub.domain.com/path': True
  'example.com': False
  'ftp://files.com': False

Password validation:
  'weak': ✗ missing: at least 8 characters, uppercase letter, digit, special character
  'Stronger1!': ✓
  'NoSpecial1': ✗ missing: special character
  'no_uppercase_1!': ✗ missing: uppercase letter
```

---

## Exercise 7 Solution

```python
import re

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

def extract_urls(html: str) -> list[str]:
    """Extract all http/https URLs from href attributes."""
    pattern = r'href="(https?://[^"]+)"'
    return re.findall(pattern, html)


def extract_images(html: str) -> list[str]:
    """Extract all image sources."""
    pattern = r'src="([^"]+)"'
    return re.findall(pattern, html)


def extract_link_text(html: str) -> list[str]:
    """Extract text from anchor tags."""
    pattern = r"<a[^>]*>([^<]+)</a>"
    return re.findall(pattern, html)


def extract_emails(html: str) -> list[str]:
    """Extract email addresses from mailto links."""
    pattern = r'href="mailto:([^"]+)"'
    return re.findall(pattern, html)


print("URLs:", extract_urls(html_text))
# ['https://example.com', 'https://python.org']

print("Images:", extract_images(html_text))
# ['image1.jpg', 'photos/image2.png']

print("Link text:", extract_link_text(html_text))
# ['Example Site', 'Python', 'Contact Us']

print("Emails:", extract_emails(html_text))
# ['contact@example.com']
```

---

## Exercise 8 Solution

```python
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from collections import Counter

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
    """Parse a log line into a LogEntry."""
    # Main pattern: timestamp [LEVEL] logger - message
    main_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(\w+)\] ([\w.]+) - (.+)"

    match = re.match(main_pattern, line)
    if not match:
        return None

    timestamp_str, level, logger, message = match.groups()
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

    # Extract optional fields from message
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", message)
    ip_address = ip_match.group(1) if ip_match else None

    user_match = re.search(r"User '(\w+)'", message)
    user = user_match.group(1) if user_match else None

    code_match = re.search(r"code: (\d+)", message)
    error_code = int(code_match.group(1)) if code_match else None

    return LogEntry(
        timestamp=timestamp,
        level=level,
        logger=logger,
        message=message,
        ip_address=ip_address,
        user=user,
        error_code=error_code
    )


def analyze_logs(logs: list[LogEntry]) -> dict:
    """Analyze logs and return statistics."""
    by_level = Counter(entry.level for entry in logs)

    unique_ips = {entry.ip_address for entry in logs if entry.ip_address}
    unique_users = {entry.user for entry in logs if entry.user}
    error_codes = [entry.error_code for entry in logs if entry.error_code]

    return {
        "total_entries": len(logs),
        "by_level": dict(by_level),
        "unique_ips": unique_ips,
        "unique_users": unique_users,
        "error_codes": error_codes
    }


# Test
log_text = """
2024-01-15 10:23:45.123 [INFO] app.auth - User 'alice' logged in from 192.168.1.1
2024-01-15 10:24:12.456 [ERROR] app.db - Connection failed (code: 5001)
2024-01-15 10:25:33.789 [WARNING] app.memory - High usage: 85%
2024-01-15 10:26:01.234 [INFO] app.auth - User 'bob' logged in from 10.0.0.50
2024-01-15 10:27:45.567 [ERROR] app.file - File not found (code: 4004)
2024-01-15 10:28:00.890 [INFO] app.auth - User 'alice' logged out
"""

entries = []
for line in log_text.strip().split("\n"):
    entry = parse_log_line(line)
    if entry:
        entries.append(entry)
        print(f"Parsed: [{entry.level}] {entry.logger}")

stats = analyze_logs(entries)
print(f"\nTotal entries: {stats['total_entries']}")
print(f"By level: {stats['by_level']}")
print(f"Unique IPs: {stats['unique_ips']}")
print(f"Unique users: {stats['unique_users']}")
print(f"Error codes: {stats['error_codes']}")
```

---

## Exercise 9 Solution

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
        return re.findall(pattern, self.text, flags)

    def replace(
        self,
        pattern: str,
        replacement: str | Callable,
        flags: int = 0
    ) -> "TextProcessor":
        """Replace matches with string or function result."""
        self.text = re.sub(pattern, replacement, self.text, flags=flags)
        self.history.append(self.text)
        return self

    def highlight(self, pattern: str, before: str = ">>", after: str = "<<") -> str:
        """Return text with matches highlighted."""
        def highlighter(match):
            return f"{before}{match.group()}{after}"
        return re.sub(pattern, highlighter, self.text)

    def extract_between(self, start: str, end: str) -> list[str]:
        """Extract text between start and end patterns."""
        pattern = f"{start}(.+?){end}"
        return re.findall(pattern, self.text)

    def undo(self) -> "TextProcessor":
        """Undo last replacement."""
        if len(self.history) > 1:
            self.history.pop()
            self.text = self.history[-1]
        return self

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

# Find capitalized words
capitals = processor.find_all(r"\b[A-Z][a-z]+\b")
print(f"Capitalized words: {capitals}")
# ['The', 'Email', 'Phone', 'Price', 'Date']

# Redact email
processor.replace(r"[\w.]+@[\w.]+", "[EMAIL REDACTED]")
print(f"After redacting email:\n{processor}")

# Highlight phone numbers
highlighted = processor.highlight(r"\(\d{3}\) \d{3}-\d{4}")
print(f"With phone highlighted:\n{highlighted}")

# Undo the redaction
processor.undo()
print(f"After undo (email restored):\n{processor}")

# Extract between patterns
processor2 = TextProcessor("Name: John, Age: 25, City: Boston")
values = processor2.extract_between(r": ", r"(,|$)")
print(f"\nExtracted values: {values}")
# ['John', '25', 'Boston']
```

---

## Quick Reference

### Common Patterns

| Pattern | Matches |
|---------|---------|
| `\d` | Digit (0-9) |
| `\D` | Non-digit |
| `\w` | Word character (a-z, A-Z, 0-9, _) |
| `\W` | Non-word character |
| `\s` | Whitespace |
| `\S` | Non-whitespace |
| `.` | Any character except newline |
| `^` | Start of string |
| `$` | End of string |
| `\b` | Word boundary |

### Quantifiers

| Quantifier | Meaning |
|------------|---------|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 |
| `{n}` | Exactly n |
| `{n,}` | n or more |
| `{n,m}` | Between n and m |

---

[← Back to Exercises](../exercises/ex_05b_regex.md) | [← Back to Chapter](../05b_regex.md) | [← Back to Module 1](../README.md)
