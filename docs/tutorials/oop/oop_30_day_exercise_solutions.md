# 30-Day OOP Plan — Exercise Solutions (Reference)

These are minimal, illustrative solutions. Multiple solutions may be valid; prefer clarity over cleverness.

Note: Some snippets assume files/modules exist; adapt imports/package layout as needed.

## Week 1 — Foundations

### Day 1 — Book
```python
class Book:
    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author

b1 = Book("1984", "George Orwell")
b2 = Book("Dune", "Frank Herbert")
print(b1.title, b2.title)
```

### Day 2 — Describe
```python
class Book:
    def __init__(self, title: str, author: str, pages: int, isbn: str):
        self.title = title
        self.author = author
        self.pages = pages
        self.isbn = isbn

    def describe(self) -> str:
        return f"{self.title} by {self.author} — {self.pages} pages (ISBN: {self.isbn})"
```

### Day 3 — Class var and from_dict
```python
class Book:
    total_created = 0

    def __init__(self, title: str, author: str, pages: int, isbn: str):
        type(self).total_created += 1
        self.title = title
        self.author = author
        self.pages = pages
        self.isbn = isbn

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(data["title"], data["author"], data["pages"], data["isbn"])
```

### Day 4 — Property with validation
```python
class Book:
    def __init__(self, title: str, author: str, pages: int, isbn: str):
        self.title = title
        self.author = author
        self.pages = pages
        self._isbn = None
        self.isbn = isbn

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, value: str) -> None:
        if not isinstance(value, str) or len(value.replace("-", "")) not in (10, 13):
            raise ValueError("Invalid ISBN")
        self._isbn = value
```

### Day 5 — Dataclass with slots
```python
from dataclasses import dataclass

@dataclass(slots=True)
class Book:
    title: str
    author: str
    pages: int
    isbn: str
```

### Day 6 — pytest sample
```python
# test_book.py
from book import Book

def test_describe():
    b = Book("1984", "George Orwell", 328, "1234567890")
    assert "1984" in b.describe()
```

### Day 7 — Inheritance
```python
class Item:
    def __init__(self, title: str):
        self.title = title

class Book(Item):
    def __init__(self, title: str, author: str):
        super().__init__(title)
        self.author = author
```

## Week 2 — Polymorphism, ABCs, Composition, Typing

### Day 8 — Polymorphism
```python
class Book:
    def __init__(self, title: str, pages: int):
        self.title = title
        self.pages = pages
    def get_size(self) -> int:
        return self.pages

class EBook:
    def __init__(self, title: str, megabytes: float):
        self.title = title
        self.megabytes = megabytes
    def get_size(self) -> int:
        return int(self.megabytes * 500_000)  # heuristic
```

### Day 9 — ABC
```python
from abc import ABC, abstractmethod

class Borrowable(ABC):
    @abstractmethod
    def borrow(self, member_id: str) -> None: ...
    @abstractmethod
    def return_(self) -> None: ...

class Item(Borrowable):
    def __init__(self, title: str):
        self.title = title
        self._borrower = None
    def borrow(self, member_id: str) -> None:
        if self._borrower is not None:
            raise RuntimeError("Already borrowed")
        self._borrower = member_id
    def return_(self) -> None:
        self._borrower = None
```

### Day 10 — Composition
```python
class NotificationService:
    def send(self, to: str, msg: str) -> None:
        print(f"To {to}: {msg}")

class Library:
    def __init__(self, notifier: NotificationService):
        self._notifier = notifier
        self._items = {}
    def add_item(self, item):
        self._items[item.title] = item
    def notify(self, to: str, msg: str):
        self._notifier.send(to, msg)
```

### Day 11 — Protocol
```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, to: str, msg: str) -> None: ...

class EmailNotifier:
    def send(self, to: str, msg: str) -> None:
        print(f"EMAIL {to}: {msg}")

class SMSNotifier:
    def send(self, to: str, msg: str) -> None:
        print(f"SMS {to}: {msg}")
```

### Day 12 — SRP/OCP
```python
class Inventory:
    def __init__(self):
        self._items = {}
    def add(self, item): self._items[item.title] = item
    def get(self, title): return self._items.get(title)

class AudioBook:
    def __init__(self, title: str, narrator: str):
        self.title = title
        self.narrator = narrator
```

### Day 13 — LSP/ISP/DIP
```python
class Authenticator:
    def authenticate(self, user: str, pwd: str) -> bool: return True

class Authorizer:
    def can_borrow(self, user: str) -> bool: return True

class Library:
    def __init__(self, notifier):
        self._notifier = notifier
```

### Day 14 — Integration
```python
inv = Inventory()
inv.add(AudioBook("Dune", "Narrator"))
```

## Week 3 — Patterns and Python Data Model

### Day 15 — Factory
```python
class ItemFactory:
    @staticmethod
    def create(payload: dict):
        typ = payload["type"].lower()
        if typ == "book":
            return Book(payload["title"], payload["author"])
        if typ == "ebook":
            return EBook(payload["title"], payload["megabytes"])
        if typ == "audiobook":
            return AudioBook(payload["title"], payload["narrator"])
        raise ValueError("Unknown type")
```

### Day 16 — Strategy
```python
class PricingStrategy:
    def price(self, base: float) -> float: return base

class StudentPricing(PricingStrategy):
    def price(self, base: float) -> float: return base * 0.8

class Library:
    def __init__(self, pricing: PricingStrategy):
        self._pricing = pricing
```

### Day 17 — Observer
```python
class EventBus:
    def __init__(self): self._subs = {}
    def subscribe(self, event: str, fn): self._subs.setdefault(event, []).append(fn)
    def publish(self, event: str, data):
        for fn in self._subs.get(event, []): fn(data)
```

### Day 18 — Decorator/Composite
```python
class DiscountedItem:
    def __init__(self, item, pct: float):
        self._item = item; self._pct = pct
    def price(self, base: float) -> float:
        return base * (1 - self._pct)

class Collection:
    def __init__(self, name: str): self.name = name; self._children = []
    def add(self, item): self._children.append(item)
    def __iter__(self): return iter(self._children)
```

### Day 19 — Dunder methods
```python
class Catalog:
    def __init__(self, items): self._items = list(items)
    def __iter__(self): return iter(self._items)
    def __repr__(self): return f"Catalog(n={len(self._items)})"
```

### Day 20 — Context managers
```python
class LoanSession:
    def __init__(self, library):
        self._lib = library
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        if exc: print("rollback"); return False
        print("commit"); return False
```

### Day 21 — Refactor
```python
# Focus on extracting small classes/functions and adding tests.
```

## Week 4 — Advanced OOP, Testing, Error Handling

### Day 22 — Descriptors
```python
class Validated:
    def __init__(self, validator): self.validator = validator; self._name = None
    def __set_name__(self, owner, name): self._name = name
    def __get__(self, inst, owner):
        if inst is None: return self
        return inst.__dict__.get(self._name)
    def __set__(self, inst, value):
        self.validator(value); inst.__dict__[self._name] = value

def valid_isbn(x):
    if not isinstance(x, str) or len(x.replace('-', '')) not in (10, 13):
        raise ValueError("bad isbn")

class Book:
    isbn = Validated(valid_isbn)
    def __init__(self, isbn): self.isbn = isbn
```

### Day 23 — Metaclass registry
```python
class RegistryMeta(type):
    registry = {}
    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        if name != 'Base': mcls.registry[name.lower()] = cls
        return cls

class Base(metaclass=RegistryMeta): pass

class Book(Base): pass
class EBook(Base): pass

def get_subclass(name: str): return RegistryMeta.registry.get(name)
```

### Day 24 — MI & mixins
```python
class TimestampedMixin:
    def __init__(self, *a, **kw):
        import time; super().__init__(*a, **kw); self.created_at = time.time()

class SerializableMixin:
    def to_dict(self): return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class Item: pass

class Book(TimestampedMixin, SerializableMixin, Item):
    def __init__(self, title: str): super().__init__(); self.title = title
```

### Day 25 — Monkey patching
```python
class Slow:
    def work(self):
        import time; time.sleep(1); return 42

class Patch:
    def __init__(self, obj, name, new): self.obj=obj; self.name=name; self.new=new
    def __enter__(self): self.old=getattr(self.obj, self.name); setattr(self.obj, self.name, self.new)
    def __exit__(self, *exc): setattr(self.obj, self.name, self.old)

def fast_work(self): return 42

s = Slow()
with Patch(Slow, 'work', fast_work): assert s.work()==42
```

### Day 26 — Error handling
```python
class LibraryError(Exception): pass
class LoanError(LibraryError): pass

def checkout(item, user):
    if item is None: raise LoanError("missing item")
```

### Day 27 — Testing with fakes
```python
class FakeNotifier:
    def __init__(self): self.sent = []
    def send(self, to, msg): self.sent.append((to, msg))

def test_notify():
    f = FakeNotifier(); lib = Library(f)
    lib.notify('u', 'm')
    assert ('u','m') in f.sent
```

### Day 28 — JSON serialization
```python
import json

class Loan:
    version = 1
    def __init__(self, user: str, title: str): self.user=user; self.title=title
    def to_json(self): return json.dumps({'v': self.version, 'user': self.user, 'title': self.title})
    @classmethod
    def from_json(cls, s: str):
        d = json.loads(s)
        if d.get('v') != cls.version: raise ValueError('bad version')
        return cls(d['user'], d['title'])
```

### Day 29 — Async service (sketch)
```python
import asyncio

class ReminderService:
    async def send_overdue(self, items):
        async def send_one(i): await asyncio.sleep(0); return f"reminded {i}"
        return await asyncio.gather(*(send_one(i) for i in items))
```

### Day 30 — Capstone demo
```python
def demo():
    print("borrow/return, notify, serialize, tests run")
```
