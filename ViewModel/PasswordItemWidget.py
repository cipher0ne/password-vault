from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray
from View.PasswordItem_ui import Ui_Form
import re


class PasswordItemWidget(QWidget):
    """Custom widget for displaying a password entry with up/down buttons"""
    
    move_up_clicked = Signal(int)  # Emits the index
    move_down_clicked = Signal(int)
    item_clicked = Signal(int)
    edit_clicked = Signal(int)  # Emits the index for editing
    
    def __init__(self, index: int, name: str, username: str, password: str = "", url: str = "", parent=None, model=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.index = index
        self.name = name
        self.username = username
        self.password = password
        self.url = url
        self.model = model
        
        # Set the text content
        self.ui.nameLabel.setText(name)
        self.ui.label_3.setText(url if url else "No URL")  # URL label
        
        # Set theme-aware icons
        self._set_theme_icons()
        
        # Connect button signals
        self.ui.upButton.clicked.connect(lambda: self.move_up_clicked.emit(self.index))
        self.ui.downButton.clicked.connect(lambda: self.move_down_clicked.emit(self.index))
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
        self.edit_icon = self._recolor_svg_icon("icons/edit.svg", text_color)
        
        # Apply the recolored icons
        if not self.edit_icon.isNull():
            self.ui.toolButton_5.setIcon(self.edit_icon)
    
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
