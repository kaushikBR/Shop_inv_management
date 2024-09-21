from PyQt5.QtWidgets import (QMainWindow, QDialog ,QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QFormLayout, QLineEdit, QPushButton, QTextEdit, 
                             QLabel, QTabWidget, QDateEdit, QComboBox, QHeaderView)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QKeySequence, QFont
from src.dbSetup import databaseSetup
from src.product import products
from src.sales import salesData, FinalizeSaleDialog
from src.report import reportGeneration
from src.exceptions import exceptions as ex

stylesheet = """
QLineEdit, QPushButton, QDateEdit {
    font-size: 9pt;
}
"""

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.product_int = products()
        self.sales_int = salesData()
        self.setWindowTitle('Inventory Management System')
        self.setGeometry(100, 100, 800, 600)
        self.showMaximized()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        header_layout = QHBoxLayout()
        title_label = QLabel("Shop Inventory Management", self)
        title_label.setAlignment(Qt.AlignCenter)  # Align the title to the center
        header_layout.addWidget(title_label)
        self.layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.sales_tab = QWidget()
        self.inventory_tab = QWidget()
        self.report_tab = QWidget()

        self.tab_widget.addTab(self.sales_tab, 'Sales')
        self.tab_widget.addTab(self.inventory_tab, 'Inventory')
        self.tab_widget.addTab(self.report_tab, 'Reports')

        self.setup_inventory_tab()
        self.setup_sales_tab()
        self.setup_report_tab()
        databaseSetup.create_db(self)

    def setup_inventory_tab(self):
        layout = QFormLayout()

        self.product_id = QLineEdit()
        self.product_id.setPlaceholderText("Scan Barcode for ID")
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter Product Name")
        self.price = QLineEdit()
        self.price.setPlaceholderText("Enter Product price")
        self.date_edit = QDateEdit(self)
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.Quantity = QLineEdit()
        self.Quantity.setPlaceholderText("Quantity in ml")
        self.category = QLineEdit()
        self.category.setPlaceholderText("Whisky/Beer/Rum/Vodka")

        layout.addRow(QLabel("Producy ID:"), self.product_id)
        layout.addRow(QLabel("Product Name:"), self.product_name)
        layout.addRow(QLabel("Price:"), self.price)
        layout.addRow(QLabel("Stock Date:"), self.date_edit)
        # Create a horizontal layout to hold both Quantity and Category widgets
        hbox = QHBoxLayout()
        # Add QLabel and QLineEdit for Quantity
        hbox.addWidget(QLabel("Quantity:        "))
        hbox.addWidget(self.Quantity)

        # Add QLabel and QLineEdit for Category
        hbox.addWidget(QLabel("  Category:        "))
        hbox.addWidget(self.category)

        # Now add this horizontal layout as a row to the form layout
        layout.addRow(hbox)

        # Add QDateEdit widget for date selection
        self.date_edit.setCalendarPopup(True)  # Enable the calendar popup
        self.date_edit.setDate(QDate.currentDate())  # Set to the system's current date
        self.date_edit.setFixedWidth(150)

        self.Quantity.maximumWidth
        self.category.maximumWidth

        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(lambda: products.add_product(self, self.product_id, self.product_name, 
                                                            self.price, self.date_edit,
                                                            self.Quantity, self.category))
        self.shortcut = QKeySequence("Return")
        self.add_button.setShortcut(self.shortcut)
        self.bulk_add_button = QPushButton("Import Excel/CSV For Bulk Product Add")
        self.bulk_add_button.clicked.connect(self.product_int.add_bulk_product)


        layout.addWidget(self.add_button)
        layout.addWidget(self.bulk_add_button)

        layout.addRow(QLabel(""))
        layout.addRow(QLabel(""))
        layout.addRow(QLabel(""))

        search_layout = QHBoxLayout()
        title_label = QLabel("Search Inventory", self)
        search_layout.addWidget(title_label)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addRow(search_layout)
        searchbox = QHBoxLayout()
        self.search_by_combo = QComboBox()
        self.search_by_combo.addItems(["Product ID", "Product Name", "Category"])
        self.search_by_combo.setCurrentIndex(-1)

        # LineEdit for search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text to search")

        # Search Button
        self.search_button = QPushButton("Search")

        self.search_button.clicked.connect(self.perform_search)

        # Add widgets to search layout
        searchbox.addWidget(QLabel("Search By:"))
        searchbox.addWidget(self.search_by_combo)
        searchbox.addWidget(self.search_input)
        searchbox.addWidget(self.search_button)

        # Add the search layout to the main layout
        layout.addRow(searchbox)


        self.inventory_tab.setLayout(layout)

    def perform_search(self):
        search_by = self.search_by_combo.currentText()  # Get the selected value from the combo box
        search_value = self.search_input.text()  # Get the text from the input field
        if search_by == 'Product Name':
            search_by = 'product_name'
        elif search_by == 'Category':
            search_by= 'category'
        elif search_by == 'Product ID':
            search_by = 'product_id'
        else:
            return

        # Now call the search_product method with the values
        self.product_int.search_product(search_by, search_value)
        self.search_input.clear()

    def setup_sales_tab(self):
        layout = QFormLayout()

        self.sale_product_id = QLineEdit()
        self.sale_product_id.setPlaceholderText("Scan Barcode for ID")
        self.sale_date_edit = QDateEdit(self)
        self.sale_date_edit.setMaximumDate(QDate.currentDate())
        self.sale_Discount = QLineEdit()
        self.sale_Discount.setPlaceholderText("Discount %")

        layout.addRow(QLabel("Product ID:"), self.sale_product_id)
        layout.addRow(QLabel("Sale Date (YYYY-MM-DD):"), self.sale_date_edit)
        layout.addRow(QLabel("Discount:"), self.sale_Discount)

        self.sale_date_edit.setCalendarPopup(True)  # Enable the calendar popup
        self.sale_date_edit.setDate(QDate.currentDate())  # Set to the system's current date
        self.sale_date_edit.setFixedWidth(150)


        self.record_sale_button = QPushButton("Record Sale")
        self.record_sale_button.clicked.connect(lambda: self.sales_int.record_sale(self.sale_product_id, 
                                                                                   self.sale_Discount, 
                                                                                   self.sale_date_edit,
                                                                                   self.product_info_table, 
                                                                                   self.total_price_label))

        layout.addWidget(self.record_sale_button)
        self.shortcut = QKeySequence("Return")
        self.record_sale_button.setShortcut(self.shortcut)

        # Table to display product info
        self.product_info_table = QTableWidget(0, 7)
        self.product_info_table.setHorizontalHeaderLabels(["Date", "Product ID", "Product Name", "Stock Date", "MRP", "Discounted MRP", "  "])
        # Adjust the column width to fit the table's width
        header = self.product_info_table.horizontalHeader()

        # Stretch the columns to match the window layout
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.product_info_table)

        # Label to display the total price
        self.total_price_label = QLabel("Total: ₹0.00")
        my_font = QFont("Arial", 20)
        self.total_price_label.setFont(my_font)
        layout.addWidget(self.total_price_label)

        # Done button to finalize the sale
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.open_finalize_sale_dialog)
        layout.addWidget(self.done_button)
        self.sales_tab.setLayout(layout)

    def open_finalize_sale_dialog(self):
        # Collect current sale items from the product_info_table
        sale_items = []
        for row in range(self.product_info_table.rowCount()):
            item = {
                'id': self.product_info_table.item(row, 1).text(),
                'name': self.product_info_table.item(row, 2).text(),
                'MRP': float(self.product_info_table.item(row, 4).text().replace("₹", "")),
                'Discounted MRP': float(self.product_info_table.item(row, 5).text().replace("₹", ""))
            }
            sale_items.append(item)

        total_price = self.sales_int.total_price
        date = self.sales_int.date

        # Open the finalize sale dialog
        dialog = FinalizeSaleDialog(self, sale_items, total_price, date, self.total_price_label)
        if dialog.exec_() == QDialog.Accepted:
            ex.show_warning_message("Done", "Sale Recorded")

    def clear_sales_table(self):
        # Clear the product info table after finalizing
        self.product_info_table.setRowCount(0)
        self.total_price_label.setText("Total Price: ₹0.00")
        self.sales_int.total_price = 0.0

    def setup_report_tab(self):
        # Replacing this method with the full integration of reportGeneration UI
        self.report_widget = reportGeneration()  # Instantiate the report generation class
        report_layout = QVBoxLayout()  # Create a layout for the Reports tab
        report_layout.addWidget(self.report_widget)  # Add the report widget to the layout
        self.report_tab.setLayout(report_layout)  # Set the layout on the Reports tab