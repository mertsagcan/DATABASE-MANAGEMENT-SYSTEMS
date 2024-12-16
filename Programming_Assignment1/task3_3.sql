-- Standard view for dynamic, up-to-date data access
CREATE OR REPLACE VIEW customer_view AS
SELECT 
    c.customer_id, 
    c.name, 
    c.surname, 
    o.order_id, 
    o.order_time, 
    o.shipping_time, 
    o.status, 
    sc.product_id, 
    p.name AS product_name, 
    sc.amount, 
    p.price
FROM 
    customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN shopping_carts sc ON o.order_id = sc.order_id
JOIN products p ON sc.product_id = p.product_id
WHERE 
    o.customer_id = CURRENT_USER OR CURRENT_USER = 'postgres';


--I have assumed that the current user is the customer. 
--I have added my username to the last row so i can view all users' information.