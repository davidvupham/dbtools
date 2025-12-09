# SQLModel Tutorial

Type-safe database operations combining Pydantic and SQLAlchemy.

## Overview

**SQLModel** is a library for interacting with SQL databases using Python type hints. Created by the author of FastAPI, it combines the power of **Pydantic** (data validation) and **SQLAlchemy** (database operations) into a single, intuitive API.

| | |
|---|---|
| **Package** | `sqlmodel` |
| **Install** | `pip install sqlmodel` |
| **Documentation** | [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/) |
| **GitHub** | [tiangolo/sqlmodel](https://github.com/tiangolo/sqlmodel) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Defining Models](#defining-models)
4. [Database Setup](#database-setup)
5. [CRUD Operations](#crud-operations)
6. [Relationships](#relationships)
7. [Queries](#queries)
8. [FastAPI Integration](#fastapi-integration)
9. [Migrations with Alembic](#migrations-with-alembic)
10. [Best Practices](#best-practices)

---

## Installation

```bash
pip install sqlmodel
```

For async support:

```bash
pip install sqlmodel aiosqlite  # SQLite async
pip install sqlmodel asyncpg    # PostgreSQL async
```

---

## Quick Start

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Define a model
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None

# Create database engine
engine = create_engine("sqlite:///database.db")

# Create tables
SQLModel.metadata.create_all(engine)

# Insert data
with Session(engine) as session:
    hero = Hero(name="Spider-Man", secret_name="Peter Parker", age=25)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    print(f"Created hero: {hero.name} with id: {hero.id}")

# Query data
with Session(engine) as session:
    heroes = session.exec(select(Hero)).all()
    for hero in heroes:
        print(f"{hero.name}: {hero.secret_name}")
```

---

## Defining Models

### Basic Model

```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    full_name: str | None = None
    is_active: bool = Field(default=True)
```

### Field Options

```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Required field with index
    name: str = Field(index=True)

    # Optional field with default
    description: str | None = Field(default=None)

    # Numeric constraints
    price: float = Field(ge=0)  # Greater than or equal to 0
    quantity: int = Field(default=0, ge=0)

    # String constraints
    sku: str = Field(min_length=5, max_length=20, unique=True)

    # Timestamp with default
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Data Models vs Table Models

Use separate models for API vs Database:

```python
from sqlmodel import Field, SQLModel

# Base model (shared fields)
class UserBase(SQLModel):
    username: str
    email: str
    full_name: str | None = None

# Model for creating (no id)
class UserCreate(UserBase):
    password: str

# Model for reading (includes id)
class UserRead(UserBase):
    id: int

# Database table model
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
```

---

## Database Setup

### SQLite

```python
from sqlmodel import create_engine

# File-based SQLite
engine = create_engine("sqlite:///./database.db")

# In-memory SQLite
engine = create_engine("sqlite:///:memory:")

# With connection arguments
engine = create_engine(
    "sqlite:///./database.db",
    connect_args={"check_same_thread": False}  # For FastAPI
)
```

### PostgreSQL

```python
from sqlmodel import create_engine

engine = create_engine(
    "postgresql://user:password@localhost:5432/dbname"
)

# With connection pool
engine = create_engine(
    "postgresql://user:password@localhost:5432/dbname",
    pool_size=10,
    max_overflow=20,
)
```

### Async Engine

```python
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
    echo=True,
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

---

## CRUD Operations

### Create

```python
from sqlmodel import Session

def create_user(session: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

### Read

```python
from sqlmodel import Session, select

def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()
```

### Update

```python
from sqlmodel import Session

def update_user(session: Session, user_id: int, user_data: UserUpdate) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None

    # Update only provided fields
    user_dict = user_data.model_dump(exclude_unset=True)
    for key, value in user_dict.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

### Delete

```python
from sqlmodel import Session

def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True
```

---

## Relationships

### One-to-Many

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationship to heroes
    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Foreign key
    team_id: int | None = Field(default=None, foreign_key="team.id")

    # Relationship to team
    team: Team | None = Relationship(back_populates="heroes")
```

### Many-to-Many

```python
from sqlmodel import Field, Relationship, SQLModel

# Link table
class HeroPowerLink(SQLModel, table=True):
    hero_id: int = Field(foreign_key="hero.id", primary_key=True)
    power_id: int = Field(foreign_key="power.id", primary_key=True)

class Power(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    heroes: list["Hero"] = Relationship(
        back_populates="powers",
        link_model=HeroPowerLink
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    powers: list[Power] = Relationship(
        back_populates="heroes",
        link_model=HeroPowerLink
    )
```

### Querying Relationships

```python
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

# Eager loading
def get_team_with_heroes(session: Session, team_id: int) -> Team | None:
    statement = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.heroes))
    )
    return session.exec(statement).first()
```

---

## Queries

### Basic Queries

```python
from sqlmodel import Session, select

# All records
heroes = session.exec(select(Hero)).all()

# First record
hero = session.exec(select(Hero)).first()

# By primary key
hero = session.get(Hero, 1)
```

### Filtering

```python
from sqlmodel import Session, select

# Equal
statement = select(Hero).where(Hero.name == "Spider-Man")

# Not equal
statement = select(Hero).where(Hero.age != 25)

# Greater than
statement = select(Hero).where(Hero.age > 18)

# Multiple conditions (AND)
statement = select(Hero).where(Hero.age > 18, Hero.team_id == 1)

# OR conditions
from sqlmodel import or_
statement = select(Hero).where(or_(Hero.age < 18, Hero.age > 60))

# LIKE
statement = select(Hero).where(Hero.name.contains("Man"))

# IN
statement = select(Hero).where(Hero.team_id.in_([1, 2, 3]))

# IS NULL
statement = select(Hero).where(Hero.team_id == None)
```

### Ordering and Pagination

```python
from sqlmodel import Session, select

# Order by
statement = select(Hero).order_by(Hero.name)
statement = select(Hero).order_by(Hero.age.desc())

# Pagination
statement = select(Hero).offset(10).limit(20)

# Combined
statement = (
    select(Hero)
    .where(Hero.age > 18)
    .order_by(Hero.name)
    .offset(0)
    .limit(10)
)
```

### Aggregations

```python
from sqlmodel import Session, select, func

# Count
statement = select(func.count(Hero.id))
count = session.exec(statement).one()

# Count with condition
statement = select(func.count(Hero.id)).where(Hero.age > 18)

# Average
statement = select(func.avg(Hero.age))

# Group by
statement = (
    select(Hero.team_id, func.count(Hero.id))
    .group_by(Hero.team_id)
)
```

---

## FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

app = FastAPI()

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroRead])
def read_heroes(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    heroes = session.exec(select(Hero).offset(skip).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroRead)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Async FastAPI

```python
from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine

async def get_async_session() -> AsyncSession:
    async with AsyncSession(async_engine) as session:
        yield session

@app.get("/heroes/")
async def read_heroes(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Hero))
    return result.all()
```

---

## Migrations with Alembic

### Setup

```bash
pip install alembic

# Initialize Alembic
alembic init alembic
```

### Configure `alembic/env.py`

```python
from sqlmodel import SQLModel
from myapp.models import *  # Import all models

target_metadata = SQLModel.metadata
```

### Create and Run Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Best Practices

### 1. Use Session Context Manager

```python
# ✅ Good - automatic cleanup
with Session(engine) as session:
    hero = session.get(Hero, 1)

# ❌ Bad - manual cleanup required
session = Session(engine)
try:
    hero = session.get(Hero, 1)
finally:
    session.close()
```

### 2. Separate API and DB Models

```python
# Base without table
class HeroBase(SQLModel):
    name: str
    secret_name: str

# API models
class HeroCreate(HeroBase):
    pass

class HeroRead(HeroBase):
    id: int

# Database model
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
```

### 3. Use Transactions

```python
from sqlmodel import Session

def transfer_hero(session: Session, hero_id: int, new_team_id: int):
    try:
        hero = session.get(Hero, hero_id)
        old_team = session.get(Team, hero.team_id)
        new_team = session.get(Team, new_team_id)

        old_team.hero_count -= 1
        new_team.hero_count += 1
        hero.team_id = new_team_id

        session.add(old_team)
        session.add(new_team)
        session.add(hero)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

### 4. Index Frequently Queried Fields

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)  # Indexed
    username: str = Field(index=True)            # Indexed
    bio: str | None = None                       # Not indexed
```

---

## Quick Reference

### Common Field Types

| Python Type | SQL Type |
|-------------|----------|
| `int` | INTEGER |
| `str` | VARCHAR |
| `float` | FLOAT |
| `bool` | BOOLEAN |
| `datetime` | DATETIME |
| `date` | DATE |
| `bytes` | BLOB |

### Field Arguments

| Argument | Description |
|----------|-------------|
| `primary_key=True` | Primary key |
| `foreign_key="table.id"` | Foreign key |
| `index=True` | Create index |
| `unique=True` | Unique constraint |
| `default=value` | Default value |
| `nullable=False` | Not nullable |

---

## See Also

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI + SQLModel](https://sqlmodel.tiangolo.com/tutorial/fastapi/)
- [Litestar Tutorial](../litestar/README.md) - Alternative async web framework

---

[← Back to Modules Index](../README.md)
