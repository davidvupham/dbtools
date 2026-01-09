-- Create orderdb database for each environment
-- Uses a single database per container (mssql_dev, mssql_stg, mssql_prd)
-- Each container hosts its own orderdb instance

-- Create orderdb database (idempotent)
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'orderdb'
) CREATE DATABASE orderdb;
GO
