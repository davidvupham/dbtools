-- Check certificate details
SELECT
    name,
    certificate_id,
    start_date,
    expiry_date,
    DATEDIFF(day, GETDATE(), expiry_date) AS days_until_expiry
FROM sys.certificates
WHERE name LIKE '%hadr%' OR name LIKE '%mirror%' OR name LIKE '%endpoint%';
