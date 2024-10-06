import sys
from src.frames import InventoryApp
from src.license import LicenseManager, ActivationDialog
from PyQt5.QtWidgets import QApplication, QDialog, QShortcut
from PyQt5.QtGui import QKeySequence

def main():
    app = QApplication(sys.argv)
    
    license_manager = LicenseManager()
    is_trial_active, days_left = license_manager.check_trial()
    print(is_trial_active)

    if is_trial_active and days_left == 0:
        window = InventoryApp()
        window.show()
    elif is_trial_active or days_left > 0:
        window = InventoryApp()
        window.show()
    else:
        # Open the activation dialog if trial expired
        dialog = ActivationDialog()
        if dialog.exec_() == QDialog.Accepted:
            # Re-launch the app after activation
            window = InventoryApp()
            window.show()
        else:
            sys.exit(0)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
