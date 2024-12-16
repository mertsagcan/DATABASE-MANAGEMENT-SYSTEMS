WITH NonCancelledRefundedOrders AS (
    SELECT o.order_id
    FROM orders o
    LEFT JOIN refunds r ON o.order_id = r.order_id
    WHERE o.status != 'CANCELLED' AND r.order_id IS NULL
), OrderCategoryPairs AS (
    SELECT 
        o1.order_id, 
        p1.category_id AS category_id1, 
        p2.category_id AS category_id2
    FROM NonCancelledRefundedOrders o1
    JOIN shopping_carts s1 ON o1.order_id = s1.order_id
    JOIN products p1 ON s1.product_id = p1.product_id
    JOIN shopping_carts s2 ON o1.order_id = s2.order_id
    JOIN products p2 ON s2.product_id = p2.product_id
    WHERE p1.category_id < p2.category_id
), CategoryPairCounts AS (
    SELECT 
        category_id1, 
        category_id2, 
        COUNT(*) AS total_value
    FROM OrderCategoryPairs
    GROUP BY category_id1, category_id2
), CategoryPairsWithNames AS (
    SELECT 
        c1.name AS category_name1, 
        c2.name AS category_name2, 
        cpc.total_value
    FROM CategoryPairCounts cpc
    JOIN product_category c1 ON cpc.category_id1 = c1.category_id
    JOIN product_category c2 ON cpc.category_id2 = c2.category_id
)
SELECT
    CASE 
        WHEN category_name1 < category_name2 THEN category_name1
        ELSE category_name2
    END AS category1,
    CASE 
        WHEN category_name1 < category_name2 THEN category_name2
        ELSE category_name1
    END AS category2,
    total_value
FROM CategoryPairsWithNames
ORDER BY total_value DESC
LIMIT 10;