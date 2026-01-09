-- Verify orderdb database exists
-- Run this against each container (mssql_dev, mssql_stg, mssql_prd)
SELECT name,
    database_id,
    create_date
FROM sys.databases
WHERE name = 'orderdb'
ORDER BY name;
