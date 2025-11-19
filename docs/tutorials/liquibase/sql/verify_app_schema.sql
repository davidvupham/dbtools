SELECT 'dev' AS env,
    s.name AS schema_name
FROM testdbdev.sys.schemas s
WHERE s.name = 'app'
UNION ALL
SELECT 'stage' AS env,
    s.name AS schema_name
FROM testdbstg.sys.schemas s
WHERE s.name = 'app'
UNION ALL
SELECT 'prod' AS env,
    s.name AS schema_name
FROM testdbprd.sys.schemas s
WHERE s.name = 'app';
