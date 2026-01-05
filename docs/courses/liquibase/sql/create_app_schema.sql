USE testdbdev;
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'app'
) EXEC('CREATE SCHEMA app');
PRINT 'Created app schema in testdbdev';
GO
USE testdbstg;
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'app'
) EXEC('CREATE SCHEMA app');
PRINT 'Created app schema in testdbstg';
GO
USE testdbprd;
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'app'
) EXEC('CREATE SCHEMA app');
PRINT 'Created app schema in testdbprd';
GO
SELECT 'Schema creation complete in all three databases.' AS Result;
