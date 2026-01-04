from PySide6.QtWidgets import QDialog, QMessageBox
from View.NewItem_ui import Ui_Dialog


class NewItemWindow(QDialog):
    """New item window ViewModel"""
    
    def __init__(self, model, parent=None, edit_mode=False, edit_index=None, entry_data=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model
        self.edit_mode = edit_mode
        self.edit_index = edit_index
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_add)
        self.ui.pushButton_2.clicked.connect(self.handle_cancel)
        
        # Make password field hidden
        self.ui.lineEdit_3.setEchoMode(self.ui.lineEdit_3.EchoMode.Password)
        
        # Press Enter to add (from last field)
        self.ui.lineEdit_4.returnPressed.connect(self.handle_add)
        
        # If in edit mode, pre-fill the fields
        if edit_mode and entry_data:
            self.ui.lineEdit.setText(entry_data.get('name', ''))
            self.ui.lineEdit_2.setText(entry_data.get('username', ''))
            self.ui.lineEdit_3.setText(entry_data.get('password', ''))
            self.ui.lineEdit_4.setText(entry_data.get('url', ''))
            self.setWindowTitle("Edit Password Entry")
    
    def handle_add(self):
        """Handle add/update button click"""
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
        
        # Update or add the entry based on mode
        if self.edit_mode:
            success = self.model.update_password_entry(self.edit_index, name, username, password, url)
        else:
            success = self.model.add_password_entry(name, username, password, url)
        
        if success:
            self.accept()  # Close dialog with success
        else:
            action = "update" if self.edit_mode else "add"
            QMessageBox.warning(self, "Error", f"Failed to {action} password entry")
    
    def handle_cancel(self):
        """Handle cancel button click"""
        self.reject()  # Close dialog without success
