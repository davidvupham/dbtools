-- Database-level sync status
SELECT
    ag.name AS ag_name,
    ar.replica_server_name,
    db.name AS database_name,
    drs.synchronization_state_desc,
    drs.synchronization_health_desc,
    drs.is_suspended,
    drs.suspend_reason_desc,
    drs.log_send_queue_size / 1024.0 AS log_send_queue_mb,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.last_hardened_time,
    drs.last_redone_time
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_database_replica_states drs ON ar.replica_id = drs.replica_id
JOIN sys.databases db ON drs.database_id = db.database_id
ORDER BY ag.name, ar.replica_server_name, db.name;
