-- ============================================================
-- 01_velocity.sql
-- Velocity analysis: time gaps between successive transactions per customer.
--
-- CRITICAL: Date and Time are TEXT in DD/MM/YY and HH:MM:SS AM/PM format.
-- Two bugs lie in wait if you order by the raw strings:
--
-- Bug 1 — Lexicographic trap: SQLite compares text character by character.
--         '02/07/23' sorts before '12/02/22' because '0' < '1', even though
--         July 2023 is AFTER Feb 2022. Naive ORDER BY Date sorts wrong.
--
-- Bug 2 — julianday NULL trap: julianday() requires 4-digit years (ISO 8601).
--         julianday('22-02-12') returns NULL. Must prepend '20' to the year
--         before passing to julianday(), otherwise all gap calculations are
--         silently NULL and aggregates return empty.
--
-- Both bugs are fixed below. Always normalize to ISO 8601 (YYYY-MM-DD)
-- with 4-digit years at the earliest stage of any date pipeline.
-- ============================================================


-- ============================================================
-- STEP 1: Diagnostic — prove the lexicographic trap on real data
-- ============================================================
-- Returns customers whose lexicographically-smallest Date is NOT their
-- chronologically-earliest date. Any row here proves string sort is broken.

WITH normalized AS (
    SELECT
        Customer_ID,
        Date,
        substr(Date, 7, 2) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2) AS iso_date
    FROM transactions
)
SELECT
    t.Customer_ID,
    t.Date        AS lex_first_date,
    t.iso_date    AS its_real_date,
    (SELECT MIN(iso_date) FROM normalized WHERE Customer_ID = t.Customer_ID) AS true_earliest
FROM normalized t
WHERE t.Date = (SELECT MIN(Date) FROM normalized WHERE Customer_ID = t.Customer_ID)
  AND t.iso_date <> (SELECT MIN(iso_date) FROM normalized WHERE Customer_ID = t.Customer_ID)
LIMIT 10;


-- ============================================================
-- STEP 2: Velocity detail — 20 fastest-succession transactions
-- ============================================================
-- Shows the individual transactions with gaps under 60 seconds. The
-- fraud column tells you whether rapid succession correlates with fraud.

WITH clean AS (
    SELECT
        Customer_ID,
        fraud,
        amount,
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
        amount,
        LAG(txn_datetime) OVER (PARTITION BY Customer_ID ORDER BY txn_datetime) AS prev_txn_time,
        ROUND(
            (julianday(txn_datetime) - julianday(LAG(txn_datetime) OVER (PARTITION BY Customer_ID ORDER BY txn_datetime))) * 86400,
            0
        ) AS seconds_since_prev
    FROM clean
)
SELECT
    Customer_ID,
    txn_datetime,
    prev_txn_time,
    seconds_since_prev,
    fraud,
    amount
FROM velocity
WHERE seconds_since_prev IS NOT NULL
  AND seconds_since_prev < 60
ORDER BY seconds_since_prev ASC
LIMIT 20;


-- ============================================================
-- STEP 3: Velocity aggregate — fraud rate by gap bucket
-- ============================================================
-- The payload. Answers: does transaction velocity predict fraud?
-- Baseline fraud rate is 0.23986. Compare each bucket to it.
--   Bucket >> 0.23986  -> velocity is a strong signal
--   Bucket ~= 0.23986  -> velocity is neutral
--   Bucket << 0.23986  -> velocity is a signal in reverse

WITH clean AS (
    SELECT
        Customer_ID,
        fraud,
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
        fraud,
        (julianday(txn_datetime) - julianday(LAG(txn_datetime) OVER (PARTITION BY Customer_ID ORDER BY txn_datetime))) * 86400 AS gap_seconds
    FROM clean
)
SELECT
    CASE
        WHEN gap_seconds < 60       THEN '1. under 1 minute'
        WHEN gap_seconds < 3600     THEN '2. 1-60 minutes'
        WHEN gap_seconds < 86400    THEN '3. 1-24 hours'
        ELSE                             '4. over 1 day'
    END AS gap_bucket,
    COUNT(*)                              AS total,
    SUM(fraud)                            AS frauds,
    ROUND(1.0 * SUM(fraud) / COUNT(*), 4) AS fraud_rate
FROM velocity
WHERE gap_seconds IS NOT NULL
GROUP BY gap_bucket
ORDER BY gap_bucket;