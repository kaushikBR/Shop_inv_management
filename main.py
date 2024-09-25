import sys
from src.frames import InventoryApp
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()