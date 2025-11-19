USE testdbdev;
-- Step 1: Create schema
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'app'
) EXEC('CREATE SCHEMA app');
-- Step 2: Create customer table
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
    created_at DATETIME2(3) NOT NULL CONSTRAINT DF_customer_created_at DEFAULT (SYSUTCDATETIME())
);
PRINT 'Created table app.customer';
END -- Step 3: Create view
IF OBJECT_ID(N'app.v_customer_basic', N'V') IS NOT NULL DROP VIEW app.v_customer_basic;
GO CREATE VIEW app.v_customer_basic AS
SELECT customer_id,
    full_name,
    email,
    created_at
FROM app.customer;
GO PRINT 'Created view app.v_customer_basic';
-- Step 4: Create stored procedure
IF OBJECT_ID(N'app.usp_add_customer', N'P') IS NOT NULL DROP PROCEDURE app.usp_add_customer;
GO CREATE PROCEDURE app.usp_add_customer @full_name NVARCHAR(200),
    @email NVARCHAR(320) = NULL AS BEGIN
SET NOCOUNT ON;
INSERT INTO app.customer (full_name, email)
VALUES (@full_name, @email);
SELECT SCOPE_IDENTITY() AS customer_id;
END;
GO PRINT 'Created procedure app.usp_add_customer';
-- Step 5: Create function
IF OBJECT_ID(N'app.fn_mask_email', N 'FN') IS NOT NULL DROP FUNCTION app.fn_mask_email;
GO CREATE FUNCTION app.fn_mask_email (@email NVARCHAR(320)) RETURNS NVARCHAR(320) AS BEGIN IF @email IS NULL RETURN NULL;
DECLARE @at INT = CHARINDEX('@', @email);
IF @at <= 1 RETURN @email;
RETURN CONCAT(
    LEFT(@email, 1),
    '***',
    SUBSTRING(@email, @at, LEN(@email))
);
END;
GO PRINT 'Created function app.fn_mask_email';
-- Step 6: Insert sample data
INSERT INTO app.customer (full_name, email, phone_number)
VALUES (
        N'Alice Anderson',
        N'alice@example.com',
        N'555-0001'
    ),
    (N'Bob Brown', N'bob@example.com', N'555-0002'),
    (N'Carol Chen', N'carol@example.com', NULL);
SELECT 'Setup complete. Created schema, table, view, procedure, function, and sample data.' AS Result;
