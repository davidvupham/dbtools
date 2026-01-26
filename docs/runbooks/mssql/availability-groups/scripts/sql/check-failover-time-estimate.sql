-- Calculate estimated failover time based on redo queue
SELECT
    ar.replica_server_name,
    adc.database_name,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.redo_rate / 1024.0 AS redo_rate_kbps,
    CASE
        WHEN drs.redo_rate > 0
        THEN CAST(drs.redo_queue_size / drs.redo_rate AS DECIMAL(10,2))
        ELSE -1
    END AS estimated_redo_seconds,
    CASE
        WHEN drs.redo_rate > 0
        THEN CAST((drs.redo_queue_size / drs.redo_rate) / 60.0 AS DECIMAL(10,2))
        ELSE -1
    END AS estimated_redo_minutes
FROM sys.dm_hadr_database_replica_states drs
INNER JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
INNER JOIN sys.availability_databases_cluster adc ON drs.group_database_id = adc.group_database_id
WHERE drs.is_local = 0  -- Remote replicas only
ORDER BY drs.redo_queue_size DESC;
