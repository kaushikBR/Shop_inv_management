from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
import pandas as pd
import sqlite3
from src.exceptions import exceptions as ex
import re

class products():
    def __init__(self) -> None:
        pass

    def add_product(self, product_id, product_name, price, date_edit, Quantity, category):
        try:
            id = self.product_id.text()
            name = self.product_name.text()
            price = float(self.price.text())
            date = self.date_edit.text()
            quantity = int(self.Quantity.text())
            category = self.category.text()

            if not name or not id or price < 0 or quantity < 0:
                ex.show_warning_message("Input Error", "Input valid details")
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Products (date, product_id, product_name, price, quantity, category) VALUES (?, ?, ?, ?, ?, ?)",
                            (date, id, name, price, quantity, category))
            conn.commit()
            conn.close()
            self.product_id.clear()
            self.product_name.clear()
            self.price.clear()
            self.product_id.setFocus()
            self.Quantity.clear()
            self.category.clear()
        except ValueError:
            ex.show_warning_message("Input Error", "Input valid details")
        except Exception as e:
            ex.show_error_message("Database Error", str(e))

    def add_bulk_product(self):
        try:
            check = 0
            file_path, _ = QFileDialog.getOpenFileName(None, 'Import CSV/Excel File', '', 'CSV/Excel Files (*.csv *.xlsx)')
            if file_path:
                if file_path.endswith('.csv'):
                    try:
                        header_row = self.find_header_row(file_path, file_type='csv')
                    except Exception as e:
                        ex.show_warning_message("Error", "File Error")
                    if header_row is not None:
                        df = pd.read_csv(file_path, skiprows=header_row)
                        df.dropna(how='all', axis=1, inplace=True)
                        check += 1
                    else:
                        ex.show_warning_message("Error", "Could not detect header in the CSV file.")
                    return
                
                elif file_path.endswith('.xlsx'):
                    try:
                        header_row = self.find_header_row(file_path, file_type='excel')
                    except Exception as e:
                        ex.show_warning_message("Error", "File Error")
                    if header_row is not None:
                        df = pd.read_excel(file_path, skiprows=header_row)
                        df.dropna(how='all', axis=1, inplace=True)
                        check += 1
                    else:
                        ex.show_warning_message("Error", "Could not detect header in the Excel file.")
                    return

                
        except Exception as e:
            ex.show_error_message("File Error", "Please check the file format")

        finally:
            if check:
                e_columns = ['product_id', 'product_name', 'price', 'date', 'quantity', 'category']
                regex_patterns = [r'product\s*id', r'product\s*name', r'price', r'date', r'quantity', r'category']

                df.columns = [re.sub(r'\s+', ' ', col.strip().lower()) for col in df.columns]

                m_columns = []
                for pattern in regex_patterns:
                    for col in df.columns:
                        if re.match(pattern, col):
                            m_columns.append(col)
                df.rename(columns={m_columns[0]:e_columns[0],
                               m_columns[1]:e_columns[1],
                               m_columns[2]:e_columns[2],
                               m_columns[3]:e_columns[3],
                               m_columns[4]:e_columns[4],
                               m_columns[5]:e_columns[5],}, inplace=True)
                dialog = ImportDialog(df)
                if dialog.exec_() == QDialog.Accepted:
                    try:
                        # Assuming df is ready and columns match
                        conn = sqlite3.connect('inventory_sales.db')
                        df.to_sql('Products', conn, if_exists='append', index=False)
                        conn.commit()
                        conn.close()
                        ex.show_warning_message("Import", f"Imported {len(df)} Rows")
                    except Exception as e:
                        ex.show_error_message("Import Error", "Duplicate data detected.")
                else:
                    # User clicked Cancel, do nothing
                    ex.show_error_message("Import", "Import Cancelled")
            else:
                return
    
    def find_header_row(self, file_path, file_type):
        if file_type == 'csv':
            # For CSV files, manually read the file line by line
            with open(file_path, 'r') as file:
                for row_idx, line in enumerate(file):
                    # Split by comma and remove leading/trailing whitespace
                    columns = [col.strip() for col in line.split(',')]
                    if self.is_valid_header(columns):
                        return row_idx  # Return the index of the header row
        elif file_type == 'excel':
            # For Excel files, load the file and scan for the header
            df = pd.read_excel(file_path, header=None)  # Load without header
            for row_idx in range(len(df)):
                columns = df.iloc[row_idx].dropna().astype(str).str.strip().tolist()  # Convert to list of strings
                if self.is_valid_header(columns):
                    return row_idx  # Return the index of the header row
        
        return None
    
    def is_valid_header(self, columns):
        """
        Check if the current row can be considered as a valid header.
        We assume that a valid header contains specific keywords like 'product id', 'product name', etc.
        """
        # Regex patterns to match header names
        regex_patterns = {
            'product id': r'product\s*id|prod\s*id|productid|pid',
            'product name': r'product\s*name|prod\s*name|pname',
            'price': r'price|cost|amount',
            'date': r'date|datetime|time',
            'quantity':r'quantity|Quantity|quant|Q|ml',
            'category':r'category|Category|cat|cata'
        }

        valid_column_count = 0

        # Check each column against the regex patterns
        for pattern in regex_patterns.values():
            for col in columns:
                if re.match(pattern, col.lower()):
                    valid_column_count += 1
                    break

        # A valid header must match at least 5 out of 6 expected columns (for flexibility)
        return valid_column_count >= 5
    
    def search_product(self, *args):
        if len(args) != 2:
            ex.show_warning_message("Search Error", "Invalid search parameters")
            return
        search_by = args[0]
        search_value = args[1]

        valid_fields = ['product_id', 'product_name', 'category']
        if search_by not in valid_fields:
            ex.show_warning_message("Search Error", "Invalid field to search by")
            return
        try:
            # Connect to the database
            conn = sqlite3.connect('inventory_sales.db')
            cursor = conn.cursor()
            query = f"SELECT * FROM Products WHERE {search_by} LIKE ?"
            cursor.execute(query, ('%' + search_value + '%',))
            results = cursor.fetchall()
            if not results:
                ex.show_warning_message("Search Result", "No matching products found")
            else:
                dialog = ImportDialog(pd.DataFrame(results, columns=['date', 'product_id', 'product_name', 'price', 'quantity', 'category']))
                dialog.exec_()

        
        except sqlite3.Error as e:
            ex.show_error_message("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()

class ImportDialog(QDialog):
    def __init__(self, data_frame, parent=None):
        super(ImportDialog, self).__init__(parent)
        self.setWindowTitle('Confirm Data Import')
        self.setGeometry(200, 200, 700, 400)

        # Main layout
        layout = QVBoxLayout()

        # Table for displaying data
        self.table_widget = QTableWidget()
        self.load_data_into_table(data_frame)
        layout.addWidget(self.table_widget)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect the buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def load_data_into_table(self, df):
        """Load pandas DataFrame into the QTableWidget."""
        self.table_widget.setRowCount(len(df))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        # Populate the table with data
        for row_idx in range(len(df)):
            for col_idx, col_name in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[row_idx, col_idx]))
                self.table_widget.setItem(row_idx, col_idx, item)
