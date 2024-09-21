import sqlite3
from src.exceptions import exceptions as ex

class databaseSetup():
    def __init__(self) -> None:
        pass

    def create_db(self):
        try:
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()

            # Create the Products table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                date DATE,
                product_id VARCHAR,
                product_name TEXT NOT NULL,
                price REAL,
                quantity TEXT,
                category TEXT,
                CONSTRAINT PK_product PRIMARY KEY (product_id, product_name)
            )
            """)

            # Create the Sales table with a unique sale_id for each transaction
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date DATE,
                total_price REAL
            )
            """)

            # Create the SaleItems table to hold individual sale items
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS SaleItems (
                sale_id INTEGER,
                product_id VARCHAR,
                product_name TEXT NOT NULL,
                quantity INTEGER,
                discount_percent REAL DEFAULT 0,
                MRP REAL,
                sale_price REAL,
                PRIMARY KEY (sale_id, product_id),
                FOREIGN KEY (sale_id) REFERENCES Sales(sale_id)
            )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            ex.show_error_message("Database Error", str(e))