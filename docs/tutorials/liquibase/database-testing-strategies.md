# Database Testing Strategies for CI/CD

**Date:** November 20, 2025
**Purpose:** Guide to testing database changes in automated pipelines
**Audience:** Developers, DBAs, DevOps Engineers
**Prerequisites:** Basic SQL knowledge, understanding of testing concepts
**Status:** Phase 1A - Core chapters complete, remaining chapters in Phase 1B

---

## Table of Contents

1. [Introduction to Database Testing](#introduction-to-database-testing)
2. [Why Test Database Changes](#why-test-database-changes)
3. [Types of Database Tests](#types-of-database-tests)
4. [Database Unit Testing](#database-unit-testing)
5. [Integration Testing](#integration-testing) ⚠️ *Phase 1B*
6. [Performance Testing](#performance-testing) ⚠️ *Phase 1B*
7. [Data Quality Testing](#data-quality-testing) ⚠️ *Phase 1B*
8. [Testing in CI/CD Pipelines](#testing-in-cicd-pipelines) ⚠️ *Phase 1B*
9. [Test Data Management](#test-data-management) ⚠️ *Phase 1B*
10. [Tools and Frameworks](#tools-and-frameworks) ⚠️ *Phase 1B*
11. [Best Practices](#best-practices) ⚠️ *Phase 1B*

---

## Introduction to Database Testing

### What is Database Testing?

Database testing validates that database changes:
- ✅ Work as intended
- ✅ Don't break existing functionality
- ✅ Perform acceptably
- ✅ Maintain data integrity
- ✅ Meet quality standards

**Think of it like:**
- Unit testing for your code → Unit testing for your database
- Integration tests for APIs → Integration tests for database queries
- Performance tests for apps → Performance tests for database operations

### Why Database Testing in CI/CD?

**Traditional approach (manual):**
```
Developer writes SQL
    ↓
DBA reviews manually (if available)
    ↓
Deploy to production
    ↓
🤞 Hope nothing breaks
```

**Problem:** Errors found in production = expensive fixes

**CI/CD approach (automated):**
```
Developer writes SQL + tests
    ↓
Commit to Git
    ↓
Automated tests run in GitHub Actions
    ↓
Tests pass → Deploy automatically
    ↓
Tests fail → Deployment blocked, fix in dev
    ↓
✅ Confidence in quality
```

**Benefit:** Errors caught in pipeline = cheap fixes

### Testing Philosophy

**The Testing Pyramid for Databases:**

```
           /\
          /  \  E2E Tests
         /    \  (Few, Slow, Expensive)
        /------\
       /        \
      / Integration\ Tests
     /    Tests    \ (Some, Medium Speed)
    /--------------\
   /                \
  /   Unit Tests     \
 /    (Many, Fast,    \
/      Cheap)          \
/______________________\
```

**Apply to databases:**
- **Many unit tests (80%):** Test individual database objects (fast, < 1 second)
- **Some integration tests (15%):** Test database with application (medium, 1-10 seconds)
- **Few E2E tests (5%):** Test complete user workflows (slow, 10+ seconds)

**Why this matters:**
- Fast tests = fast feedback
- Cheap tests = run on every commit
- Many tests = high confidence

---

## Why Test Database Changes

### The Cost of Database Bugs

Production database bugs are **expensive**. Here's why:

#### Example 1: Missing Constraint Allows Bad Data

**Scenario:** Developer adds new table but forgets NOT NULL constraint

```sql
-- What was deployed:
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,  -- ❌ Forgot NOT NULL!
    order_date DATETIME,
    total_amount DECIMAL(10,2)
);
```

**Impact:**
- Application assumes `customer_id` always has value
- NULL values get inserted (50,000 records over 2 weeks)
- Reports break, queries fail
- Customer service receives complaints

**Cost:**
- 40 hours to identify, fix, and clean data
- Developer time: $2,000
- Reputation damage: Priceless

**If tested:**
```sql
-- Test would have caught this:
INSERT INTO orders (order_id, customer_id) VALUES (1, NULL);
-- Expected: Error
-- Actual: Success ← Test fails, bug caught before production
```

#### Example 2: Performance Regression

**Scenario:** Schema change removes important index

```sql
-- Migration removes old index
DROP INDEX idx_orders_customer_id ON orders;

-- But forgets to add it back in new structure
CREATE TABLE orders_new (...);
-- ❌ Missing index!
```

**Impact:**
- Query that was instant now takes 30 seconds
- Application timeouts
- Database CPU spikes to 100%
- Site goes down for 2 hours

**Cost:**
- Downtime: 2 hours
- Lost revenue: $10,000
- Emergency fix time: 8 hours × 3 people = $1,200
- Total: $11,200

**If tested:**
```sql
-- Performance test would have caught this:
-- Baseline: Query runs in 100ms
-- After change: Query runs in 30,000ms ← Test fails, bug caught
```

#### Example 3: Data Corruption

**Scenario:** Data migration script has logic error

```sql
-- Migration to normalize customer addresses
UPDATE customers
SET state = SUBSTRING(address, -2, 2)  -- ❌ Bug: Should be last 2 chars
WHERE address LIKE '%,%';

-- Actually updates with wrong values
```

**Impact:**
- 10,000 customer addresses corrupted
- Orders ship to wrong states
- Customer complaints flood in
- Legal issues

**Cost:**
- Data recovery: 100 hours
- Customer service: 200 hours
- Free shipping to correct addresses: $50,000
- Legal fees: Unknown
- **Total: $100,000+**

**If tested:**
```sql
-- Test would have caught this:
INSERT INTO test_customers (address) VALUES ('123 Main St, Boston, MA');
-- Run migration
-- Assert: state = 'MA'
-- Actual: state = 'MA' ✅ (or wrong value ❌)
```

### Benefits of Database Testing

#### 1. Catch Bugs Before Production

**Impact:** Zero production issues from database changes

```
Without tests:
    100 deployments → 5 production bugs → 5 incidents → 100 hours fixing

With tests:
    100 deployments → 5 bugs caught in CI → 0 incidents → 10 hours fixing

Savings: 90 hours = $4,500
```

#### 2. Faster Development

**Developers work faster when they have confidence:**

- Make changes without fear
- Refactor safely
- Try new approaches
- Automated feedback (not waiting for QA)

**Speed improvement:** 20-30% faster development cycle

#### 3. Better Quality

**Consistent standards enforced automatically:**

- All constraints tested
- All performance benchmarks met
- All edge cases covered
- Regression prevention

**Quality improvement:** 80% fewer bugs

#### 4. Cost Savings

**Bug cost by stage:**

```
Development (tests catch it):      $10 to fix
QA (manual testing finds it):      $100 to fix
Staging (found before production): $1,000 to fix
Production (customers find it):    $10,000+ to fix

ROI of testing: 100-1,000x
```

### What Should You Test?

#### Schema Changes

**Test that:**
- ✅ Tables created correctly with right columns
- ✅ Data types are correct
- ✅ Constraints work (NOT NULL, CHECK, UNIQUE)
- ✅ Indexes created and used
- ✅ Foreign keys enforce relationships
- ✅ Defaults apply correctly

**Example test:**
```sql
-- Test: Orders table has required constraints
CREATE PROCEDURE test_orders_table_constraints
AS
BEGIN
    -- Try to insert invalid data
    INSERT INTO orders (order_id) VALUES (1);
    -- Should fail due to NOT NULL constraint on customer_id
END
```

#### Data Migrations

**Test that:**
- ✅ All data migrated (row count matches)
- ✅ No data loss
- ✅ Transformations correct
- ✅ NULL handling correct
- ✅ Performance acceptable

**Example test:**
```sql
-- Test: All customer addresses migrated correctly
CREATE PROCEDURE test_address_migration
AS
BEGIN
    -- Count before
    DECLARE @before_count INT = (SELECT COUNT(*) FROM customers_old);

    -- Run migration
    EXEC migrate_customer_addresses;

    -- Count after
    DECLARE @after_count INT = (SELECT COUNT(*) FROM customers_new);

    -- Assert counts match
    IF @before_count != @after_count
        THROW 50000, 'Data loss in migration', 1;
END
```

#### Stored Procedures / Functions

**Test that:**
- ✅ Business logic correct
- ✅ Edge cases handled
- ✅ Error handling works
- ✅ Performance acceptable
- ✅ NULL handling correct

**Example test:**
```sql
-- Test: CalculateOrderTotal handles empty orders
CREATE PROCEDURE test_calculate_order_total_empty
AS
BEGIN
    DECLARE @total DECIMAL(10,2);

    -- Call function with non-existent order
    EXEC CalculateOrderTotal @order_id = 999, @total = @total OUTPUT;

    -- Assert returns 0 or NULL (not error)
    IF @total IS NULL OR @total = 0
        PRINT 'Pass';
    ELSE
        THROW 50000, 'Expected NULL or 0 for empty order', 1;
END
```

#### Application Integration

**Test that:**
- ✅ Application can connect
- ✅ Queries return expected data
- ✅ Transactions work correctly
- ✅ Concurrent access handled
- ✅ Connection pooling works

---

## Types of Database Tests

### 1. Unit Tests

**What:** Test individual database objects in isolation

**Test these objects:**
- Stored procedures
- Functions
- Triggers
- Views
- Constraints

**Characteristics:**
- Fast (< 1 second per test)
- Isolated (no dependencies)
- Automated
- Run on every commit

**Example:**
```sql
-- Unit test for stored procedure
CREATE PROCEDURE test_calculate_discount
AS
BEGIN
    DECLARE @discount DECIMAL(5,2);

    -- Test regular customer (10% discount)
    EXEC CalculateCustomerDiscount
        @customer_type = 'regular',
        @discount = @discount OUTPUT;

    IF @discount = 0.10
        PRINT 'Pass: Regular customer discount';
    ELSE
        THROW 50000, 'Wrong discount for regular customer', 1;
END
```

**When to use:**
- Test business logic in database
- Test calculations
- Test data validation rules
- Test complex SQL logic

**Benefit:** Catch logic errors before they reach production

### 2. Integration Tests

**What:** Test database with application code

**Test these interactions:**
- API endpoints that query database
- ORM mappings (Entity Framework, etc.)
- Transaction boundaries
- Connection management
- Data access layers

**Characteristics:**
- Medium speed (1-10 seconds)
- Tests real interactions
- Requires test database
- Run before deployment

**Example:**
```javascript
// Integration test (Node.js + Jest)
test('GET /orders/:id returns order with items', async () => {
    // Arrange: Create test data in database
    const testOrder = await db.orders.create({
        customer_id: 1,
        total: 100.00
    });

    // Act: Call API endpoint
    const response = await request(app).get(`/orders/${testOrder.id}`);

    // Assert: Verify response
    expect(response.status).toBe(200);
    expect(response.body.total).toBe(100.00);
});
```

**When to use:**
- Verify application and database work together
- Test realistic user scenarios
- Test complete workflows
- Before deploying application changes

**Benefit:** Catch integration issues before production

### 3. Performance Tests

**What:** Test database performance characteristics

**Test these metrics:**
- Query execution time
- Index effectiveness
- Concurrent user handling
- Large dataset performance
- Resource usage (CPU, memory, I/O)

**Characteristics:**
- Slower (10+ seconds)
- Requires production-like data
- Run before major deployments
- Establish baselines

**Example:**
```sql
-- Performance test
CREATE PROCEDURE test_order_search_performance
AS
BEGIN
    DECLARE @start_time DATETIME = GETDATE();

    -- Run query
    SELECT * FROM orders
    WHERE customer_id = 12345
    AND order_date > '2025-01-01';

    DECLARE @duration_ms INT = DATEDIFF(MILLISECOND, @start_time, GETDATE());

    -- Assert: Query completes in < 100ms
    IF @duration_ms > 100
        THROW 50000, 'Query too slow', 1;
    ELSE
        PRINT 'Pass: Query completed in ' + CAST(@duration_ms AS VARCHAR) + 'ms';
END
```

**When to use:**
- Before deploying schema changes
- After adding/removing indexes
- With production data volumes
- Before high-traffic events

**Benefit:** Avoid performance regressions in production

### 4. Data Quality Tests

**What:** Test data integrity and quality

**Test these qualities:**
- Referential integrity (foreign keys valid)
- Data consistency (no orphaned records)
- Business rule compliance (valid states, dates, etc.)
- No duplicate data (unique constraints enforced)
- Data completeness (required fields populated)

**Characteristics:**
- Run continuously in production
- Catch data quality issues
- Alert when quality degrades
- Preventive monitoring

**Example:**
```sql
-- Data quality test
CREATE PROCEDURE test_no_orphaned_orders
AS
BEGIN
    -- Find orders with no customer
    DECLARE @orphan_count INT = (
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    );

    -- Assert: No orphaned orders
    IF @orphan_count > 0
        THROW 50000, 'Found orphaned orders', 1;
    ELSE
        PRINT 'Pass: No orphaned orders';
END
```

**When to use:**
- After data migrations
- Continuously in production
- After schema changes
- Regular data audits

**Benefit:** Maintain high data quality over time

---

## Database Unit Testing

### Introduction to tSQLt Framework

**tSQLt** is the most popular unit testing framework for SQL Server:

**Features:**
- ✅ Free and open source
- ✅ Compatible with SQL Server 2005+
- ✅ Easy to use (like JUnit for SQL)
- ✅ Isolates tests with fakes
- ✅ Integrates with CI/CD
- ✅ Works with SSMS

**Website:** https://tsqlt.org

### Installing tSQLt

**Step 1: Download tSQLt**

```bash
# Download from https://tsqlt.org/downloads/
# Get tSQLt.class.sql (single file, ~1MB)
```

**Step 2: Create test database**

```sql
-- Don't install in production database!
CREATE DATABASE MyApp_Tests;
GO

USE MyApp_Tests;
GO
```

**Step 3: Execute tSQLt script**

```sql
-- In SSMS, open tSQLt.class.sql and execute
-- This creates tSQLt schema and procedures
```

**Step 4: Verify installation**

```sql
EXEC tSQLt.Info;

-- Expected output:
-- Version: Latest version info
-- ClrVersion: CLR version
```

**Step 5: Enable CLR (if needed)**

```sql
-- tSQLt uses CLR, may need to enable
EXEC sp_configure 'clr enabled', 1;
RECONFIGURE;
```

### Your First Database Test

Let's write a complete test from scratch.

**Scenario:** Test a stored procedure that calculates order totals

#### Step 1: Create the Procedure to Test

```sql
-- The procedure we want to test
CREATE OR ALTER PROCEDURE dbo.CalculateOrderTotal
    @OrderID INT,
    @Total DECIMAL(10,2) OUTPUT
AS
BEGIN
    SELECT @Total = SUM(Quantity * UnitPrice)
    FROM OrderItems
    WHERE OrderID = @OrderID;
END
GO
```

#### Step 2: Create Test Class

```sql
-- Organize tests into classes (like folders)
EXEC tSQLt.NewTestClass 'OrderTests';
GO
```

#### Step 3: Write the Test

```sql
CREATE OR ALTER PROCEDURE OrderTests.[test CalculateOrderTotal returns correct sum]
AS
BEGIN
    -- Arrange: Set up test data
    -- FakeTable creates isolated copy
    EXEC tSQLt.FakeTable 'dbo.OrderItems';

    -- Insert test data
    INSERT INTO dbo.OrderItems (OrderID, Quantity, UnitPrice)
    VALUES
        (1, 2, 10.00),  -- 2 × 10 = 20
        (1, 3, 5.00);   -- 3 × 5 = 15
    -- Expected total: 35.00

    -- Act: Execute procedure under test
    DECLARE @ActualTotal DECIMAL(10,2);
    EXEC dbo.CalculateOrderTotal
        @OrderID = 1,
        @Total = @ActualTotal OUTPUT;

    -- Assert: Verify result
    EXEC tSQLt.AssertEquals
        @Expected = 35.00,
        @Actual = @ActualTotal;
END
GO
```

#### Step 4: Run the Test

```sql
-- Run all tests in class
EXEC tSQLt.Run 'OrderTests';

-- Expected output:
-- [OrderTests].[test CalculateOrderTotal returns correct sum] passed
-- Test execution summary: 1 test(s) executed
--                         1 test(s) passed
--                         0 test(s) failed
```

**Success!** ✅ Your first database test works!

### Test Structure: Arrange-Act-Assert

Every good test follows the **AAA pattern:**

#### 1. Arrange: Set Up Test Data

```sql
-- Create isolated test environment
EXEC tSQLt.FakeTable 'dbo.Orders';
EXEC tSQLt.FakeTable 'dbo.OrderItems';

-- Insert known test data
INSERT INTO dbo.Orders (OrderID, CustomerID, OrderDate)
VALUES (1, 100, '2025-11-20');

INSERT INTO dbo.OrderItems (OrderID, ProductID, Quantity, UnitPrice)
VALUES
    (1, 1, 2, 10.00),
    (1, 2, 3, 5.00);
```

**Why fake tables?**
- Tests don't affect real data
- Each test starts with clean slate
- Tests can run in parallel
- Fast (in-memory)

#### 2. Act: Execute Code Under Test

```sql
-- Call the procedure or function you're testing
DECLARE @Result DECIMAL(10,2);
EXEC dbo.CalculateOrderTotal
    @OrderID = 1,
    @Total = @Result OUTPUT;
```

**Keep it simple:**
- One procedure call per test
- Clear what you're testing
- Easy to understand

#### 3. Assert: Verify Results

```sql
-- Check that result matches expectation
EXEC tSQLt.AssertEquals
    @Expected = 35.00,
    @Actual = @Result;
```

**If assertion fails:**
- Test fails with error message
- Shows expected vs actual
- Pinpoints the problem

### Common Assertions in tSQLt

```sql
-- 1. Assert Equals (most common)
EXEC tSQLt.AssertEquals
    @Expected = 100,
    @Actual = @ActualValue;

-- 2. Assert Not Equals
EXEC tSQLt.AssertNotEquals
    @Expected = NULL,
    @Actual = @ActualValue;

-- 3. Assert Equals String (case-sensitive)
EXEC tSQLt.AssertEqualsString
    @Expected = 'John',
    @Actual = @ActualName;

-- 4. Assert Result Set Matches
EXEC tSQLt.AssertEqualsTable
    @Expected = '#ExpectedResults',
    @Actual = '#ActualResults';

-- 5. Assert Table Is Empty
EXEC tSQLt.AssertEmptyTable
    @TableName = 'dbo.ErrorLog';

-- 6. Assert Object Exists
EXEC tSQLt.AssertObjectExists
    @ObjectName = 'dbo.Orders';

-- 7. Fail Test with Message
EXEC tSQLt.Fail 'Custom failure message explaining what went wrong';
```

### Testing Edge Cases

**Always test:**
- ✅ Happy path (normal case that should work)
- ✅ Empty data (no records)
- ✅ NULL values (missing data)
- ✅ Boundary values (min, max, zero)
- ✅ Error conditions (invalid input)

#### Example: Testing NULL Handling

```sql
CREATE OR ALTER PROCEDURE OrderTests.[test CalculateOrderTotal handles order with no items]
AS
BEGIN
    -- Arrange: Order exists but has no items
    EXEC tSQLt.FakeTable 'dbo.OrderItems';
    -- Intentionally insert NO data

    -- Act: Calculate total for empty order
    DECLARE @Total DECIMAL(10,2);
    EXEC dbo.CalculateOrderTotal
        @OrderID = 999,
        @Total = @Total OUTPUT;

    -- Assert: Should return NULL (not crash!)
    EXEC tSQLt.AssertEquals
        @Expected = NULL,
        @Actual = @Total;
END
GO
```

#### Example: Testing Boundary Values

```sql
CREATE OR ALTER PROCEDURE OrderTests.[test CalculateOrderTotal handles zero quantity]
AS
BEGIN
    -- Arrange: Item with quantity = 0
    EXEC tSQLt.FakeTable 'dbo.OrderItems';

    INSERT INTO dbo.OrderItems (OrderID, Quantity, UnitPrice)
    VALUES (1, 0, 10.00);  -- 0 × 10 = 0

    -- Act
    DECLARE @Total DECIMAL(10,2);
    EXEC dbo.CalculateOrderTotal
        @OrderID = 1,
        @Total = @Total OUTPUT;

    -- Assert: Total should be 0
    EXEC tSQLt.AssertEquals
        @Expected = 0.00,
        @Actual = @Total;
END
GO
```

#### Example: Testing Error Handling

```sql
CREATE OR ALTER PROCEDURE OrderTests.[test CalculateOrderTotal handles negative quantity]
AS
BEGIN
    -- Arrange: Invalid data (negative quantity)
    EXEC tSQLt.FakeTable 'dbo.OrderItems';

    INSERT INTO dbo.OrderItems (OrderID, Quantity, UnitPrice)
    VALUES (1, -5, 10.00);  -- ❌ Should not be negative

    -- Act & Assert: Should raise error
    EXEC tSQLt.ExpectException
        @ExpectedMessage = 'Quantity cannot be negative';

    DECLARE @Total DECIMAL(10,2);
    EXEC dbo.CalculateOrderTotal
        @OrderID = 1,
        @Total = @Total OUTPUT;
END
GO
```

### Organizing Tests

**Best practices:**

1. **One test class per database object**
```sql
-- Tests for Orders procedures
EXEC tSQLt.NewTestClass 'OrderTests';

-- Tests for Customer procedures
EXEC tSQLt.NewTestClass 'CustomerTests';

-- Tests for Payment procedures
EXEC tSQLt.NewTestClass 'PaymentTests';
```

2. **Descriptive test names**
```sql
-- ✅ Good: Clear what it tests
CREATE PROCEDURE OrderTests.[test CalculateOrderTotal returns correct sum for multiple items]

-- ❌ Bad: Unclear what it tests
CREATE PROCEDURE OrderTests.[test1]
```

3. **One assertion per test**
```sql
-- ✅ Good: Tests one thing
CREATE PROCEDURE OrderTests.[test order total includes all items]
CREATE PROCEDURE OrderTests.[test order total excludes canceled items]

-- ❌ Bad: Tests multiple things
CREATE PROCEDURE OrderTests.[test order total calculation]
-- ... tests multiple scenarios ...
```

---

## Next Steps

This document provides the foundation for database testing. The remaining chapters will be completed in **Phase 1B**:

### Coming in Phase 1B:
- **Integration Testing** - Test database with application code
- **Performance Testing** - Ensure database changes don't slow things down
- **Data Quality Testing** - Maintain data integrity
- **Testing in CI/CD** - Run tests in GitHub Actions automatically
- **Test Data Management** - Create and manage test datasets
- **Tools and Frameworks** - Complete tool comparison
- **Best Practices** - Testing strategies and guidelines

### What You Can Do Now:

1. **Install tSQLt** in a test database
2. **Write your first test** for an existing stored procedure
3. **Practice the AAA pattern** (Arrange-Act-Assert)
4. **Test edge cases** (NULL, empty, boundaries)
5. **Run tests locally** before committing changes

### Resources:

- **tSQLt Website:** https://tsqlt.org
- **tSQLt Documentation:** https://tsqlt.org/user-guide/
- **Example Tests:** https://github.com/tSQLt-org/tSQLt

---

**Document Status:** Phase 1A Complete (Core chapters)
**Next Update:** Phase 1B (Complete remaining chapters)
**Date:** November 20, 2025
