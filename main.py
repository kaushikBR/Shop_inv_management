import sys
from src.frames import InventoryApp
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = InventoryApp()
window.show()
sys.exit(app.exec_())
