# Project 4: REST API with Litestar

**Goal**: Build a backend API for a Todo application.

## Learning Objectives

* REST Principles
* Litestar Framework
* SQLModel (Database)
* Type-safe API definitions

## Prerequisites

Before starting this project, review:

* **[REST API Concepts](./api-concepts/README.md)** - Idempotency, pagination, error handling, caching, and other essential API patterns

## Requirements

* **Models**: `TodoItem` (id, title, completed).
* **Endpoints**:
  * `GET /todos`: List all items.
  * `POST /todos`: Create item.
  * `PUT /todos/{id}`: Update item.
  * `DELETE /todos/{id}`: Delete item.
* **Data Store**: Use SQLite for simplicity.

## Resources

* [Litestar Guide](./litestar/README.md)
* [SQLModel Guide](./sqlmodel/README.md)
* [REST API Concepts](./api-concepts/README.md)
