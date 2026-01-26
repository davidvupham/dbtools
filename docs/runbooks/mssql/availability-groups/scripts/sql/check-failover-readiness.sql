-- Verify all databases are failover-ready
SELECT
    ar.replica_server_name,
    drcs.database_name,
    drcs.is_failover_ready,
    drs.synchronization_state_desc
FROM sys.dm_hadr_database_replica_cluster_states drcs
JOIN sys.dm_hadr_database_replica_states drs
    ON drcs.replica_id = drs.replica_id AND drcs.group_database_id = drs.group_database_id
JOIN sys.availability_replicas ar ON drcs.replica_id = ar.replica_id
ORDER BY ar.replica_server_name, drcs.database_name;
