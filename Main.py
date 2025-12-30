#!/usr/bin/env python3
"""
Password Vault Application
A secure password manager with user authentication
"""

import sys
from PySide6.QtWidgets import QApplication
from model.Model import PasswordVaultModel
from ViewModel.LoginWindow import LoginWindow
from ViewModel.MainWindow import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create the data model
    model = PasswordVaultModel()
    
    # Create and show login window
    login_window = LoginWindow(model)
    
    # Keep reference to main window to prevent garbage collection
    main_window = None
    
    # Connect login success to opening main window
    def on_login_success(email):
        """Handle successful login"""
        nonlocal main_window
        print(f"Login successful for: {email}")  # Debug
        try:
            main_window = MainWindow(model)
            print("MainWindow created")  # Debug
            main_window.show()
            print("MainWindow shown")  # Debug
            
            # When main window is closed, show login again
            def on_main_window_closed():
                login_window.ui.lineEdit_2.clear()  # Clear password field
                login_window.show()
            
            main_window.destroyed.connect(on_main_window_closed)
        except Exception as e:
            print(f"Error creating MainWindow: {e}")  # Debug
            import traceback
            traceback.print_exc()
    
    login_window.login_successful.connect(on_login_success)
    
    # Show the login window
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
