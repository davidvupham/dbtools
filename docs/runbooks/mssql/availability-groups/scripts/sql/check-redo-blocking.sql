-- Check for blocking on secondary (run on secondary)
SELECT
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type IN ('HADR_SYNC_COMMIT', 'HADR_DATABASE_FLOW_CONTROL',
    'HADR_LOG_SEND', 'HADR_TRANSPORT_RECV', 'PARALLEL_REDO_WORKER_WAIT_WORK')
ORDER BY wait_time_ms DESC;
