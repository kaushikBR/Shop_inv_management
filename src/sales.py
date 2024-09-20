import sqlite3
from src.exceptions import exceptions as ex

class salesData:
    def __init__(self) -> None:
        pass
    def record_sale(self):
        try:
            product_id = int(self.sale_product_id.text())
            quantity = int(self.sale_quantity.text())
            sale_date = self.sale_date.text()
            if quantity < 0:
                ex.show_warning_message("Input Error", "Quantity cannot be negative")
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Sales (product_id, quantity, sale_date) VALUES (?, ?, ?)",
                            (product_id, quantity, sale_date))
            cursor.execute("UPDATE Products SET quantity = quantity - ? WHERE product_id = ?",
                            (quantity, product_id))
            conn.commit()
            conn.close()
        except ValueError as ve:
            ex.show_warning_message("Input Error", str(ve))
        except sqlite3.IntegrityError:
            ex.show_warning_message("Data Error", "Product ID not found")
        except Exception as e:
            ex.show_error_message("Database Error", str(e))