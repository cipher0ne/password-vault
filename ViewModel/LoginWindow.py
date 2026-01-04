from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Signal, QSettings
from View.LoginWindow_ui import Ui_Dialog


class LoginWindow(QDialog):
    """Login window ViewModel"""
    
    login_successful = Signal(str)  # Signal emitted with user email on successful login
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model
        self.settings = QSettings("PasswordVault", "LoginPreferences")
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_login)
        self.ui.pushButton_2.clicked.connect(self.open_signup)
        
        # Make password field hidden
        self.ui.lineEdit_2.setEchoMode(self.ui.lineEdit_2.EchoMode.Password)
        
        # Press Enter to login
        self.ui.lineEdit.returnPressed.connect(self.handle_login)
        self.ui.lineEdit_2.returnPressed.connect(self.handle_login)
        
        # Enable checkbox when user types email
        self.ui.lineEdit.textChanged.connect(self.check_email_entered)
        
        # Load saved email if remember me was checked
        self.load_saved_email()
    
    def check_email_entered(self, text):
        """Enable checkbox when email is entered"""
        self.ui.checkBox.setEnabled(len(text.strip()) > 0)
    
    def load_saved_email(self):
        """Load saved email if remember me was enabled"""
        remember = self.settings.value("rememberEmail", False, type=bool)
        if remember:
            saved_email = self.settings.value("savedEmail", "", type=str)
            if saved_email:
                self.ui.lineEdit.setText(saved_email)
                self.ui.checkBox.setChecked(True)
                self.ui.checkBox.setEnabled(True)
    
    def handle_login(self):
        """Handle login button click"""
        email = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
        
        success, message = self.model.login_user(email, password)
        
        if success:
            # Save email if remember me is checked
            if self.ui.checkBox.isChecked():
                self.settings.setValue("rememberEmail", True)
                self.settings.setValue("savedEmail", email)
            else:
                self.settings.setValue("rememberEmail", False)
                self.settings.remove("savedEmail")
            
            self.login_successful.emit(email)
            self.accept()  # Close dialog with success
        else:
            QMessageBox.warning(self, "Login Failed", message)
            self.ui.lineEdit_2.clear()
    
    def open_signup(self):
        """Open the sign up window"""
        from ViewModel.SignUpWindow import SignUpWindow
        signup_window = SignUpWindow(self.model, self)
        # Connect signup success to login success
        signup_window.login_successful.connect(self.login_successful.emit)
        self.hide()  # Hide login window while signup is open
        if signup_window.exec() == QDialog.DialogCode.Accepted:
            # User successfully signed up and logged in
            self.accept()  # Close login window
        else:
            self.show()  # Show login window again if signup was cancelled
