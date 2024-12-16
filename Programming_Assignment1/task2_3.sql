WITH FraudulentCategories AS (
    SELECT
        pc.name AS name,
        COUNT(*) AS fraud_count
    FROM refunds r
    JOIN orders o ON r.order_id = o.order_id
    JOIN shopping_carts sc ON o.order_id = sc.order_id
    JOIN products p ON sc.product_id = p.product_id
    JOIN product_category pc ON p.category_id = pc.category_id
    WHERE r.reason = 'FRAUD_SUSPICION'
    GROUP BY pc.name
), RankedCategories AS (
    SELECT
        name,
        fraud_count,
        NTILE(4) OVER (ORDER BY fraud_count DESC) AS quartile
    FROM FraudulentCategories
)
SELECT name, fraud_count
FROM RankedCategories
WHERE quartile = 1
ORDER BY fraud_count DESC;
