WITH RefundsDueToDamage AS (
    SELECT
        p.product_id,
        COUNT(r.order_id) AS refund_orders
    FROM refunds r
    JOIN orders o ON r.order_id = o.order_id
    JOIN shopping_carts sc ON o.order_id = sc.order_id
    JOIN products p ON sc.product_id = p.product_id
    WHERE r.reason = 'DAMAGED_DELIVERY'
    GROUP BY p.product_id
), RankedProducts AS (
    SELECT
        pc.name AS category,
        p.name AS product_name,
        rdd.refund_orders,
        RANK() OVER (PARTITION BY pc.category_id ORDER BY rdd.refund_orders DESC) AS product_rank
    FROM RefundsDueToDamage rdd
    JOIN products p ON rdd.product_id = p.product_id
    JOIN product_category pc ON p.category_id = pc.category_id
)
SELECT
    category,
    product_name,
    refund_orders,
    product_rank
FROM RankedProducts
ORDER BY category, product_rank;
