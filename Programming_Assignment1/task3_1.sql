
CREATE TABLE IF NOT EXISTS category_avg_prices (
    category_id INTEGER PRIMARY KEY,
    avg_price NUMERIC(10, 2)
);


INSERT INTO category_avg_prices(category_id, avg_price)
SELECT category_id, AVG(price) AS avg_price
FROM products
GROUP BY category_id
ORDER BY category_id ASC;


CREATE OR REPLACE FUNCTION update_avg_price()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE category_avg_prices
    SET avg_price = (
        SELECT AVG(price)
        FROM products
        WHERE category_id = NEW.category_id
    )
    WHERE category_id = NEW.category_id;

    IF NOT FOUND THEN
        INSERT INTO category_avg_prices(category_id, avg_price)
        VALUES (
            NEW.category_id,
            (SELECT AVG(price) FROM products WHERE category_id = NEW.category_id ORDER BY NEW.avg_price)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER trg_update_avg_price
AFTER INSERT ON products
FOR EACH ROW
EXECUTE FUNCTION update_avg_price();
