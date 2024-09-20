from PyQt5.QtWidgets import QMessageBox

class exceptions:
    def __init__(self) -> None:
        pass

    def show_warning_message(title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_error_message(title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()