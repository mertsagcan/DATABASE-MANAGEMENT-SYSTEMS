WITH RevenueByDay AS (
    SELECT
        EXTRACT(ISODOW FROM o.order_time) AS day_of_week,
        DATE_TRUNC('week', o.order_time) AS week,
        SUM(sc.amount * p.price) AS daily_revenue
    FROM orders o
    JOIN shopping_carts sc ON o.order_id = sc.order_id
    JOIN products p ON sc.product_id = p.product_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM refunds r
        WHERE r.order_id = o.order_id
    )
    AND o.status NOT IN ('CANCELLED')
    GROUP BY day_of_week, week
), AverageRevenue AS (
    SELECT
        day_of_week,
        AVG(daily_revenue) AS avg_daily_revenue
    FROM RevenueByDay
    GROUP BY day_of_week
)
SELECT
    CASE day_of_week
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
        WHEN 7 THEN 'Sunday'
    END AS weekday,
    avg_daily_revenue
FROM AverageRevenue
ORDER BY avg_daily_revenue DESC
LIMIT 3;
