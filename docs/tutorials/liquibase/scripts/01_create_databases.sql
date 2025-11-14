-- Create three databases for the tutorial
-- testdbdev: Development environment
-- testdbstg: Staging environment
-- testdbprd: Production environment

-- Create development database
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbdev')
CREATE DATABASE testdbdev;

-- Create staging database
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbstg')
CREATE DATABASE testdbstg;

-- Create production database
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'testdbprd')
CREATE DATABASE testdbprd;
