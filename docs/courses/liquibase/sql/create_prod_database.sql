-- Create orderdb database for production environment
-- Run this against mssql_prd container
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'orderdb'
) CREATE DATABASE orderdb;
GO
