USE testdbdev;
-- Note: This script assumes the 'app' schema already exists
-- Liquibase does not manage schema creation - schemas must be created separately
-- Step 1: Create customer table
IF NOT EXISTS (
    SELECT 1
    FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[app].[customer]')
        AND type = 'U'
) BEGIN CREATE TABLE app.customer (
    customer_id INT IDENTITY(1, 1) CONSTRAINT PK_customer PRIMARY KEY,
    full_name NVARCHAR(200) NOT NULL,
    email NVARCHAR(320) NULL,
    phone_number NVARCHAR(20) NULL,
    created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_customer_email UNIQUE (email)
);
-- Add index for name lookups
CREATE NONCLUSTERED INDEX IX_customer_name ON app.customer(full_name);
PRINT 'Created table app.customer with indexes';
END -- Step 2: Create view
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL DROP VIEW app.v_customer_basic;
GO
CREATE VIEW app.v_customer_basic AS
SELECT customer_id,
    full_name,
    email,
    phone_number,
    created_at
FROM app.customer;
GO
PRINT 'Created view app.v_customer_basic';
-- Step 3: Insert sample data
INSERT INTO app.customer (full_name, email, phone_number)
VALUES (
        N'Alice Anderson',
        N'alice@example.com',
        N'555-0001'
    ),
    (N'Bob Brown', N'bob@example.com', N'555-0002'),
    (N'Carol Chen', N'carol@example.com', NULL);
SELECT 'Setup complete. Created table, view, and sample data in app schema.' AS Result;
