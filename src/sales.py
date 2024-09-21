import sqlite3
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QHeaderView, QLabel, QPushButton, QHBoxLayout, QTableWidget, QLineEdit
from src.exceptions import exceptions as ex

class FinalizeSaleDialog(QDialog):
    def __init__(self, parent, sale_items, total_price, date, total_price_label):
        super().__init__(parent)
        self.sale_items = sale_items
        self.total_price = total_price
        self.discount = 0.0
        self.date = date
        self.total_price_label = total_price_label
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Finalize Sale")
        layout = QVBoxLayout()
        self.setGeometry(200, 200, 700, 400)

        # Table to display items and MRP
        self.items_table = QTableWidget(len(self.sale_items), 3)
        self.items_table.setHorizontalHeaderLabels(["Item", "MRP", "Discounted MRP"])
        header = self.items_table.horizontalHeader()
        # Stretch the columns to match the window layout
        header.setSectionResizeMode(QHeaderView.Stretch)
        for row, item in enumerate(self.sale_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['name']))  # Item name
            self.items_table.setItem(row, 1, QTableWidgetItem(f"₹{item['MRP']:.2f}"))  # MRP
            self.items_table.setItem(row, 2, QTableWidgetItem(f"₹{item['Discounted MRP']:.2f}"))  # Discounted MRP
        
        layout.addWidget(self.items_table)

        # Total Price display
        self.total_label = QLabel(f"Total: ₹{self.total_price:.2f}")
        self.total_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: blue;")
        layout.addWidget(self.total_label)

        # Discount input and apply button
        discount_layout = QHBoxLayout()
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("Enter discount %")

        self.apply_discount_button = QPushButton("Apply Discount")
        self.apply_discount_button.clicked.connect(self.apply_discount)

        discount_layout.addWidget(self.discount_input)
        discount_layout.addWidget(self.apply_discount_button)

        layout.addLayout(discount_layout)

        # Done and Cancel buttons
        button_layout = QHBoxLayout()
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.finalize_sale)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.done_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_discount(self):
        try:
            discount_percent = float(self.discount_input.text())
            self.discount = discount_percent / 100
            discounted_total = self.total_price * (1 - self.discount)
            self.total_label.setText(f"Total after Discount: ₹{discounted_total:.2f}")
        except ValueError:
            self.total_label.setText("Invalid discount input!")

    def finalize_sale(self):
        try:
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()

            # Insert sale record into Sales table
            cursor.execute("INSERT INTO Sales (sale_date, total_price) VALUES (?, ?)", (self.date, self.total_price,))
            sale_id = cursor.lastrowid

            # Insert each product into SaleItems table and delete from Products
            for item in self.sale_items:
                product_id = item['id']
                if self.discount:
                    discount_percent = self.discount * 100
                    sale_price = item['Discounted MRP'] * (1 - self.discount)
                elif item['MRP'] == item['Discounted MRP']:
                    discount_percent = 0.0
                    sale_price = item['Discounted MRP']
                else:
                    sale_price = item['Discounted MRP']
                    discount_percent = ((item['MRP'] - item['Discounted MRP'])/item['MRP']) * 100
                # Insert sale item
                cursor.execute("""
                INSERT INTO SaleItems (sale_id, product_id, product_name, quantity, discount_percent, MRP, sale_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sale_id, product_id, item['name'], 1, discount_percent, item['MRP'], sale_price,))

                # Delete product from Products table
                cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))

            conn.commit()
            conn.close()

            # Clear the sales UI after finalizing the sale
            self.total_price_label.setText("Total: ₹0.00")
            self.parent().clear_sales_table()  # Clear the sales table in the parent window

            self.accept()  # Close the dialog after success
        except Exception as e:
            ex.show_error_message("Database Error", str(e))
            conn.rollback()
        finally:
            conn.close()

class salesData:
    def __init__(self):
        self.total_price = 0.0
        self.current_sale_id = None
        self.date = None

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
            if sale_Discount.text():
                discount_percent = float(sale_Discount.text())
                if float(sale_Discount.text()) > 100:
                    ex.show_error_message("Invalid", "Discount cannot be more than 100")
                    return None
            else:
                discount_percent = 0

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
                self.date = sale_date

            else:
                ex.show_error_message("Error", "Product Not found")
        except Exception as e:
            ex.show_error_message("Error", e)
        finally:
            sale_product_id.clear()
            sale_product_id.setFocus()
            sale_Discount.clear()

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