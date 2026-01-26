-- Check flow control delays (run on primary)
SELECT
    ar.replica_server_name,
    fc.database_name,
    fc.flow_control_active,
    fc.flow_control_send_wait_ms
FROM sys.dm_hadr_database_replica_states drs
CROSS APPLY sys.fn_hadr_database_flow_control_info(drs.database_id) fc
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id;
