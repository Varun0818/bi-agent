-- Retail analytics demo schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Electronics', 'Clothing', 'Food', 'Furniture')),
    unit_price REAL NOT NULL,
    stock_qty INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    region TEXT NOT NULL CHECK (region IN ('North', 'South', 'East', 'West')),
    city TEXT NOT NULL,
    joined_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Completed', 'Pending', 'Cancelled')),
    total_amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_pct REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sales_targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,
    month TEXT NOT NULL,
    target_amount REAL NOT NULL,
    UNIQUE (region, month)
);
