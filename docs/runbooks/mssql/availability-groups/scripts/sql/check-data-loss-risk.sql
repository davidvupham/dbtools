-- Calculate potential data loss based on send queue
SELECT
    ar.replica_server_name,
    adc.database_name,
    ar.availability_mode_desc,
    drs.log_send_queue_size / 1024.0 AS send_queue_mb,
    drs.last_sent_time,
    drs.last_hardened_time,
    DATEDIFF(SECOND, drs.last_hardened_time, GETDATE()) AS seconds_behind,
    CASE
        WHEN ar.availability_mode_desc = 'SYNCHRONOUS_COMMIT'
            AND drs.synchronization_state_desc = 'SYNCHRONIZED'
        THEN 'No data loss expected'
        ELSE 'Potential data loss: ' +
            CAST(drs.log_send_queue_size / 1024.0 AS VARCHAR(20)) + ' MB'
    END AS rpo_assessment
FROM sys.dm_hadr_database_replica_states drs
INNER JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
INNER JOIN sys.availability_databases_cluster adc ON drs.group_database_id = adc.group_database_id
WHERE drs.is_local = 0
ORDER BY drs.log_send_queue_size DESC;
