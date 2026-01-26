-- Monitor queue sizes
SELECT
    ar.replica_server_name,
    db.name AS database_name,
    drs.log_send_queue_size / 1024.0 AS send_queue_mb,
    drs.redo_queue_size / 1024.0 AS redo_queue_mb,
    drs.log_send_rate / 1024.0 AS send_rate_kbps,
    drs.redo_rate / 1024.0 AS redo_rate_kbps,
    CASE
        WHEN drs.redo_rate > 0
        THEN drs.redo_queue_size / drs.redo_rate
        ELSE 0
    END AS estimated_redo_time_seconds
FROM sys.dm_hadr_database_replica_states drs
JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
JOIN sys.databases db ON drs.database_id = db.database_id
ORDER BY drs.redo_queue_size DESC;
