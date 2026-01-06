from PySide6.QtWidgets import QDialog, QApplication
from PySide6.QtCore import QByteArray, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from View.ItemPopup_ui import Ui_Dialog
import re


class ItemPopupDialog(QDialog):
    """Popup dialog for displaying password entry details"""
    
    def __init__(self, index: int, name: str, username: str, password: str = "", url: str = "", parent=None, model=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        self.index = index
        self.name = name
        self.username = username
        self.password = password
        self.url = url
        self.password_visible = False
        self.model = model
        
        # Set window title to item name
        self.setWindowTitle(name)
        
        # Set the text content
        self.ui.nameLabel.setText(name)
        self.ui.label.setText(username)  # Username label
        self.ui.label_2.setText("*" * len(password))  # Password label (hidden)
        self.ui.label_3.setText(url if url else "No URL")  # URL label
        
        # Set theme-aware icons
        self._set_theme_icons()
        
        # Connect copy buttons
        self.ui.toolButton.clicked.connect(self.copy_username)
        self.ui.toolButton_2.clicked.connect(self.copy_password)
        self.ui.toolButton_3.clicked.connect(self.copy_url)
        self.ui.toolButton_4.clicked.connect(self.toggle_password_visibility)
        
        # Connect close button
        self.ui.pushButton.clicked.connect(self.close)
        
        # Set dialog to be non-modal so main window remains accessible
        self.setModal(False)
    
    def _recolor_svg_icon(self, svg_path: str, color: QColor, size: int = 16) -> QIcon:
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
        
        # Apply the recolored icons
        if not self.copy_icon.isNull():
            self.ui.toolButton.setIcon(self.copy_icon)
            self.ui.toolButton_2.setIcon(self.copy_icon)
            self.ui.toolButton_3.setIcon(self.copy_icon)
        
        if not self.show_icon.isNull():
            self.ui.toolButton_4.setIcon(self.show_icon)
    
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
        if self.model:
            self.model.increment_copy_count(self.index)
    
    def copy_password(self):
        """Copy password to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password)
        self._show_copied_tooltip(self.ui.toolButton_2)
        if self.model:
            self.model.increment_copy_count(self.index)
    
    def copy_url(self):
        """Copy URL to clipboard"""
        if self.url:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.url)
            self._show_copied_tooltip(self.ui.toolButton_3)
            if self.model:
                self.model.increment_copy_count(self.index)
    
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
