-- Create app schema in orderdb database
-- Run this against each container (mssql_dev, mssql_stg, mssql_prd)
USE orderdb;
GO
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'app'
) EXEC('CREATE SCHEMA app');
GO
PRINT 'Created app schema in orderdb';
GO
SELECT 'Schema creation complete.' AS Result;
