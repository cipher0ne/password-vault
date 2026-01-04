from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Signal, QByteArray, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from View.PasswordItem_ui import Ui_Form
import re


class PasswordItemWidget(QWidget):
    """Custom widget for displaying a password entry with up/down buttons"""
    
    move_up_clicked = Signal(int)  # Emits the index
    move_down_clicked = Signal(int)
    item_clicked = Signal(int)
    edit_clicked = Signal(int)  # Emits the index for editing
    
    def __init__(self, index: int, name: str, username: str, password: str = "", url: str = "", parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.index = index
        self.name = name
        self.username = username
        self.password = password
        self.url = url
        self.password_visible = False
        
        # Store original tooltips
        self.original_tooltip_username = self.ui.toolButton.toolTip()
        self.original_tooltip_password = self.ui.toolButton_2.toolTip()
        self.original_tooltip_url = self.ui.toolButton_3.toolTip()
        
        # Set the text content
        self.ui.nameLabel.setText(name)
        self.ui.label.setText(username)  # Username label
        self.ui.label_2.setText("*" * len(password))  # Password label (hidden)
        self.ui.label_3.setText(url if url else "No URL")  # URL label
        
        # Set theme-aware icons
        self._set_theme_icons()
        
        # Connect button signals
        self.ui.upButton.clicked.connect(lambda: self.move_up_clicked.emit(self.index))
        self.ui.downButton.clicked.connect(lambda: self.move_down_clicked.emit(self.index))
        
        # Connect copy buttons
        self.ui.toolButton.clicked.connect(self.copy_username)
        self.ui.toolButton_2.clicked.connect(self.copy_password)
        self.ui.toolButton_3.clicked.connect(self.copy_url)
        self.ui.toolButton_4.clicked.connect(self.toggle_password_visibility)
        self.ui.toolButton_5.clicked.connect(lambda: self.edit_clicked.emit(self.index))
        
        # Make the whole widget clickable
        self.mousePressEvent = lambda event: self.item_clicked.emit(self.index)
    
    def _recolor_svg_icon(self, svg_path: str, color: QColor, size: int = 16) -> QIcon:
        """Recolor an SVG icon to match the theme"""
        try:
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Replace all fill colors in the SVG with the theme color
            # This regex replaces fill="..." with the new color
            color_hex = color.name()
            svg_content = re.sub(r'fill="[^"]*"', f'fill="{color_hex}"', svg_content)
            svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color_hex}"', svg_content)
            
            # If no fill/stroke attributes, add fill to the svg tag
            if 'fill=' not in svg_content:
                svg_content = svg_content.replace('<svg', f'<svg fill="{color_hex}"')
            
            # Render the modified SVG
            svg_bytes = QByteArray(svg_content.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return QIcon(pixmap)
        except Exception as e:
            print(f"Error recoloring icon {svg_path}: {e}")
            return QIcon()
    
    def _set_theme_icons(self):
        """Set icons that adapt to system theme"""
        # Get the text color from palette to use for icons
        text_color = self.palette().text().color()
        
        # Recolor the custom SVG icons using actual file paths
        self.copy_icon = self._recolor_svg_icon("icons/copy.svg", text_color)
        self.show_icon = self._recolor_svg_icon("icons/show.svg", text_color)
        self.hide_icon = self._recolor_svg_icon("icons/hide.svg", text_color)
        self.edit_icon = self._recolor_svg_icon("icons/edit.svg", text_color)
        
        # Apply the recolored icons
        if not self.copy_icon.isNull():
            self.ui.toolButton.setIcon(self.copy_icon)
            self.ui.toolButton_2.setIcon(self.copy_icon)
            self.ui.toolButton_3.setIcon(self.copy_icon)
        
        if not self.show_icon.isNull():
            self.ui.toolButton_4.setIcon(self.show_icon)
        
        if not self.edit_icon.isNull():
            self.ui.toolButton_5.setIcon(self.edit_icon)
    
    def _show_copied_tooltip(self, button):
        """Temporarily show 'Copied!' tooltip"""
        original_tooltip = button.toolTip()
        button.setToolTip("✓ Copied!")
        
        # Store original to restore later
        def restore_tooltip():
            button.setToolTip(original_tooltip if original_tooltip else "")
        
        # Reset tooltip after delay
        QTimer.singleShot(1500, restore_tooltip)
    
    def copy_username(self):
        """Copy username to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.username)
        self._show_copied_tooltip(self.ui.toolButton)
    
    def copy_password(self):
        """Copy password to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password)
        self._show_copied_tooltip(self.ui.toolButton_2)
    
    def copy_url(self):
        """Copy URL to clipboard"""
        if self.url:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.url)
            self._show_copied_tooltip(self.ui.toolButton_3)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.ui.label_2.setText(self.password)
            if not self.hide_icon.isNull():
                self.ui.toolButton_4.setIcon(self.hide_icon)
            self.ui.toolButton_4.setToolTip("Hide password")
        else:
            self.ui.label_2.setText("*" * len(self.password))
            if not self.show_icon.isNull():
                self.ui.toolButton_4.setIcon(self.show_icon)
            self.ui.toolButton_4.setToolTip("Show password")
    
    def set_buttons_enabled(self, up_enabled: bool, down_enabled: bool):
        """Enable/disable up and down buttons"""
        self.ui.upButton.setEnabled(up_enabled)
        self.ui.downButton.setEnabled(down_enabled)
    
    def set_buttons_visible(self, visible: bool):
        """Show/hide up and down buttons"""
        self.ui.upButton.setVisible(visible)
        self.ui.downButton.setVisible(visible)
    
    def update_index(self, new_index: int):
        """Update the stored index"""
        self.index = new_index
