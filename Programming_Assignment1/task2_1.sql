SELECT DISTINCT
    c.customer_id,
    c.gender,
    SUM(sc.amount * p.price) OVER (PARTITION BY c.customer_id) AS sum
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN refunds r ON o.order_id = r.order_id
JOIN shopping_carts sc ON o.order_id = sc.order_id
JOIN products p ON sc.product_id = p.product_id
WHERE o.status = 'COMPLETED'
ORDER BY c.customer_id ASC;
