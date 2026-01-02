from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QByteArray, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from View.PasswordGenerator_ui import Ui_Form
import re


class PasswordGeneratorWidget(QWidget):
    """Password Generator widget with theme-aware icons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Set theme-aware icons
        self._set_theme_icons()
        
        # Connect copy button
        self.ui.toolButton.clicked.connect(self.copy_password)
        # Connect regenerate button
        self.ui.toolButton_2.clicked.connect(self.generate_password)
    
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
        
        # Apply the recolored icons to all copy buttons
        if not self.copy_icon.isNull():
            self.ui.toolButton.setIcon(self.copy_icon)
            self.ui.toolButton_5.setIcon(self.copy_icon)
            self.ui.toolButton_6.setIcon(self.copy_icon)
            self.ui.toolButton_7.setIcon(self.copy_icon)
    
    def copy_password(self):
        """Copy generated password to clipboard"""
        password = self.ui.label.text()
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self._show_copied_tooltip()
    
    def _show_copied_tooltip(self):
        """Temporarily show 'Copied!' tooltip"""
        original_tooltip = self.ui.toolButton.toolTip()
        self.ui.toolButton.setToolTip("✓ Copied!")
        
        # Store original to restore later
        def restore_tooltip():
            self.ui.toolButton.setToolTip(original_tooltip if original_tooltip else "")
        
        # Reset tooltip after delay
        QTimer.singleShot(1500, restore_tooltip)
    
    def generate_password(self):
        """Generate a new password based on selected options"""
        # TODO: Implement password generation logic
        import random
        import string
        
        length = 16  # Default length
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        self.ui.label.setText(password)
