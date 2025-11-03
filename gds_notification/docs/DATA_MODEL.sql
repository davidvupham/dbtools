/*
 SQL data model for GDS Notification Service PoC.
 This file contains table definitions and a sample stored procedure that returns recipients
 for an alert. The stored proc is intended as a suggested implementation for SQL Server.
*/

-- Table: database_instances
CREATE TABLE IF NOT EXISTS dbo.database_instances (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    environment NVARCHAR(100) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: recipients
CREATE TABLE IF NOT EXISTS dbo.recipients (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(256) NOT NULL,
    name NVARCHAR(256) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: recipient_groups
CREATE TABLE IF NOT EXISTS dbo.recipient_groups (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(1000) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: recipient_group_members
CREATE TABLE IF NOT EXISTS dbo.recipient_group_members (
    group_id INT NOT NULL REFERENCES dbo.recipient_groups(id),
    recipient_id INT NOT NULL REFERENCES dbo.recipients(id),
    PRIMARY KEY(group_id, recipient_id)
);

-- Table: alerts (alert definitions)
CREATE TABLE IF NOT EXISTS dbo.alert_definitions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    alert_name NVARCHAR(200) NOT NULL,
    description NVARCHAR(1000) NULL,
    default_group_id INT NULL REFERENCES dbo.recipient_groups(id),
    severity INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: alert_subscriptions (which groups/recipients get which alerts for which DB instances)
CREATE TABLE IF NOT EXISTS dbo.alert_subscriptions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    alert_definition_id INT NOT NULL REFERENCES dbo.alert_definitions(id),
    db_instance_id INT NOT NULL REFERENCES dbo.database_instances(id),
    recipient_group_id INT NULL REFERENCES dbo.recipient_groups(id),
    recipient_id INT NULL REFERENCES dbo.recipients(id),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: blackout_periods (time ranges where alerts are suppressed)
CREATE TABLE IF NOT EXISTS dbo.blackout_periods (
    id INT IDENTITY(1,1) PRIMARY KEY,
    target_type NVARCHAR(50) NOT NULL, -- 'group' | 'recipient' | 'db_instance'
    target_id INT NOT NULL, -- id in corresponding table
    start_utc DATETIME2 NOT NULL,
    end_utc DATETIME2 NOT NULL,
    reason NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Table: alert_events (persisted incoming alerts)
CREATE TABLE IF NOT EXISTS dbo.alert_events (
    id INT IDENTITY(1,1) PRIMARY KEY,
    idempotency_id NVARCHAR(200) NOT NULL UNIQUE,
    alert_name NVARCHAR(200) NOT NULL,
    db_instance_id INT NULL REFERENCES dbo.database_instances(id),
    subject NVARCHAR(1000) NULL,
    body_text NVARCHAR(MAX) NULL,
    body_html NVARCHAR(MAX) NULL,
    raw_headers NVARCHAR(MAX) NULL,
    received_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    status NVARCHAR(50) NOT NULL DEFAULT 'queued'
);

-- Table: recipient_send_status
CREATE TABLE IF NOT EXISTS dbo.recipient_send_status (
    id INT IDENTITY(1,1) PRIMARY KEY,
    alert_event_id INT NOT NULL REFERENCES dbo.alert_events(id),
    recipient_id INT NOT NULL REFERENCES dbo.recipients(id),
    attempt_count INT NOT NULL DEFAULT 0,
    last_attempt_at DATETIME2 NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'pending', -- pending|sent|failed|blackout
    last_error NVARCHAR(2000) NULL
);

-- Sample stored procedure: GetRecipientsForAlert
-- This stored procedure returns recipients (recipient id, email, name) for a given alert name and db instance.
-- It demonstrates the expected signature and output shape for the notification service.

IF OBJECT_ID('dbo.GetRecipientsForAlert', 'P') IS NOT NULL
    DROP PROCEDURE dbo.GetRecipientsForAlert;
GO

CREATE PROCEDURE dbo.GetRecipientsForAlert
    @AlertName NVARCHAR(200),
    @DbInstanceId INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Strategy:
    -- 1. Find alert_definition by name
    -- 2. Find active subscriptions for that alert and db_instance
    -- 3. Return recipients via the groups or explicit recipients

    SELECT DISTINCT r.id AS RecipientId,
           r.email AS RecipientEmail,
           r.name AS RecipientName,
           'email' AS DeliveryChannel
    FROM dbo.alert_definitions ad
    INNER JOIN dbo.alert_subscriptions s ON s.alert_definition_id = ad.id
    LEFT JOIN dbo.recipient_groups rg ON s.recipient_group_id = rg.id
    LEFT JOIN dbo.recipient_group_members rgm ON rg.id = rgm.group_id
    LEFT JOIN dbo.recipients r ON r.id = COALESCE(s.recipient_id, rgm.recipient_id)
    WHERE ad.alert_name = @AlertName
      AND s.db_instance_id = @DbInstanceId
      AND s.is_active = 1;
END;
GO

-- NOTE: This is a minimal example. Production systems should consider performance (indexes),
-- timezone-aware blackout calculations, and shaped outputs (e.g., return group id, recipient preferences).
