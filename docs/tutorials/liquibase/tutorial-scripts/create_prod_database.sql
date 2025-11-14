-- Create production database
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbprd')
CREATE DATABASE testdbprd;
