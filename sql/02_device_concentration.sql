-- ============================================================
-- 02_device_concentration.sql
-- Device concentration analysis: hunt for mule-ring patterns.
--
-- STRUCTURAL FINDING — why this dataset produces a NULL result:
--
--   Cardinality diagnostic reveals:
--     • 647 unique customers across 100,000 transactions
--     • 647 unique devices — IDENTICAL to customer count
--     • 99,998 unique IPs across 100,000 transactions
--
--   This means:
--     • Device_ID is 1:1 with Customer_ID by construction. Every customer
--       uses exactly one device; every device belongs to exactly one
--       customer. Device_ID is a disguised Customer_ID, not an
--       independent network signal.
--     • IP_Address is essentially unique per transaction (2 duplicate
--       occurrences in 100,000 rows). IP is random noise, not a
--       behavioral feature.
--
--   Therefore mule-ring detection has no testable signal on this
--   dataset. On real UPI data, a device serving 3+ customers is a
--   strong red flag and this query is a first-pass mule-ring filter.
-- ============================================================


-- ============================================================
-- STEP 0: Cardinality — structural picture of the dataset
-- ============================================================
-- OBSERVED: 100000 | 647 | 647 | 99998 | 100000
-- Customers = Devices exactly. IPs essentially unique.

SELECT
    COUNT(DISTINCT Transaction_ID) AS unique_transactions,
    COUNT(DISTINCT Customer_ID)    AS unique_customers,
    COUNT(DISTINCT Device_ID)      AS unique_devices,
    COUNT(DISTINCT IP_Address)     AS unique_ips,
    COUNT(*)                       AS total_rows
FROM transactions;


-- ============================================================
-- STEP 1: Distribution — shape of the device-to-customer relationship
-- ============================================================
-- OBSERVED: 647 devices, all in bucket 1. Buckets 2-5 empty.

WITH device_customer_count AS (
    SELECT
        Device_ID,
        COUNT(DISTINCT Customer_ID) AS unique_customers
    FROM transactions
    GROUP BY Device_ID
)
SELECT
    CASE
        WHEN unique_customers = 1   THEN '1. exactly 1 customer'
        WHEN unique_customers = 2   THEN '2. 2 customers'
        WHEN unique_customers <= 5  THEN '3. 3-5 customers'
        WHEN unique_customers <= 10 THEN '4. 6-10 customers'
        ELSE                             '5. over 10 customers'
    END AS device_bucket,
    COUNT(*) AS device_count
FROM device_customer_count
GROUP BY device_bucket
ORDER BY device_bucket;


-- ============================================================
-- STEP 2: Concentration — devices with >1 customer
-- ============================================================
-- OBSERVED: zero rows. No device serves more than one customer.

SELECT
    Device_ID,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    COUNT(*)                    AS total_transactions,
    SUM(fraud)                  AS frauds,
    ROUND(1.0 * SUM(fraud) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY Device_ID
HAVING COUNT(DISTINCT Customer_ID) > 1
ORDER BY unique_customers DESC, fraud_rate DESC
LIMIT 20;


-- ============================================================
-- STEP 3: Production concentration — devices with >10 customers
-- ============================================================
-- OBSERVED: zero rows (subsumed by STEP 2).
-- On real UPI data, this is the standard mule-ring review threshold.

SELECT
    Device_ID,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    COUNT(*)                    AS total_transactions,
    SUM(fraud)                  AS frauds,
    ROUND(1.0 * SUM(fraud) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY Device_ID
HAVING COUNT(DISTINCT Customer_ID) > 10
ORDER BY unique_customers DESC, fraud_rate DESC
LIMIT 20;