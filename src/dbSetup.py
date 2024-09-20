import sqlite3
from src.exceptions import exceptions as ex
class databaseSetup():
    def __init__(self) -> None:
        pass

    def create_db(self):
        try:
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()
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
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id VARCHAR,
                product_name TEXT NOT NULL,
                quantity INTEGER,
                sale_date DATE,
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            ex.show_error_message("Database Error", str(e))