import sqlite3
import pandas as pd
from src.exceptions import exceptions as ex

class reportGeneration:
    def __init__(self) -> None:
        pass

    def generate_report(self):
        try:
            conn = sqlite3.connect('inventory_sales.db')
            query = """
            SELECT p.name, SUM(s.quantity) as total_quantity, SUM(s.quantity * p.price) as total_sales
            FROM Sales s
            JOIN Products p ON s.product_id = p.product_id
            GROUP BY p.name
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            self.report_text.setPlainText(df.to_string(index=False))
        except Exception as e:
            ex.show_error_message("Report Error", str(e))