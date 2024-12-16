WITH OrderTotals AS (
    SELECT
        o.customer_id,
        EXTRACT(YEAR FROM o.order_time) AS year,
        EXTRACT(MONTH FROM o.order_time) AS month,
        o.order_id,
        SUM(sc.amount * p.price) AS cart_total
    FROM orders o
    JOIN shopping_carts sc ON o.order_id = sc.order_id
    JOIN products p ON sc.product_id = p.product_id
    GROUP BY o.customer_id, year, month, o.order_id
), RankedOrders AS (
    SELECT
        customer_id,
        year,
        month,
        cart_total,
        RANK() OVER (PARTITION BY year, month ORDER BY cart_total DESC) as rank
    FROM OrderTotals
)
SELECT
    customer_id,
    year,
    month,
    cart_total
FROM RankedOrders
WHERE rank = 1
ORDER BY month ASC;
