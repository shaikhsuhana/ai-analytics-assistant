# setup_db.py — Creates and seeds the sample e-commerce SQLite database

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"

PRODUCTS = [
    ("Wireless Headphones", "Electronics", 79.99),
    ("Running Shoes", "Footwear", 59.99),
    ("Coffee Maker", "Appliances", 49.99),
    ("Yoga Mat", "Fitness", 29.99),
    ("Laptop Stand", "Accessories", 39.99),
    ("Bluetooth Speaker", "Electronics", 54.99),
    ("Water Bottle", "Fitness", 19.99),
    ("Desk Lamp", "Accessories", 24.99),
    ("Sunglasses", "Accessories", 34.99),
    ("Backpack", "Accessories", 44.99),
]

REGIONS = ["North", "South", "East", "West", "Central"]
CHANNELS = ["Online", "In-Store", "Mobile App"]
STATUSES = ["Completed", "Completed", "Completed", "Refunded", "Pending"]  # weighted

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id   INTEGER PRIMARY KEY,
            name          TEXT,
            region        TEXT,
            signup_date   TEXT
        );

        CREATE TABLE products (
            product_id    INTEGER PRIMARY KEY,
            name          TEXT,
            category      TEXT,
            unit_price    REAL
        );

        CREATE TABLE orders (
            order_id      INTEGER PRIMARY KEY,
            customer_id   INTEGER,
            product_id    INTEGER,
            quantity      INTEGER,
            channel       TEXT,
            status        TEXT,
            order_date    TEXT,
            revenue       REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id)  REFERENCES products(product_id)
        );
    """)

    # Seed products
    c.executemany(
        "INSERT INTO products (name, category, unit_price) VALUES (?, ?, ?)",
        PRODUCTS
    )

    # Seed customers (200)
    names = [
        "Aarav Shah", "Priya Mehta", "Rohan Verma", "Sneha Iyer", "Arjun Nair",
        "Kavya Reddy", "Vikram Singh", "Ananya Gupta", "Rahul Joshi", "Divya Rao",
        "Amit Sharma", "Pooja Desai", "Nikhil Patel", "Riya Kapoor", "Karan Malhotra",
        "Shruti Bhat", "Siddharth Kumar", "Meera Pillai", "Aditya Rao", "Nisha Tiwari",
    ]
    customers = []
    for i in range(1, 201):
        name = random.choice(names) + f" #{i}"
        region = random.choice(REGIONS)
        days_ago = random.randint(30, 730)
        signup = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        customers.append((i, name, region, signup))
    c.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?)", customers
    )

    # Seed orders (1 000)
    orders = []
    base_date = datetime.now()
    for i in range(1, 1001):
        cust_id   = random.randint(1, 200)
        prod_id   = random.randint(1, len(PRODUCTS))
        qty       = random.randint(1, 5)
        channel   = random.choice(CHANNELS)
        status    = random.choice(STATUSES)
        days_ago  = random.randint(0, 365)
        order_dt  = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        price     = PRODUCTS[prod_id - 1][2]
        revenue   = round(price * qty, 2) if status != "Refunded" else 0.0
        orders.append((i, cust_id, prod_id, qty, channel, status, order_dt, revenue))
    c.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", orders
    )

    conn.commit()
    conn.close()
    print(f"✅ Database created at {DB_PATH} with sample e-commerce data.")

if __name__ == "__main__":
    create_db()
