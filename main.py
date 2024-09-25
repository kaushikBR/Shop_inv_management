import sys
from src.frames import InventoryApp
from src.license import check_trial, validate_license, save_license
from PyQt5.QtWidgets import QApplication
import hashlib

def main():
    if not check_trial():
        while True:
            license_key = input("Enter your license key: ")
            if validate_license(license_key):
                save_license(hashlib.sha256(license_key.encode()).hexdigest())
                print("License key is valid. Enjoy the full version!")
                break
            else:
                print("Invalid license key. Please try again.")
    else:
        app = QApplication(sys.argv)
        window = InventoryApp()
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()