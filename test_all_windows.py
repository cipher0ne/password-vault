import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QWidget

from gui.LoginWindow_ui import Ui_Dialog as Ui_LoginDialog
from gui.SignUpWindow_ui import Ui_Dialog as Ui_SignUpDialog
from gui.NewItem_ui import Ui_Dialog as Ui_NewItemDialog
from gui.MainWindow_ui import Ui_MainWindow


class WindowTester(QWidget):
    """Main window with buttons to test all windows"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Tester")
        self.setMinimumSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Create buttons for each window
        btn_login = QPushButton("Test Login Window")
        btn_login.clicked.connect(self.show_login)
        layout.addWidget(btn_login)
        
        btn_signup = QPushButton("Test SignUp Window")
        btn_signup.clicked.connect(self.show_signup)
        layout.addWidget(btn_signup)
        
        btn_new_item = QPushButton("Test New Item Window")
        btn_new_item.clicked.connect(self.show_new_item)
        layout.addWidget(btn_new_item)
        
        btn_main = QPushButton("Test Main Window")
        btn_main.clicked.connect(self.show_main)
        layout.addWidget(btn_main)
        
        self.setLayout(layout)
        
        # Store references to keep windows alive
        self.windows = []
    
    def show_login(self):
        dialog = QDialog(self)
        ui = Ui_LoginDialog()
        ui.setupUi(dialog)
        self.windows.append(dialog)
        dialog.show()
    
    def show_signup(self):
        dialog = QDialog(self)
        ui = Ui_SignUpDialog()
        ui.setupUi(dialog)
        self.windows.append(dialog)
        dialog.show()
    
    def show_new_item(self):
        dialog = QDialog(self)
        ui = Ui_NewItemDialog()
        ui.setupUi(dialog)
        self.windows.append(dialog)
        dialog.show()
    
    def show_main(self):
        window = QMainWindow(self)
        ui = Ui_MainWindow()
        ui.setupUi(window)
        self.windows.append(window)
        window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    tester = WindowTester()
    tester.show()
    
    sys.exit(app.exec())
