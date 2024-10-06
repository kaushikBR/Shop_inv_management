import sqlite3
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from src.exceptions import exceptions as ex
from src.dbSetup import databaseSetup

class LicenseManager:
    def __init__(self):
        databaseSetup.create_db(self)
        self.db_path = 'inventory_sales.db'
        self.trial_period_days = 30

    def check_trial(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch license details
            cursor.execute("SELECT activation_key, activation_status, day_left FROM license LIMIT 1")
            license_data = cursor.fetchone()

            if license_data is None:
                # If no license data exists, insert initial trial record (30 days)
                day_left = 30
                cursor.execute("INSERT INTO license (activation_key, activation_status, day_left, date_installed) VALUES (?, ?, ?, ?)",
                               ('b8f0accd37176bbe72328f6ebefda52bbba34fa1ea333e2eee60c363d4573bd2', 0, day_left, (datetime.today().strftime('%Y-%m-%d'))))
                conn.commit()
                return True, day_left  # Trial active with 30 days left
            else:
                activation_status = license_data[1]
                day_left = license_data[2]

                if activation_status == 1:
                    return True, 0  # License activated
                else:
                    if day_left > 0:
                        return False, day_left  # Trial still active
                    else:
                        return False, 0  # Trial expired
        except Exception as e:
            ex.show_error_message("License Error", "Error with license")
        finally:
            conn.close()

    def update_trial_days(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch the installation date and day_left
            cursor.execute("SELECT date_installed, activation_status FROM license")
            result = cursor.fetchone()

            if result:
                date_installed = datetime.strptime(result[0], "%Y-%m-%d").date()
                activation_status = result[1]

                # If the app is already activated, skip further checks
                if activation_status == 1:
                    return True

                current_date = datetime.now().date()

                # Calculate the days passed since installation
                days_passed = (current_date - date_installed).days
                day_left = self.trial_period_days - days_passed

                # If trial expired, set day_left to 0
                if day_left < 0:
                    day_left = 0

                # Update the day_left in the database
                cursor.execute("UPDATE license SET day_left = ? WHERE activation_status = 0", (day_left,))
                conn.commit()
        except Exception as e:
            ex.show_error_message("License Error", e)
        finally:
            conn.close()

    def validate_key(self, key):
        try:
            hashed_key = hashlib.sha256(key.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch current activation key from the database
            cursor.execute("SELECT activation_key FROM license LIMIT 1")
            db_key = cursor.fetchone()[0]

            if db_key == hashed_key:
                # Update activation status to 1 (activated)
                cursor.execute("UPDATE license SET activation_status = 1, day_left = 0 WHERE activation_key = ?", (db_key,))
                conn.commit()
                return True
            else:
                return False  # Invalid activation key
        except Exception as e:
            ex.show_error_message("License Error", str(e))
        finally:
            conn.close()

class ActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activate License")
        self.setGeometry(300, 300, 300, 150)
        self.layout = QVBoxLayout()

        self.label = QLabel("Your trial period has ended. Please enter the activation key:")
        self.layout.addWidget(self.label)

        self.activation_key_input = QLineEdit()
        self.activation_key_input.setPlaceholderText("Enter activation key")
        self.activation_key_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.activation_key_input)

        self.activate_button = QPushButton("Activate")
        self.activate_button.clicked.connect(self.activate)
        self.layout.addWidget(self.activate_button)

        self.setLayout(self.layout)
        self.license_manager = LicenseManager()

    def activate(self):
        activation_key = self.activation_key_input.text()
        if self.license_manager.validate_key(activation_key):
            ex.show_warning_message("Success", "License activated successfully!")
            self.accept()
        else:
            ex.show_error_message("Error", "Invalid activation key. Please try again.")
