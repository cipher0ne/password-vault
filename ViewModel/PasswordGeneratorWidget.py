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
        
        # Initialize password length
        self.password_length = 12  # Default length
        self.ui.label_2.setText(str(self.password_length))
        
        # Connect copy button
        self.ui.toolButton.clicked.connect(self.copy_password)
        # Connect regenerate button
        self.ui.toolButton_2.clicked.connect(self.generate_password)
        # Connect length adjustment buttons
        self.ui.toolButton_3.clicked.connect(self.decrease_length)  # Minus button
        self.ui.toolButton_4.clicked.connect(self.increase_length)  # Plus button
        
        # Connect checkboxes to regenerate password
        self.ui.checkBox.toggled.connect(self.generate_password)    # A-Z
        self.ui.checkBox_2.toggled.connect(self.generate_password)  # a-z
        self.ui.checkBox_3.toggled.connect(self.generate_password)  # 0-9
        self.ui.checkBox_4.toggled.connect(self.generate_password)  # Special chars
        
        # Generate initial password
        self.generate_password()
    
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
        
        # Recolor the custom SVG icon using actual file path
        self.copy_icon = self._recolor_svg_icon("icons/copy.svg", text_color)
        
        # Apply the recolored icon to the copy button
        if not self.copy_icon.isNull():
            self.ui.toolButton.setIcon(self.copy_icon)
    
    def copy_password(self):
        """Copy generated password to clipboard"""
        # Get the password without line breaks
        password = self.ui.label.text().replace('\n', '')
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
        import random
        import string
        
        # Build character sets for each category
        categories = []
        all_chars = ""
        
        if self.ui.checkBox.isChecked():  # A-Z
            uppercase = string.ascii_uppercase
            categories.append(uppercase)
            all_chars += uppercase
        
        if self.ui.checkBox_2.isChecked():  # a-z
            lowercase = string.ascii_lowercase
            categories.append(lowercase)
            all_chars += lowercase
        
        if self.ui.checkBox_3.isChecked():  # 0-9
            digits = string.digits
            categories.append(digits)
            all_chars += digits
        
        if self.ui.checkBox_4.isChecked():  # Special characters
            special = "!@#$%^&*"  # Only the specific characters shown in label
            categories.append(special)
            all_chars += special
        
        # If no character types selected, use all
        if not categories:
            uppercase = string.ascii_uppercase
            lowercase = string.ascii_lowercase
            digits = string.digits
            special = "!@#$%^&*"
            categories = [uppercase, lowercase, digits, special]
            all_chars = uppercase + lowercase + digits + special
        
        # Ensure password is long enough for at least one char from each category
        length = max(self.password_length, len(categories))
        
        # Start with one character from each selected category
        password_chars = []
        for category in categories:
            password_chars.append(random.choice(category))
        
        # Fill remaining length with random characters from all categories
        remaining_length = length - len(categories)
        for _ in range(remaining_length):
            password_chars.append(random.choice(all_chars))
        
        # Shuffle to avoid predictable pattern
        random.shuffle(password_chars)
        
        password = ''.join(password_chars)
        
        # Insert line breaks every 20 characters
        formatted_password = '\n'.join(password[i:i+20] for i in range(0, len(password), 20))
        
        self.ui.label.setText(formatted_password)
    
    def increase_length(self):
        """Increase password length"""
        if self.password_length < 64:  # Max length
            self.password_length += 1
            self.ui.label_2.setText(str(self.password_length))
            self.generate_password()
    
    def decrease_length(self):
        """Decrease password length"""
        if self.password_length > 4:  # Min length
            self.password_length -= 1
            self.ui.label_2.setText(str(self.password_length))
            self.generate_password()
