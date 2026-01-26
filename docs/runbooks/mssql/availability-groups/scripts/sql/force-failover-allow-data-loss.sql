-- Perform forced failover if needed (WITH DATA LOSS)
-- Only use this after confirming primary is permanently unavailable
ALTER AVAILABILITY GROUP [AGName] FORCE_FAILOVER_ALLOW_DATA_LOSS;
