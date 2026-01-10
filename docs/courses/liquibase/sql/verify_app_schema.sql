-- Verify app schema exists in orderdb
-- Run this against each container (mssql_dev, mssql_stg, mssql_prd)
USE orderdb;
GO
SELECT @@SERVERNAME AS instance_name,
    DB_NAME() AS database_name,
    s.name AS schema_name
FROM sys.schemas s
WHERE s.name = 'app';
