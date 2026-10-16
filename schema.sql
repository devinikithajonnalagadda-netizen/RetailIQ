CREATE DATABASE IF NOT EXISTS retailiq_db;

USE retailiq_db;

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(120) NOT NULL UNIQUE,
    category VARCHAR(60) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (unit_price > 0),
    CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_name VARCHAR(120) NOT NULL DEFAULT 'Walk-in Customer',
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (quantity > 0),
    CHECK (unit_price > 0),
    CHECK (unit_cost >= 0)
);

INSERT IGNORE INTO products
(product_name, category, unit_price, unit_cost)
VALUES
('Rice 5kg', 'Grocery', 420.00, 350.00),
('Cooking Oil 1L', 'Grocery', 155.00, 125.00),
('Shampoo 180ml', 'Personal Care', 120.00, 82.00),
('Notebook', 'Other', 60.00, 35.00),
('Biscuits Pack', 'Food & Beverage', 30.00, 18.00);

SHOW TABLES;

SELECT * FROM products;

