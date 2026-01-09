-- Create orderdb database for staging environment
-- Run this against mssql_stg container
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'orderdb'
) CREATE DATABASE orderdb;
GO
