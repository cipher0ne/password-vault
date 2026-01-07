#!/usr/bin/env python3
import sys
import os

# Disable Qt accessibility to suppress warnings
os.environ['QT_ACCESSIBILITY'] = '0'
os.environ['QT_LINUX_ACCESSIBILITY_ALWAYS_ON'] = '0'
os.environ['NO_AT_BRIDGE'] = '1'

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from model.Model import PasswordVaultModel
from ViewModel.LoginWindow import LoginWindow
from ViewModel.MainWindow import MainWindow
import platform


def get_app_icon():
    """Get appropriate icon format for the platform"""
    if platform.system() == "Windows":
        # Use ICO on Windows for best compatibility
        return QIcon("icons/app_icon.ico")
    else:
        # Use PNG on Linux/macOS for better quality
        icon = QIcon()
        # Add multiple sizes for better rendering at different DPIs
        for size in [16, 32, 48, 64, 128, 256]:
            icon.addFile(f"icons/app_icon_{size}.png")
        return icon


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application icon (for taskbar, alt-tab, etc.)
    app_icon = get_app_icon()
    app.setWindowIcon(app_icon)
    
    # Create the data model
    model = PasswordVaultModel()
    
    # Create and show login window
    login_window = LoginWindow(model)
    login_window.setWindowIcon(app_icon)
    
    # Keep reference to main window to prevent garbage collection
    main_window = None
    
    # Connect login success to opening main window
    def on_login_success(email):
        """Handle successful login"""
        nonlocal main_window
        print(f"Login successful for: {email}")
        try:
            main_window = MainWindow(model)
            print("MainWindow created")
            
            # Connect logout signal
            main_window.logout_requested.connect(on_logout)
            
            main_window.show()
            print("MainWindow shown")
        except Exception as e:
            print(f"Error creating MainWindow: {e}")
            import traceback
            traceback.print_exc()
    
    def on_logout():
        """Handle logout - return to login screen"""
        # Clear and reset login window
        login_window.ui.lineEdit.clear()
        login_window.ui.lineEdit_2.clear()
        login_window.ui.checkBox.setChecked(False)
        login_window.ui.checkBox.setEnabled(False)
        login_window.show()
    
    login_window.login_successful.connect(on_login_success)
    
    # Show the login window
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
