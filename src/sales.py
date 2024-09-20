import sqlite3
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QPushButton
from src.exceptions import exceptions as ex

class salesData:
    def __init__(self):
        self.total_price = 0.0
        self.current_sale_id = None

    def query_product(self, product_id):
        conn = sqlite3.connect('inventory_sales.db')
        cursor = conn.cursor()

        # Query the product details from the database
        # product_id = int(product_id)
        try:
            cursor.execute("SELECT product_id, product_name, price, date FROM Products WHERE product_id = ?", (int(product_id),))
            product = cursor.fetchone()

            conn.close()

            if product:
                return product
            else:
                return None
        except Exception as e:
            return None

    def record_sale(self, sale_product_id, sale_Discount, sale_date_edit, product_info_table, total_price_label):
        try:
            product_id = sale_product_id.text()
            discount_percent = float(sale_Discount.text()) if sale_Discount.text() else 0
            sale_date = sale_date_edit.date().toString("yyyy-MM-dd")

            # Query product information
            product = self.query_product(product_id)
            if product:
                product_id, product_name, price, stock_date = product
                discounted_price = price * (1 - discount_percent / 100)
                

                # Add the product info to the table
                row_position = product_info_table.rowCount()
                product_info_table.insertRow(row_position)
                product_info_table.setItem(row_position, 0, QTableWidgetItem(sale_date))
                product_info_table.setItem(row_position, 1, QTableWidgetItem(product_id))
                product_info_table.setItem(row_position, 2, QTableWidgetItem(product_name))
                product_info_table.setItem(row_position, 3, QTableWidgetItem(stock_date))
                product_info_table.setItem(row_position, 4, QTableWidgetItem(f"₹{price:.2f}"))
                product_info_table.setItem(row_position, 5, QTableWidgetItem(f"₹{discounted_price:.2f}"))



                delete_button = QPushButton("✖")  # Cross mark
                delete_button.clicked.connect(lambda :self.delete_item(delete_button, product_info_table, total_price_label))
                product_info_table.setCellWidget(row_position, 6, delete_button)

                # Update the total price
                self.total_price += discounted_price
                total_price_label.setText(f"Total Price: ₹{self.total_price:.2f}")

            else:
                ex.show_error_message("Error", "Product Not found")
        except Exception as e:
            ex.show_error_message("Error", "Invalid action.")
        finally:
            sale_product_id.clear()
            sale_product_id.setFocus()
            sale_Discount.clear()

    def finalize_sale(self):
        conn = sqlite3.connect('inventory_sales.db')
        cursor = conn.cursor()

        # Insert the sale into the Sales table and get the sale_id
        cursor.execute("INSERT INTO Sales (sale_date, total_price) VALUES (?, ?)", 
                       (self.sale_date_edit.date().toString("yyyy-MM-dd"), self.total_price))
        self.current_sale_id = cursor.lastrowid  # Get the last inserted sale_id

        # Save each row in the table to the SaleItems database
        for row in range(self.product_info_table.rowCount()):
            product_id = self.product_info_table.item(row, 0).text()
            product_name = self.product_info_table.item(row, 1).text()
            quantity = int(self.product_info_table.item(row, 2).text())
            discount_percent = float(self.sale_Discount.text()) if self.sale_Discount.text() else 0
            sale_price = float(self.product_info_table.item(row, 4).text().replace("$", ""))

            cursor.execute("""
                INSERT INTO SaleItems (sale_id, product_id, product_name, quantity, discount_percent, sale_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.current_sale_id, product_id, product_name, quantity, discount_percent, sale_price))

        conn.commit()
        conn.close()

        # Clear the total price and product info after saving
        self.total_price = 0.0
        self.total_price_label.setText("Total Price: $0.00")
        self.product_info_table.setRowCount(0)  # Clear the table

        print("Sale finalized and saved.")

    def delete_item(self, delete_button, product_info_table, total_price_label):
        row_position = product_info_table.indexAt(delete_button.pos()).row()  # Get row dynamically based on button position
        
        if row_position == -1:
            return  # If the row is invalid, do nothing
        
        discounted_price_item = product_info_table.item(row_position, 5)  # Column for Discounted Price
        try:
            if discounted_price_item is not None:
                discounted_price = float(discounted_price_item.text().replace("₹", ""))
                # Update the total price before removing the row
                self.total_price -= discounted_price
                
                # Remove the row from the table
                product_info_table.removeRow(row_position)
            
                # Update the total price label
                total_price_label.setText(f"Total Price: ₹{self.total_price:.2f}")
            else:
                ex.show_error_message("Error", "Item not found.")
        except Exception as e:
            ex.show_error_message("Error", "Some error has occurred.")