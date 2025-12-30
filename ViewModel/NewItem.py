from PySide6.QtWidgets import QDialog, QMessageBox
from View.NewItem_ui import Ui_Dialog


class NewItemWindow(QDialog):
    """New item window ViewModel"""
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_add)
        self.ui.pushButton_2.clicked.connect(self.handle_cancel)
        
        # Make password field hidden
        self.ui.lineEdit_3.setEchoMode(self.ui.lineEdit_3.EchoMode.Password)
        
        # Press Enter to add (from last field)
        self.ui.lineEdit_4.returnPressed.connect(self.handle_add)
    
    def handle_add(self):
        """Handle add button click"""
        name = self.ui.lineEdit.text().strip()
        username = self.ui.lineEdit_2.text().strip()
        password = self.ui.lineEdit_3.text()
        url = self.ui.lineEdit_4.text().strip()
        
        # Validate required fields
        if not name:
            QMessageBox.warning(self, "Error", "Please enter an item name")
            return
        
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a login/username")
            return
        
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return
        
        # Add the entry
        success = self.model.add_password_entry(name, username, password, url)
        
        if success:
            QMessageBox.information(self, "Success", "Password entry added successfully!")
            self.accept()  # Close dialog with success
        else:
            QMessageBox.warning(self, "Error", "Failed to add password entry")
    
    def handle_cancel(self):
        """Handle cancel button click"""
        self.reject()  # Close dialog without success
