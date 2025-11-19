-- Verify all three databases exist
SELECT name,
    database_id,
    create_date
FROM sys.databases
WHERE name IN ('testdbdev', 'testdbstg', 'testdbprd')
ORDER BY name;
