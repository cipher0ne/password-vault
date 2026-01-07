from PySide6.QtWidgets import QMainWindow, QMessageBox, QListWidget, QListWidgetItem, QMenu, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QApplication
from PySide6.QtCore import QSize, Signal, QSettings, QByteArray
from PySide6.QtGui import QActionGroup, QIcon, QPixmap, QPalette, QColor
from PySide6.QtSvg import QSvgRenderer
from View.MainWindow_ui import Ui_MainWindow
from ViewModel.PasswordItemWidget import PasswordItemWidget
from ViewModel.PasswordGeneratorWidget import PasswordGeneratorWidget
from ViewModel.AboutDialog import AboutDialog
from ViewModel.ItemPopup import ItemPopupDialog
import re


class MainWindow(QMainWindow):
    """Main window ViewModel"""
    
    logout_requested = Signal()  # Signal emitted when user logs out
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = model
        self.settings = QSettings("PasswordVault", "MainWindow")
        
        # Set window icon from application icon
        self.setWindowIcon(QApplication.instance().windowIcon())
        
        # Create stacked widget to replace verticalLayout_2 content
        self.stacked_widget = QStackedWidget()
        
        # Page 0: Vault view - reparent existing widgets
        self.vault_widget = QWidget()
        vault_layout = QVBoxLayout(self.vault_widget)
        vault_layout.setContentsMargins(0, 0, 0, 0)
        
        # Move existing widgets from UI to vault layout
        vault_layout.addWidget(self.ui.lineEdit)  # Search bar
        
        # Add button row
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ui.pushButton_4)  # Add button
        button_layout.addWidget(self.ui.pushButton_3)  # Remove button
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(self.ui.toolButton)  # Sort button
        vault_layout.addLayout(button_layout)
        
        # Replace QListView with QListWidget
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        self.ui.listView.setParent(None)  # Remove old list view
        vault_layout.addWidget(self.list_widget)
        
        self.stacked_widget.addWidget(self.vault_widget)
        
        # Page 1: Password Generator view
        self.generator_widget = PasswordGeneratorWidget()
        self.stacked_widget.addWidget(self.generator_widget)
        
        # Clear verticalLayout_2 and add stacked widget
        while self.ui.verticalLayout_2.count():
            child = self.ui.verticalLayout_2.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        self.ui.verticalLayout_2.addWidget(self.stacked_widget)
        
        # Load saved sort type
        self.current_sort = self.settings.value("sortType", "custom", type=str)
        self.search_query = ""
        self.selected_index = -1
        self.current_popup = None  # Track the currently open popup
        
        # Update UI with user info
        if self.model.current_user:
            self.ui.label_2.setText(self.model.current_user)
        
        # Apply theme-aware icons
        self._apply_themed_icons()
        
        # Connect buttons
        self.ui.pushButton.clicked.connect(self.handle_logout)
        self.ui.pushButton_4.clicked.connect(self.add_new_item)
        self.ui.pushButton_3.clicked.connect(self.remove_selected_item)
        self.ui.toolButton.clicked.connect(self.show_sort_menu)
        
        # Connect view switching buttons
        self.ui.pushButton_7.clicked.connect(lambda: self.switch_view(0))  # Vault button
        self.ui.pushButton_6.clicked.connect(lambda: self.switch_view(1))  # Password generator button
        
        # Connect search
        self.ui.lineEdit.textChanged.connect(self.on_search_changed)
        
        # Connect menu actions
        self.ui.actionAbout.triggered.connect(self.show_about_dialog)
        self.ui.actionRemove_all_passwords.triggered.connect(self.remove_all_passwords)
        
        # Load password entries
        self.refresh_list()
        
        # Set initial view to vault
        self.switch_view(0)
        
        # Center the window on screen
        self.center_window()
    
    def _recolor_svg_icon(self, svg_path: str, color: QColor, size: int = 24) -> QIcon:
        """Recolor an SVG icon to match the theme"""
        try:
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Replace all fill colors in the SVG with the theme color
            color_hex = color.name()
            svg_content = re.sub(r'fill="[^"]*"', f'fill="{color_hex}"', svg_content)
            svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color_hex}"', svg_content)
            
            # If no fill/stroke attributes, add fill to the svg tag
            if 'fill=' not in svg_content:
                svg_content = svg_content.replace('<svg', f'<svg fill="{color_hex}"')
            
            # Render the modified SVG
            svg_bytes = QByteArray(svg_content.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(0x00000000)  # Transparent background
            
            from PySide6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return QIcon(pixmap)
        except Exception as e:
            print(f"Error recoloring icon {svg_path}: {e}")
            return QIcon()
    
    def _apply_themed_icons(self):
        """Apply theme-aware coloring to SVG icons"""
        # Get the current text color from the palette
        text_color = self.palette().color(QPalette.ColorRole.WindowText)
        
        # Recolor and set the sort button icon
        self.sort_icon = self._recolor_svg_icon("icons/sort.svg", text_color, size=24)
        self.ui.toolButton.setIcon(self.sort_icon)
        # Explicitly set icon size for Windows compatibility
        self.ui.toolButton.setIconSize(QSize(24, 24))
    
    def switch_view(self, index: int):
        """Switch between vault and password generator views"""
        self.stacked_widget.setCurrentIndex(index)
        # Update button states
        self.ui.pushButton_7.setChecked(index == 0)
        self.ui.pushButton_6.setChecked(index == 1)
    
    def on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_query = text
        self.refresh_list()
    
    def show_sort_menu(self):
        """Show sorting options menu"""
        menu = QMenu(self)
        
        # Create action group for radio buttons
        action_group = QActionGroup(self)
        action_group.setExclusive(True)
        
        # Create actions with radio button behavior
        custom_action = menu.addAction("Custom Order")
        custom_action.setCheckable(True)
        custom_action.setChecked(self.current_sort == "custom")
        custom_action.setActionGroup(action_group)
        custom_action.triggered.connect(lambda: self.set_sort_type("custom"))
        
        asc_action = menu.addAction("Alphabetical (A-Z)")
        asc_action.setCheckable(True)
        asc_action.setChecked(self.current_sort == "alphabetical_asc")
        asc_action.setActionGroup(action_group)
        asc_action.triggered.connect(lambda: self.set_sort_type("alphabetical_asc"))
        
        desc_action = menu.addAction("Alphabetical (Z-A)")
        desc_action.setCheckable(True)
        desc_action.setChecked(self.current_sort == "alphabetical_desc")
        desc_action.setActionGroup(action_group)
        desc_action.triggered.connect(lambda: self.set_sort_type("alphabetical_desc"))
        
        freq_action = menu.addAction("Frequently Used")
        freq_action.setCheckable(True)
        freq_action.setChecked(self.current_sort == "frequently_used")
        freq_action.setActionGroup(action_group)
        freq_action.triggered.connect(lambda: self.set_sort_type("frequently_used"))
        
        # Show menu at button position
        menu.exec(self.ui.toolButton.mapToGlobal(self.ui.toolButton.rect().bottomLeft()))
    
    def set_sort_type(self, sort_type: str):
        """Set the sorting type and refresh list"""
        self.current_sort = sort_type
        # Save sort preference
        self.settings.setValue("sortType", sort_type)
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
            item.setSizeHint(QSize(0, 80))  # Reduced height since UI is now simpler
            
            # Create custom widget with all data
            widget = PasswordItemWidget(
                i, 
                entry['name'], 
                entry['username'],
                entry.get('password', ''),
                entry.get('url', ''),
                model=self.model
            )
            
            # Connect signals
            widget.move_up_clicked.connect(self.move_item_up)
            widget.move_down_clicked.connect(self.move_item_down)
            widget.item_clicked.connect(self.on_item_clicked)
            widget.edit_clicked.connect(self.edit_item)
            
            # Show/hide up/down buttons based on sort mode
            if self.current_sort == "custom":
                widget.set_buttons_visible(True)
                # Enable/disable buttons based on position
                widget.set_buttons_enabled(i > 0, i < len(entries) - 1)
            else:
                # Hide up/down buttons when not in custom sort mode
                widget.set_buttons_visible(False)
            
            # Add to list
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
        
        # Update remove button state
        self.ui.pushButton_3.setEnabled(len(entries) > 0 and self.selected_index >= 0)
    
    def on_item_clicked(self, index: int):
        """Handle item click - show popup with details"""
        self.selected_index = index
        self.list_widget.setCurrentRow(index)
        self.ui.pushButton_3.setEnabled(True)
        
        # Close the previous popup if it exists
        if self.current_popup is not None:
            self.current_popup.close()
            self.current_popup = None
        
        # Get the entry data
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        if index < len(entries):
            entry = entries[index]
            
            # Create and show the popup dialog (non-modal)
            self.current_popup = ItemPopupDialog(
                index,
                entry['name'],
                entry['username'],
                entry.get('password', ''),
                entry.get('url', ''),
                parent=self,
                model=self.model
            )
            # Connect the close event to clear our reference
            self.current_popup.finished.connect(lambda: setattr(self, 'current_popup', None))
            self.current_popup.show()  # Use show() instead of exec() for non-modal dialog
    
    def move_item_up(self, index: int):
        """Move item up in custom order"""
        if self.current_sort != "custom":
            QMessageBox.warning(self, "Error", "Items can only be reordered in Custom Order mode")
            return
        
        if index <= 0:
            return
        
        # Get all entries in custom order (no search filter for reordering)
        all_entries = self.model.get_password_entries()
        if index >= len(all_entries):
            return
        
        # Move in model
        if self.model.move_entry_up(index):
            # Update selection
            if self.selected_index == index:
                self.selected_index = index - 1
            self.refresh_list()
    
    def move_item_down(self, index: int):
        """Move item down in custom order"""
        if self.current_sort != "custom":
            QMessageBox.warning(self, "Error", "Items can only be reordered in Custom Order mode")
            return
        
        # Get all entries in custom order (no search filter for reordering)
        all_entries = self.model.get_password_entries()
        if index < 0 or index >= len(all_entries) - 1:
            return
        
        # Move in model
        if self.model.move_entry_down(index):
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
    
    def edit_item(self, index: int):
        """Edit an existing password entry"""
        from ViewModel.NewItem import NewItemWindow
        
        # Get the current sorted/filtered entries
        entries = self.model.get_sorted_entries(self.current_sort, self.search_query)
        
        if index < 0 or index >= len(entries):
            QMessageBox.warning(self, "Error", "Invalid item index")
            return
        
        # Get the entry data
        entry_data = entries[index]
        
        # Find the actual index in the unfiltered list (for updating)
        all_entries = self.model.get_sorted_entries("custom", "")
        actual_index = None
        for i, e in enumerate(all_entries):
            if (e['name'] == entry_data['name'] and 
                e['username'] == entry_data['username'] and
                e['custom_order'] == entry_data['custom_order']):
                actual_index = i
                break
        
        if actual_index is None:
            QMessageBox.warning(self, "Error", "Could not find entry to edit")
            return
        
        # Open dialog in edit mode
        edit_window = NewItemWindow(
            self.model, 
            self, 
            edit_mode=True, 
            edit_index=actual_index, 
            entry_data=entry_data
        )
        
        if edit_window.exec():
            # Refresh the list after editing
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
                f"Are you sure you want to delete '{entry['name']}'?\nThis action cannot be reversed.",
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
            f"Are you sure you want to delete ALL {len(entries)} password(s)?\nThis action cannot be reversed.",
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
            # Clear saved email and remember me preference
            settings = QSettings("PasswordVault", "LoginPreferences")
            settings.setValue("rememberEmail", False)
            settings.remove("savedEmail")
            
            # Logout from model
            self.model.logout()
            
            # Emit signal to show login window
            self.logout_requested.emit()
            self.close()
    
    def center_window(self):
        """Center the window on the screen"""
        screen = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def show_about_dialog(self):
        """Show the About dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
