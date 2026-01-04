from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal
from View.SignUpWindow_ui import Ui_Dialog
import re


class SignUpWindow(QDialog):
    """Sign up window ViewModel"""
    
    login_successful = Signal(str)  # Signal emitted with user email on successful registration
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_signup)
        self.ui.pushButton_2.clicked.connect(self.open_login)
        
        # Make password fields hidden
        self.ui.lineEdit_2.setEchoMode(self.ui.lineEdit_2.EchoMode.Password)
        self.ui.lineEdit_3.setEchoMode(self.ui.lineEdit_3.EchoMode.Password)
        
        # Press Enter to sign up
        self.ui.lineEdit.returnPressed.connect(self.handle_signup)
        self.ui.lineEdit_2.returnPressed.connect(self.handle_signup)
        self.ui.lineEdit_3.returnPressed.connect(self.handle_signup)
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        if ' ' in password:
            return False, "Password cannot contain spaces"
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, numbers, and special characters"
        
        return True, "Password is valid"
    
    def handle_signup(self):
        """Handle sign up button click"""
        email = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text()
        repeat_password = self.ui.lineEdit_3.text()
        
        # Validate inputs
        if not email or not password or not repeat_password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        # Check if passwords match
        if password != repeat_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            self.ui.lineEdit_2.clear()
            self.ui.lineEdit_3.clear()
            return
        
        # Validate password strength
        valid, message = self.validate_password(password)
        if not valid:
            QMessageBox.warning(self, "Error", message)
            return
        
        # Register user
        success, message = self.model.register_user(email, password)
        
        if success:
            # Automatically log in the user after registration
            self.model.login_user(email, password)
            self.login_successful.emit(email)
            self.accept()  # Close dialog with success
        else:
            QMessageBox.warning(self, "Registration Failed", message)
    
    def open_login(self):
        """Return to login window"""
        self.reject()  # Close dialog without success
