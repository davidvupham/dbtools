-- Create staging database
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'testdbstg'
) CREATE DATABASE testdbstg;
