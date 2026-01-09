-- Create orderdb database for development environment
-- Run this against mssql_dev container
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'orderdb'
) CREATE DATABASE orderdb;
GO
