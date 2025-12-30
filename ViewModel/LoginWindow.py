from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal
from View.LoginWindow_ui import Ui_Dialog


class LoginWindow(QDialog):
    """Login window ViewModel"""
    
    login_successful = Signal(str)  # Signal emitted with user email on successful login
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_login)
        self.ui.pushButton_2.clicked.connect(self.open_signup)
        
        # Make password field hidden
        self.ui.lineEdit_2.setEchoMode(self.ui.lineEdit_2.EchoMode.Password)
        
        # Press Enter to login
        self.ui.lineEdit.returnPressed.connect(self.handle_login)
        self.ui.lineEdit_2.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """Handle login button click"""
        email = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
        
        success, message = self.model.login_user(email, password)
        
        if success:
            self.login_successful.emit(email)
            self.accept()  # Close dialog with success
        else:
            QMessageBox.warning(self, "Login Failed", message)
            self.ui.lineEdit_2.clear()
    
    def open_signup(self):
        """Open the sign up window"""
        from ViewModel.SignUpWindow import SignUpWindow
        signup_window = SignUpWindow(self.model, self)
        if signup_window.exec() == QDialog.DialogCode.Accepted:
            # User successfully signed up, optionally pre-fill email
            pass
