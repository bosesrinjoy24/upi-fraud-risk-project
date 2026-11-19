-- ============================================================
-- 02_device_concentration.sql
-- Investigates device sharing and IP uniqueness.
-- ============================================================

-- 1. Customers per device (Are devices shared across identities?)
-- Note: No arbitrary "industry threshold" is applied. We simply order by highest count.
SELECT 
    Device_ID, 
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    COUNT(*) AS total_transactions,
    SUM(fraud) AS total_frauds,
    ROUND(1.0 * SUM(fraud) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY Device_ID
ORDER BY unique_customers DESC
LIMIT 10;

-- 2. Devices per customer (Does a single customer use multiple devices?)
SELECT 
    Customer_ID, 
    COUNT(DISTINCT Device_ID) AS unique_devices
FROM transactions
GROUP BY Customer_ID
ORDER BY unique_devices DESC
LIMIT 10;

-- 3. IP Address Analysis
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT IP_Address) AS unique_ips,
    COUNT(*) - COUNT(DISTINCT IP_Address) AS duplicate_ips
FROM transactions;

-- 4. Repeat IP sharing across different customers
SELECT 
    IP_Address, 
    COUNT(DISTINCT Customer_ID) AS unique_customers
FROM transactions
GROUP BY IP_Address
HAVING COUNT(DISTINCT Customer_ID) > 1
ORDER BY unique_customers DESC
LIMIT 10;