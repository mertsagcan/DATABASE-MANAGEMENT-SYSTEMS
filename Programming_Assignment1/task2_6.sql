WITH CategoryProductTotals AS (
    SELECT
        pc.category_id,
        pc.name AS name,
        p.product_id,
        SUM(sc.amount) AS total_ordered
    FROM shopping_carts sc
    JOIN products p ON sc.product_id = p.product_id
    JOIN product_category pc ON p.category_id = pc.category_id
    GROUP BY pc.category_id, pc.name, p.product_id
), RankedProducts AS (
    SELECT
        name,
        product_id,
        total_ordered,
        RANK() OVER (PARTITION BY category_id ORDER BY total_ordered DESC) AS rank
    FROM CategoryProductTotals
), TopProducts AS (
    SELECT
        name,
        product_id,
        total_ordered,
        LAG(total_ordered, 1) OVER (ORDER BY total_ordered DESC) AS prev_total_amount,
        rank
    FROM RankedProducts
    WHERE rank = 1
)
SELECT
    name,
    product_id,
    total_ordered,
    total_ordered - prev_total_amount as diff_with_previous
FROM TopProducts
ORDER BY total_ordered DESC;
