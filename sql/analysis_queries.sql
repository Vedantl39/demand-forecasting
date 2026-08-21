-- Demand Forecasting Analytics — SQL analysis layer
-- Target: SQLite (data/processed/rossmann.db, table: sales)

-- ============================================================
-- 1. Day-of-week seasonality — average sales by day of week
-- ============================================================
SELECT
    DayOfWeek,
    COUNT(*) AS observations,
    ROUND(AVG(Sales), 0) AS avg_sales,
    ROUND(AVG(Customers), 0) AS avg_customers
FROM sales
GROUP BY DayOfWeek
ORDER BY DayOfWeek;


-- ============================================================
-- 2. Promotion effect on sales (within the same store type)
-- ============================================================
SELECT
    StoreType,
    Promo,
    COUNT(*) AS observations,
    ROUND(AVG(Sales), 0) AS avg_sales,
    ROUND(AVG(Sales) * 1.0 / NULLIF(AVG(Customers), 0), 2) AS avg_sales_per_customer
FROM sales
GROUP BY StoreType, Promo
ORDER BY StoreType, Promo;


-- ============================================================
-- 3. Store-type performance ranking
-- ============================================================
SELECT
    StoreType,
    Assortment,
    COUNT(DISTINCT Store) AS num_stores,
    ROUND(AVG(Sales), 0) AS avg_daily_sales,
    ROUND(AVG(Customers), 0) AS avg_daily_customers
FROM sales
GROUP BY StoreType, Assortment
ORDER BY avg_daily_sales DESC;


-- ============================================================
-- 4. Monthly sales trend (aggregate across all stores)
-- ============================================================
SELECT
    strftime('%Y-%m', Date) AS year_month,
    SUM(Sales) AS total_sales,
    COUNT(DISTINCT Store) AS active_stores,
    ROUND(SUM(Sales) * 1.0 / COUNT(DISTINCT Store), 0) AS avg_sales_per_store
FROM sales
GROUP BY year_month
ORDER BY year_month;


-- ============================================================
-- 5. School holiday effect on sales
-- ============================================================
SELECT
    SchoolHoliday,
    COUNT(*) AS observations,
    ROUND(AVG(Sales), 0) AS avg_sales
FROM sales
GROUP BY SchoolHoliday;


-- ============================================================
-- 6. Top 10 highest-volume stores (by average daily sales)
-- ============================================================
SELECT
    Store,
    StoreType,
    COUNT(*) AS days_open,
    ROUND(AVG(Sales), 0) AS avg_daily_sales
FROM sales
GROUP BY Store, StoreType
HAVING COUNT(*) >= 900
ORDER BY avg_daily_sales DESC
LIMIT 10;


-- ============================================================
-- 7. Competition distance vs average sales (does nearby competition matter?)
-- ============================================================
SELECT
    CASE
        WHEN CompetitionDistance < 500 THEN 'Very close (<500m)'
        WHEN CompetitionDistance < 2000 THEN 'Close (500-2000m)'
        WHEN CompetitionDistance < 10000 THEN 'Moderate (2-10km)'
        ELSE 'Far (>10km)'
    END AS competition_proximity,
    COUNT(DISTINCT Store) AS num_stores,
    ROUND(AVG(Sales), 0) AS avg_daily_sales
FROM sales
WHERE CompetitionDistance IS NOT NULL
GROUP BY competition_proximity
ORDER BY avg_daily_sales DESC;
