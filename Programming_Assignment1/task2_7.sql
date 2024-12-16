SELECT
    gender,
    TO_CHAR(order_time, 'Month') AS month,
    SUM(price * amount) AS cart_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN shopping_carts sc ON o.order_id = sc.order_id
JOIN products p ON sc.product_id = p.product_id
GROUP BY CUBE(gender, TO_CHAR(order_time, 'Month'))
ORDER BY gender, month;



CREATE EXTENSION IF NOT EXISTS tablefunc;


SELECT * FROM crosstab(
  $$SELECT gender, TO_CHAR(order_time, 'Month') AS month, SUM(price * amount) AS total_money_spent
    FROM customers
    JOIN orders ON customers.customer_id = orders.customer_id
    JOIN shopping_carts ON orders.order_id = shopping_carts.order_id
    JOIN products ON shopping_carts.product_id = products.product_id
    GROUP BY CUBE (gender, month)
    ORDER BY gender, month$$,
  $$SELECT DISTINCT TO_CHAR(order_time, 'Month') FROM orders ORDER BY 1$$
) AS final_result(gender text, February numeric, January numeric, March numeric);
