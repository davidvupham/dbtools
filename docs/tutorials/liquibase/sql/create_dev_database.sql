-- Create development database
IF NOT EXISTS (
    SELECT 1
    FROM sys.databases
    WHERE name = 'testdbdev'
) CREATE DATABASE testdbdev;
