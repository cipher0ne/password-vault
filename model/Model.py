from typing import Optional, List, Dict
from .DatabaseManager import DatabaseManager
from .AuthService import AuthService
from .PasswordService import PasswordService


class PasswordVaultModel:
    """Facade for managing users and their password entries using encrypted SQLite
    
    This class delegates to separate service classes for better separation of concerns:
    - DatabaseManager: handles database connections and encryption
    - AuthService: handles user authentication
    - PasswordService: handles password entry CRUD operations
    """

    def __init__(self, db_file: Optional[str] = None, master_key: str = "default_secure_key_change_in_production"):
        # Initialize core services
        self.db_manager = DatabaseManager(db_file, master_key)
        self.auth_service = AuthService(self.db_manager)
        self.password_service = PasswordService(self.db_manager)
    
    @property
    def current_user(self) -> Optional[str]:
        """Get current user"""
        return self.auth_service.current_user
    
    @current_user.setter
    def current_user(self, email: Optional[str]):
        """Set current user for both auth and password services"""
        self.auth_service.current_user = email
        self.password_service.current_user = email
    
    # ==================== Database Manager Methods ====================
    
    @staticmethod
    def _get_data_directory():
        """Get the appropriate data directory for the current OS"""
        return DatabaseManager.get_data_directory()
    
    def _get_connection(self):
        """Get database connection"""
        return self.db_manager.get_connection()
    
    def _encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.db_manager.encrypt(data)
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.db_manager.decrypt(encrypted_data)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return DatabaseManager.hash_password(password)
    
    # ==================== Auth Service Methods ====================
    
    def register_user(self, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        return self.auth_service.register_user(email, password)
    
    def login_user(self, email: str, password: str) -> tuple[bool, str]:
        """Authenticate user"""
        success, message = self.auth_service.login_user(email, password)
        if success:
            # Sync current user to password service
            self.password_service.current_user = self.auth_service.current_user
        return success, message
    
    def logout(self):
        """Logout current user"""
        self.auth_service.logout()
        self.password_service.current_user = None
    
    # ==================== Password Service Methods ====================
    
    def add_password_entry(self, name: str, username: str, password: str, url: str = "") -> bool:
        """Add a new password entry for current user"""
        return self.password_service.add_password_entry(name, username, password, url)
    
    def get_password_entries(self) -> List[Dict]:
        """Get all password entries for current user"""
        return self.password_service.get_password_entries()
    
    def delete_password_entry(self, index: int) -> bool:
        """Delete a password entry by index"""
        return self.password_service.delete_password_entry(index)
    
    def delete_all_entries(self) -> bool:
        """Delete all password entries for current user"""
        return self.password_service.delete_all_entries()
    
    def update_password_entry(self, index: int, name: str, username: str, password: str, url: str = "") -> bool:
        """Update a password entry by index"""
        return self.password_service.update_password_entry(index, name, username, password, url)
    
    def move_entry_up(self, index: int) -> bool:
        """Move an entry up in custom order"""
        return self.password_service.move_entry_up(index)
    
    def move_entry_down(self, index: int) -> bool:
        """Move an entry down in custom order"""
        return self.password_service.move_entry_down(index)
    
    def increment_copy_count(self, index: int) -> None:
        """Increment the copy_count for a password entry by index"""
        self.password_service.increment_copy_count(index)
    
    def get_sorted_entries(self, sort_type: str = "custom", search_query: str = "") -> List[Dict]:
        """Get password entries sorted by specified type and optionally filtered by search"""
        return self.password_service.get_sorted_entries(sort_type, search_query)
