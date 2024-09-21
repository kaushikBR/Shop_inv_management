import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QHeaderView,
                             QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from src.exceptions import exceptions as ex

class reportGeneration(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Generate Reports")
        title_label.setFont(QFont("Arial", 16))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Date range selectors
        date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)

        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date_edit)
        layout.addLayout(date_layout)

        # Report type selector
        report_type_layout = QHBoxLayout()
        self.report_type_combo = QComboBox(self)
        self.report_type_combo.addItems(["Sales Report", "Product Report"])
        report_type_layout.addWidget(QLabel("Report Type:"))
        report_type_layout.addWidget(self.report_type_combo)
        layout.addLayout(report_type_layout)

        # Generate report button
        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_report_button)

        # Table to display the report
        self.report_table = QTableWidget(0, 3)  # We'll adjust columns dynamically
        layout.addWidget(self.report_table)

        # Export button
        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_report_to_excel)
        layout.addWidget(self.export_button, alignment=Qt.AlignRight)

        self.setLayout(layout)
    
    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        try:
            conn = sqlite3.connect('inventory_sales.db')

            if report_type == "Sales Report":
                query = f"""
                SELECT s.sale_date AS Date, 
                       si.product_name AS Product_Name, 
                       si.sale_price AS MRP
                FROM SaleItems si
                JOIN Sales s ON si.sale_id = s.sale_id
                WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY s.sale_date
                ORDER BY s.sale_date ASC
                """
                self.show_report(conn, query, ["Date", "Product Name", "Price"])

            elif report_type == "Product Report":
                query = """
                SELECT product_name AS Product, 
                       SUM(product_name) AS Total_Quantity_Left
                FROM Products
                GROUP BY product_name
                ORDER BY product_name ASC
                """
                self.show_report(conn, query, ["Product Name", "Total Quantity Left"])

            conn.close()

        except Exception as e:
            ex.show_error_message("Report Error", str(e))

    def show_report(self, conn, query, headers):
        try:
            # Execute query and load into DataFrame
            df = pd.read_sql_query(query, conn)

            # Clear any previous data in the table
            self.report_table.clear()
            self.report_table.setRowCount(0)
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)

            header = self.report_table.horizontalHeader()
            # Stretch the columns to match the window layout
            header.setSectionResizeMode(QHeaderView.Stretch)


            # Fill the table with data from the DataFrame
            for row in df.itertuples():
                row_position = self.report_table.rowCount()
                self.report_table.insertRow(row_position)
                for column, value in enumerate(row[1:]):  # Ignore the index column from itertuples()
                    self.report_table.setItem(row_position, column, QTableWidgetItem(str(value)))

            self.report_df = df  # Store the dataframe for export
        except Exception as e:
            ex.show_error_message("Report Error", str(e))

    def export_report_to_excel(self):
        # Ensure there's data to export
        if hasattr(self, 'report_df') and not self.report_df.empty:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Excel Files (*.xlsx);;All Files (*)", options=options)

            if file_path:
                # Append .xlsx if not provided
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'

                try:
                    # Save the DataFrame to an Excel file
                    self.report_df.to_excel(file_path, index=False)
                    QMessageBox.information(self, "Success", f"Report successfully exported to {file_path}")
                except Exception as e:
                    ex.show_error_message("Export Error", str(e))
        else:
            ex.show_error_message("Export Error", "No data available to export.")