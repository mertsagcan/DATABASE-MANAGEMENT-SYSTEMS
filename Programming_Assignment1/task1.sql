-- The scirpt for creating the database:
-- CREATE DATBASE ceng352_20232_mp1

-- Create product_category table
CREATE TABLE IF NOT EXISTS product_category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INT,
    weight DECIMAL NOT NULL,
    price DECIMAL NOT NULL,
    FOREIGN KEY (category_id) REFERENCES product_category(category_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    address TEXT NOT NULL,
    state VARCHAR(5) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F'))
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(40) PRIMARY KEY,
    customer_id VARCHAR(40),
    order_time TIMESTAMP NOT NULL,
    shipping_time TIMESTAMP,
    status VARCHAR(10) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Create shopping_carts table
CREATE TABLE IF NOT EXISTS shopping_carts (
    order_id VARCHAR(40),
    product_id VARCHAR(40),
    amount INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Create refunds table
CREATE TABLE IF NOT EXISTS refunds (
    order_id VARCHAR(40),
    reason VARCHAR(50) NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
