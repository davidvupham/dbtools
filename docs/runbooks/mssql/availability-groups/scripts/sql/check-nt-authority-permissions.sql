-- Verify required permissions
SELECT
    p.name AS login_name,
    sp.permission_name,
    sp.state_desc
FROM sys.server_permissions sp
JOIN sys.server_principals p ON sp.grantee_principal_id = p.principal_id
WHERE p.name = 'NT AUTHORITY\SYSTEM';

-- Grant if missing
-- GRANT VIEW SERVER STATE TO [NT AUTHORITY\SYSTEM];
-- GRANT CONNECT SQL TO [NT AUTHORITY\SYSTEM];
