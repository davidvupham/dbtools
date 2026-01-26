-- Check endpoint status on all replicas
SELECT
    name,
    protocol_desc,
    type_desc,
    state_desc,
    port,
    ip_address,
    encryption_algorithm_desc
FROM sys.tcp_endpoints
WHERE type_desc = 'DATABASE_MIRRORING';

-- Check endpoint permissions
SELECT
    spe.class_desc,
    spe.permission_name,
    spe.state_desc,
    sp.name AS principal_name
FROM sys.server_permissions spe
JOIN sys.server_principals sp ON spe.grantee_principal_id = sp.principal_id
WHERE spe.class = 105; -- ENDPOINT class
