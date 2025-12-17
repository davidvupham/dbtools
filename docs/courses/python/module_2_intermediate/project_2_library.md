# Project 2: Library Management System

**Goal**: Model a library with Books, Members, and Loans using Object-Oriented Programming.

## Learning Objectives

* Classes and Objects
* Encapsulation (Private attributes)
* State Management
* Type Hints

## Requirements

1. **Classes**
    * `Book`: Title, Author, ISBN, Status (Available/Checked Out).
    * `Member`: Name, ID, List of Loaned Books.
    * `Library`: Collection of Books, Registry of Members.

2. **Features**
    * `add_book(book)`
    * `register_member(member)`
    * `lend_book(isbn, member_id)`: Update book status, add to member's list.
        * Raise error if book is not available.
    * `return_book(isbn)`: Update status, remove from member's list.

3. **Data Protection**
    * Make the book list private (`_books`).
    * Expose a property or method to search books.

## Challenge

Add specific logic: A member cannot borrow more than 3 books at a time.
