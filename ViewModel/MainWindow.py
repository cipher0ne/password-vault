from PySide6.QtWidgets import QMainWindow, QMessageBox, QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import QSize
from View.MainWindow_ui import Ui_MainWindow
from ViewModel.PasswordItemWidget import PasswordItemWidget


class MainWindow(QMainWindow):
    """Main window ViewModel"""
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = model
        
        # Replace QListView with QListWidget for custom items
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        # Replace the listView in the layout
        layout = self.ui.verticalLayout_2
        old_list = self.ui.listView
        layout.replaceWidget(old_list, self.list_widget)
        old_list.deleteLater()
        self.ui.listView = self.list_widget
        
        # Current sort type and search query
        self.current_sort = "custom"  # Options: "custom", "alphabetical_asc", "alphabetical_desc"
        self.search_query = ""
        self.selected_index = -1
        
        # Update UI with user info
        if self.model.current_user:
            self.ui.label_2.setText(self.model.current_user)
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_logout)
        self.ui.pushButton_4.clicked.connect(self.add_new_item)
        self.ui.pushButton_3.clicked.connect(self.remove_selected_item)
        self.ui.pushButton_2.clicked.connect(self.show_sort_menu)
        
        # Connect search
        self.ui.lineEdit.textChanged.connect(self.on_search_changed)
        
        # Connect menu actions
        self.ui.actionRemove_all_passwords.triggered.connect(self.remove_all_passwords)
        
        # Load password entries
        self.refresh_list()
    
    def on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_query = text
        self.refresh_list()
    
    def show_sort_menu(self):
        """Show sorting options menu"""
        menu = QMenu(self)
        
        # Create actions
        custom_action = menu.addAction("Custom Order")
        custom_action.setCheckable(True)
        custom_action.setChecked(self.current_sort == "custom")
        custom_action.triggered.connect(lambda: self.set_sort_type("custom"))
        
        asc_action = menu.addAction("Alphabetical (A-Z)")
        asc_action.setCheckable(True)
        asc_action.setChecked(self.current_sort == "alphabetical_asc")
        asc_action.triggered.connect(lambda: self.set_sort_type("alphabetical_asc"))
        
        desc_action = menu.addAction("Alphabetical (Z-A)")
        desc_action.setCheckable(True)
        desc_action.setChecked(self.current_sort == "alphabetical_desc")
        desc_action.triggered.connect(lambda: self.set_sort_type("alphabetical_desc"))
        
        # Show menu at button position
        menu.exec(self.ui.pushButton_2.mapToGlobal(self.ui.pushButton_2.rect().bottomLeft()))
    
    def set_sort_type(self, sort_type: str):
        """Set the sorting type and refresh list"""
        self.current_sort = sort_type
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the password list with current sort and search"""
        # Clear the list
        self.list_widget.clear()
        
        # Get sorted and filtered entries
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        
        # Add custom widgets for each entry
        for i, entry in enumerate(entries):
            # Create list item
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 120))  # Increased height for more info
            
            # Create custom widget with all data
            widget = PasswordItemWidget(
                i, 
                entry['name'], 
                entry['username'],
                entry.get('password', ''),
                entry.get('url', '')
            )
            
            # Connect signals
            widget.move_up_clicked.connect(self.move_item_up)
            widget.move_down_clicked.connect(self.move_item_down)
            widget.item_clicked.connect(self.on_item_clicked)
            
            # Enable/disable buttons based on position (only for custom sort)
            if self.current_sort == "custom":
                widget.set_buttons_enabled(i > 0, i < len(entries) - 1)
            else:
                # Disable up/down buttons when not in custom sort mode
                widget.set_buttons_enabled(False, False)
            
            # Add to list
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
        
        # Update remove button state
        self.ui.pushButton_3.setEnabled(len(entries) > 0 and self.selected_index >= 0)
    
    def on_item_clicked(self, index: int):
        """Handle item click"""
        self.selected_index = index
        self.list_widget.setCurrentRow(index)
        self.ui.pushButton_3.setEnabled(True)
    
    def move_item_up(self, index: int):
        """Move item up in custom order"""
        if self.current_sort != "custom":
            QMessageBox.warning(self, "Error", "Items can only be reordered in Custom Order mode")
            return
        
        # Get the actual entry index from the model
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        if index > 0:
            # Find actual indices in the full list
            all_entries = self.model.get_password_entries()
            actual_index = all_entries.index(entries[index])
            
            # Move in model
            if self.model.move_entry_up(actual_index):
                # Update selection
                if self.selected_index == index:
                    self.selected_index = index - 1
                self.refresh_list()
    
    def move_item_down(self, index: int):
        """Move item down in custom order"""
        if self.current_sort != "custom":
            QMessageBox.warning(self, "Error", "Items can only be reordered in Custom Order mode")
            return
        
        # Get the actual entry index from the model
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        if index < len(entries) - 1:
            # Find actual indices in the full list
            all_entries = self.model.get_password_entries()
            actual_index = all_entries.index(entries[index])
            
            # Move in model
            if self.model.move_entry_down(actual_index):
                # Update selection
                if self.selected_index == index:
                    self.selected_index = index + 1
                self.refresh_list()
    
    def add_new_item(self):
        """Open the new item window"""
        from ViewModel.NewItem import NewItemWindow
        new_item_window = NewItemWindow(self.model, self)
        if new_item_window.exec():
            # Refresh the list after adding
            self.refresh_list()
    
    def remove_selected_item(self):
        """Remove the selected password entry"""
        if self.selected_index < 0:
            QMessageBox.warning(self, "Error", "No item selected")
            return
        
        # Get the filtered entries
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        
        if 0 <= self.selected_index < len(entries):
            entry = entries[self.selected_index]
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete '{entry['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Find actual index in full list
                all_entries = self.model.get_password_entries()
                actual_index = all_entries.index(entry)
                
                self.model.delete_password_entry(actual_index)
                self.selected_index = -1
                self.refresh_list()
    
    def remove_all_passwords(self):
        """Remove all password entries"""
        entries = self.model.get_password_entries()
        
        if not entries:
            QMessageBox.information(self, "Info", "No passwords to remove")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete ALL {len(entries)} password(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete_all_entries()
            self.selected_index = -1
            self.refresh_list()
            QMessageBox.information(self, "Success", "All passwords have been removed")
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.model.logout()
            self.close()
