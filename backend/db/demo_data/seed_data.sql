-- 20 products: 5 per category
INSERT INTO products (product_name, category, unit_price, stock_qty) VALUES
('Wireless Mouse', 'Electronics', 29.99, 240),
('USB-C Hub', 'Electronics', 45.50, 180),
('Noise-Canceling Headphones', 'Electronics', 199.00, 95),
('4K Monitor', 'Electronics', 349.99, 42),
('Portable SSD 1TB', 'Electronics', 119.99, 130),
('Cotton T-Shirt', 'Clothing', 19.99, 500),
('Denim Jeans', 'Clothing', 59.99, 320),
('Running Shoes', 'Clothing', 89.50, 210),
('Winter Jacket', 'Clothing', 129.00, 88),
('Wool Scarf', 'Clothing', 24.50, 400),
('Organic Coffee 12oz', 'Food', 14.99, 600),
('Granola Bars (12pk)', 'Food', 8.49, 750),
('Olive Oil 500ml', 'Food', 12.75, 410),
('Pasta Variety Pack', 'Food', 9.25, 520),
('Dark Chocolate Bar', 'Food', 4.99, 900),
('Office Desk', 'Furniture', 279.00, 36),
('Ergonomic Chair', 'Furniture', 349.50, 28),
('Bookshelf 5-Tier', 'Furniture', 159.99, 55),
('Floor Lamp', 'Furniture', 49.00, 120),
('Coffee Table', 'Furniture', 189.00, 40);

-- 50 customers: 13 North, 13 South, 12 East, 12 West
WITH RECURSIVE c (n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM c WHERE n < 50
)
INSERT INTO customers (customer_name, email, region, city, joined_date)
SELECT
    'Customer ' || printf('%03d', n),
    'cust' || n || '@example.com',
    CASE
        WHEN n <= 13 THEN 'North'
        WHEN n <= 26 THEN 'South'
        WHEN n <= 38 THEN 'East'
        ELSE 'West'
    END,
    'City ' || printf('%02d', ((n - 1) % 25) + 1),
    date('2020-06-01', '+' || CAST(((n - 1) * 11) % 900 AS TEXT) || ' days')
FROM c;

-- 200 orders: 2023-01 through 2024-12, mixed statuses; total_amount filled after line items
WITH RECURSIVE o (n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM o WHERE n < 200
)
INSERT INTO orders (customer_id, order_date, status, total_amount)
SELECT
    ((n - 1) % 50) + 1,
    date(
        '2023-01-01',
        '+' || CAST(CAST((n - 1) * 729 / 199 AS INTEGER) AS TEXT) || ' days'
    ),
    CASE (n % 5)
        WHEN 0 THEN 'Completed'
        WHEN 1 THEN 'Completed'
        WHEN 2 THEN 'Completed'
        WHEN 3 THEN 'Pending'
        ELSE 'Cancelled'
    END,
    0.0
FROM o;

-- 400 order_items: exactly 2 per order; unit_price matches products at insert time
WITH RECURSIVE seq (n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 400
)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct)
SELECT
    (n - 1) / 2 + 1 AS oid,
    CASE WHEN n % 2 = 1
        THEN 1 + (((n - 1) / 2) % 20)
        ELSE 1 + ((((n - 1) / 2) + 7) % 20)
    END AS pid,
    CASE WHEN n % 2 = 1
        THEN 1 + (((n - 1) / 2) % 5)
        ELSE 2 + ((((n - 1) / 2) + 1) % 4)
    END,
    (SELECT unit_price FROM products WHERE product_id = CASE WHEN n % 2 = 1
        THEN 1 + (((n - 1) / 2) % 20)
        ELSE 1 + ((((n - 1) / 2) + 7) % 20)
    END),
    CASE WHEN n % 2 = 1
        THEN CAST((((n - 1) / 2) % 3) * 5 AS REAL)
        ELSE CAST(((((n - 1) / 2) + 1) % 4) * 2.5 AS REAL)
    END
FROM seq;

-- Align order totals with line items (after discount)
UPDATE orders
SET total_amount = (
    SELECT ROUND(
        IFNULL(
            SUM(quantity * unit_price * (1.0 - (discount_pct / 100.0))),
            0
        ),
        2
    )
    FROM order_items
    WHERE order_items.order_id = orders.order_id
);

-- 24 sales targets: 2024-01 .. 2024-06 × 4 regions
INSERT INTO sales_targets (region, month, target_amount) VALUES
('North', '2024-01', 125000.00),
('South', '2024-01', 118000.00),
('East', '2024-01', 132000.00),
('West', '2024-01', 110000.00),
('North', '2024-02', 128000.00),
('South', '2024-02', 121000.00),
('East', '2024-02', 135000.00),
('West', '2024-02', 112500.00),
('North', '2024-03', 130500.00),
('South', '2024-03', 124000.00),
('East', '2024-03', 138000.00),
('West', '2024-03', 115000.00),
('North', '2024-04', 127000.00),
('South', '2024-04', 122500.00),
('East', '2024-04', 136500.00),
('West', '2024-04', 113750.00),
('North', '2024-05', 133000.00),
('South', '2024-05', 126000.00),
('East', '2024-05', 140000.00),
('West', '2024-05', 117250.00),
('North', '2024-06', 135500.00),
('South', '2024-06', 128500.00),
('East', '2024-06', 142000.00),
('West', '2024-06', 119000.00);
