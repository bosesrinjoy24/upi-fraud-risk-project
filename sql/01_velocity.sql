-- ============================================================
-- 01_velocity.sql
-- Transaction velocity analysis.
-- Fixes two SQLite date traps:
--   1. Lexicographical sorting of DD/MM/YY strings.
--   2. julianday() returning NULL for two-digit years.
-- ============================================================

WITH clean AS (
    SELECT
        Transaction_ID,
        Customer_ID,
        fraud,
        amount,
        -- Prepend '20' to the year to satisfy SQLite's ISO 8601 requirement
        '20' || substr(Date, 7, 2) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2)
            || ' ' ||
        CASE
            WHEN substr(Time, -2) = 'PM' AND CAST(substr(Time, 1, 2) AS INTEGER) < 12
                THEN printf('%02d', CAST(substr(Time, 1, 2) AS INTEGER) + 12) || substr(Time, 3, 6)
            WHEN substr(Time, -2) = 'AM' AND substr(Time, 1, 2) = '12'
                THEN '00' || substr(Time, 3, 6)
            ELSE substr(Time, 1, 8)
        END AS txn_datetime
    FROM transactions
),
velocity AS (
    SELECT
        Customer_ID,
        txn_datetime,
        fraud,
        LAG(txn_datetime) OVER (
            PARTITION BY Customer_ID 
            ORDER BY txn_datetime, Transaction_ID -- Tie-breaker for identical timestamps
        ) AS prev_txn_time,
        ROUND(
            (julianday(txn_datetime) - julianday(LAG(txn_datetime) OVER (PARTITION BY Customer_ID ORDER BY txn_datetime, Transaction_ID))) * 86400,
            0
        ) AS seconds_since_prev
    FROM clean
)
SELECT
    CASE
        WHEN seconds_since_prev < 60       THEN '1. under 1 minute'
        WHEN seconds_since_prev < 3600     THEN '2. 1-60 minutes'
        WHEN seconds_since_prev < 86400    THEN '3. 1-24 hours'
        ELSE                                    '4. over 1 day'
    END AS gap_bucket,
    COUNT(*) AS total,
    SUM(fraud) AS frauds,
    ROUND(1.0 * SUM(fraud) / COUNT(*), 4) AS fraud_rate
FROM velocity
WHERE seconds_since_prev IS NOT NULL
GROUP BY gap_bucket
ORDER BY gap_bucket;