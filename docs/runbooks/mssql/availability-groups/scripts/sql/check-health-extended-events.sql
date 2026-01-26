-- Check for health events (run on primary)
SELECT
    XEL.object_name AS event_name,
    XEL.event_data.value('(event/@timestamp)[1]', 'datetime2') AS event_time,
    XEL.event_data.value('(event/data[@name="availability_group_name"]/value)[1]', 'varchar(50)') AS ag_name,
    XEL.event_data.value('(event/data[@name="error_number"]/value)[1]', 'int') AS error_number,
    XEL.event_data.value('(event/data[@name="message"]/value)[1]', 'varchar(max)') AS message
FROM (
    SELECT object_name, CAST(event_data AS XML) AS event_data
    FROM sys.fn_xe_file_target_read_file(
        'AlwaysOn_health*.xel', NULL, NULL, NULL
    )
) XEL
WHERE XEL.object_name IN ('error_reported', 'availability_replica_state_change',
    'availability_group_lease_expired', 'alwayson_ddl_executed')
ORDER BY event_time DESC;
