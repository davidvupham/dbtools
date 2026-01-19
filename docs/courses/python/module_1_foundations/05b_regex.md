# Regular Expressions

Regular expressions (regex) are powerful patterns for searching, matching, and manipulating text. They're essential for tasks like validation, parsing, and text extraction.

## What are regular expressions?

A regular expression is a sequence of characters that defines a search pattern. Python's `re` module provides regex support.

```python
import re

# Find all email addresses in text
text = "Contact us at support@example.com or sales@example.com"
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
print(emails)  # ['support@example.com', 'sales@example.com']
```

## Basic patterns

### Literal characters

Most characters match themselves:

```python
import re

text = "Hello, World!"
result = re.search(r"World", text)
print(result.group())  # "World"
```

### Special characters (metacharacters)

| Character | Meaning | Example | Matches |
|-----------|---------|---------|---------|
| `.` | Any character (except newline) | `a.c` | "abc", "a1c", "a c" |
| `^` | Start of string | `^Hello` | "Hello world" (at start) |
| `$` | End of string | `world$` | "Hello world" (at end) |
| `*` | 0 or more | `ab*c` | "ac", "abc", "abbc" |
| `+` | 1 or more | `ab+c` | "abc", "abbc" (not "ac") |
| `?` | 0 or 1 | `ab?c` | "ac", "abc" (not "abbc") |
| `\` | Escape special char | `\.` | Literal "." |
| `|` | Or | `cat|dog` | "cat" or "dog" |

```python
import re

# Match "color" or "colour"
pattern = r"colou?r"
print(re.search(pattern, "color"))   # Match
print(re.search(pattern, "colour"))  # Match

# Match file extensions
pattern = r"\.py$"
print(re.search(pattern, "script.py"))   # Match
print(re.search(pattern, "script.txt"))  # No match
```

### Character classes

| Pattern | Meaning | Equivalent |
|---------|---------|------------|
| `[abc]` | Any of a, b, or c | |
| `[a-z]` | Any lowercase letter | |
| `[A-Z]` | Any uppercase letter | |
| `[0-9]` | Any digit | `\d` |
| `[^abc]` | NOT a, b, or c | |
| `\d` | Any digit | `[0-9]` |
| `\D` | Not a digit | `[^0-9]` |
| `\w` | Word character | `[a-zA-Z0-9_]` |
| `\W` | Not a word character | `[^a-zA-Z0-9_]` |
| `\s` | Whitespace | `[ \t\n\r\f\v]` |
| `\S` | Not whitespace | `[^ \t\n\r\f\v]` |

```python
import re

# Match phone numbers
text = "Call 555-1234 or 555-5678"
phones = re.findall(r'\d{3}-\d{4}', text)
print(phones)  # ['555-1234', '555-5678']

# Match words
words = re.findall(r'\w+', "Hello, World!")
print(words)  # ['Hello', 'World']
```

### Quantifiers

| Pattern | Meaning |
|---------|---------|
| `{n}` | Exactly n times |
| `{n,}` | n or more times |
| `{n,m}` | Between n and m times |
| `*` | 0 or more (same as `{0,}`) |
| `+` | 1 or more (same as `{1,}`) |
| `?` | 0 or 1 (same as `{0,1}`) |

```python
import re

# Match zip codes (5 digits)
pattern = r'\d{5}'
print(re.findall(pattern, "ZIP: 12345 and 98765"))  # ['12345', '98765']

# Match optional area code: (123) or 123 or nothing
pattern = r'(\(\d{3}\)|\d{3})?\s?\d{3}-\d{4}'
print(re.search(pattern, "(555) 123-4567"))  # Match
print(re.search(pattern, "555 123-4567"))    # Match
print(re.search(pattern, "123-4567"))        # Match
```

## The re module

### Core functions

```python
import re

text = "The quick brown fox jumps over the lazy dog"

# re.search() - Find first match
match = re.search(r'fox', text)
if match:
    print(match.group())    # 'fox'
    print(match.start())    # 16 (start index)
    print(match.end())      # 19 (end index)
    print(match.span())     # (16, 19)

# re.match() - Match at beginning only
match = re.match(r'The', text)  # Match
match = re.match(r'fox', text)  # No match (not at start)

# re.findall() - Find all matches (returns list of strings)
words = re.findall(r'\b\w{4}\b', text)  # 4-letter words
print(words)  # ['quick', 'brown', 'over', 'lazy']

# re.finditer() - Find all matches (returns iterator of match objects)
for match in re.finditer(r'\b\w{3}\b', text):
    print(f"'{match.group()}' at {match.span()}")

# re.sub() - Replace matches
result = re.sub(r'fox', 'cat', text)
print(result)  # "The quick brown cat jumps..."

# re.split() - Split by pattern
parts = re.split(r'\s+', text)  # Split on whitespace
print(parts)  # ['The', 'quick', 'brown', ...]
```

### Compiling patterns

For patterns used multiple times, compile them for better performance:

```python
import re

# Compile once
email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')

# Use many times
emails1 = email_pattern.findall(text1)
emails2 = email_pattern.findall(text2)
match = email_pattern.search(text3)
```

### Flags

Modify pattern behavior with flags:

```python
import re

text = "Hello\nWORLD"

# re.IGNORECASE (or re.I) - Case-insensitive matching
re.findall(r'hello', text, re.IGNORECASE)  # ['Hello']

# re.MULTILINE (or re.M) - ^ and $ match line boundaries
re.findall(r'^.*$', text, re.MULTILINE)  # ['Hello', 'WORLD']

# re.DOTALL (or re.S) - . matches newline too
re.search(r'Hello.WORLD', text, re.DOTALL)  # Match

# Combine flags
re.findall(r'^hello$', text, re.IGNORECASE | re.MULTILINE)
```

## Groups

Capture parts of a match with parentheses:

```python
import re

# Basic groups
text = "John Smith, age 30"
match = re.search(r'(\w+) (\w+), age (\d+)', text)
if match:
    print(match.group(0))  # Full match: "John Smith, age 30"
    print(match.group(1))  # First group: "John"
    print(match.group(2))  # Second group: "Smith"
    print(match.group(3))  # Third group: "30"
    print(match.groups())  # All groups: ('John', 'Smith', '30')

# Named groups
pattern = r'(?P<first>\w+) (?P<last>\w+), age (?P<age>\d+)'
match = re.search(pattern, text)
if match:
    print(match.group('first'))  # "John"
    print(match.group('last'))   # "Smith"
    print(match.groupdict())     # {'first': 'John', 'last': 'Smith', 'age': '30'}
```

### Non-capturing groups

Use `(?:...)` when you need grouping but don't need to capture:

```python
import re

# Capturing group
re.findall(r'(https?)://(\S+)', "Visit http://example.com")
# [('http', 'example.com')]

# Non-capturing group for protocol
re.findall(r'(?:https?)://(\S+)', "Visit http://example.com")
# ['example.com']
```

## Common patterns

### Email validation

```python
import re

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[\w.+-]+@[\w-]+\.[\w.-]+$'
    return bool(re.match(pattern, email))

print(is_valid_email("user@example.com"))  # True
print(is_valid_email("invalid-email"))      # False
```

### Phone number extraction

```python
import re

def extract_phone_numbers(text: str) -> list[str]:
    """Extract US phone numbers in various formats."""
    pattern = r'''
        (?:
            \+?1[-.\s]?       # Optional country code
        )?
        \(?                   # Optional opening paren
        \d{3}                 # Area code
        \)?                   # Optional closing paren
        [-.\s]?               # Optional separator
        \d{3}                 # Exchange
        [-.\s]?               # Optional separator
        \d{4}                 # Subscriber
    '''
    return re.findall(pattern, text, re.VERBOSE)

text = "Call (555) 123-4567 or 555.987.6543 or +1-555-111-2222"
print(extract_phone_numbers(text))
```

### URL parsing

```python
import re

def parse_url(url: str) -> dict | None:
    """Parse URL into components."""
    pattern = r'''
        ^
        (?P<protocol>https?)://
        (?P<domain>[\w.-]+)
        (?::(?P<port>\d+))?
        (?P<path>/[\w/.-]*)?
        (?:\?(?P<query>[\w=&]+))?
        $
    '''
    match = re.match(pattern, url, re.VERBOSE)
    if match:
        return match.groupdict()
    return None

url = "https://example.com:8080/path/to/resource?key=value"
print(parse_url(url))
# {'protocol': 'https', 'domain': 'example.com', 'port': '8080',
#  'path': '/path/to/resource', 'query': 'key=value'}
```

### Data extraction

```python
import re

def extract_dates(text: str) -> list[tuple[str, str, str]]:
    """Extract dates in MM/DD/YYYY format."""
    pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
    return re.findall(pattern, text)

text = "Events on 12/25/2024 and 1/1/2025"
dates = extract_dates(text)
print(dates)  # [('12', '25', '2024'), ('1', '1', '2025')]
```

## Substitution

### Basic replacement

```python
import re

text = "Hello World"

# Simple replacement
result = re.sub(r'World', 'Python', text)
print(result)  # "Hello Python"

# Replace all digits with X
text = "Phone: 555-1234"
result = re.sub(r'\d', 'X', text)
print(result)  # "Phone: XXX-XXXX"

# Limit replacements
text = "one two one two one"
result = re.sub(r'one', 'ONE', text, count=2)
print(result)  # "ONE two ONE two one"
```

### Using captured groups

```python
import re

# Swap first and last name
text = "Smith, John"
result = re.sub(r'(\w+), (\w+)', r'\2 \1', text)
print(result)  # "John Smith"

# Named groups in replacement
result = re.sub(r'(?P<last>\w+), (?P<first>\w+)', r'\g<first> \g<last>', text)
print(result)  # "John Smith"
```

### Replacement function

```python
import re

def censor(match):
    """Replace matched word with asterisks."""
    word = match.group()
    return '*' * len(word)

text = "The password is secret123"
bad_words = re.compile(r'password|secret\d*', re.IGNORECASE)
result = bad_words.sub(censor, text)
print(result)  # "The ******** is *********"
```

## Example from our code

From the dbtools codebase, regex is used for log parsing:

```python
# python/gds_database/src/gds_database/log_parser.py
import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str

LOG_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    r'\s+(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)'
    r'\s+(?P<message>.*)$'
)

def parse_log_line(line: str) -> LogEntry | None:
    """Parse a single log line into a LogEntry."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()
    return LogEntry(
        timestamp=datetime.fromisoformat(data['timestamp']),
        level=data['level'],
        message=data['message']
    )

# Usage
line = "2024-01-15 10:30:45 ERROR Database connection failed"
entry = parse_log_line(line)
print(entry)  # LogEntry(timestamp=..., level='ERROR', message='Database...')
```

## Best practices

### Raw strings

Always use raw strings (`r'...'`) for regex patterns to avoid escaping issues:

```python
# BAD - Need to escape backslashes
pattern = "\\d+\\.\\d+"

# GOOD - Raw string, cleaner
pattern = r'\d+\.\d+'
```

### Verbose mode

Use `re.VERBOSE` for complex patterns:

```python
import re

# Hard to read
pattern = r'^[\w.+-]+@[\w-]+\.[\w.-]+$'

# Much clearer with VERBOSE
pattern = re.compile(r'''
    ^                   # Start of string
    [\w.+-]+            # Username (letters, digits, dots, plus, dash)
    @                   # @ symbol
    [\w-]+              # Domain name
    \.                  # Dot
    [\w.-]+             # TLD (can have multiple parts like .co.uk)
    $                   # End of string
''', re.VERBOSE)
```

### Avoid catastrophic backtracking

Be careful with nested quantifiers:

```python
# BAD - Can hang on certain inputs (exponential backtracking)
pattern = r'(a+)+b'

# GOOD - Use atomic groups or possessive quantifiers if available
# Or restructure the pattern
pattern = r'a+b'
```

## Best practices summary

1. **Use raw strings**: Always prefix patterns with `r`
2. **Compile for reuse**: Use `re.compile()` for frequently used patterns
3. **Use verbose mode**: `re.VERBOSE` makes complex patterns readable
4. **Name your groups**: `(?P<name>...)` is clearer than numbered groups
5. **Test your patterns**: Use regex testers like regex101.com
6. **Handle no-match cases**: Always check if `search()` or `match()` returned `None`
7. **Be specific**: Anchor patterns with `^` and `$` when matching whole strings
8. **Avoid overcomplicating**: Sometimes string methods (`split`, `startswith`) are clearer

---

[← Back to Module 1](./README.md) | [Next: Error Handling →](./06_error_handling.md)
