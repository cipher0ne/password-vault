from typing import Optional
from .DatabaseManager import DatabaseManager


class AuthService:
    """Handles user authentication and session management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_user: Optional[str] = None
    
    def register_user(self, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        # Input validation
        if not email or not email.strip():
            return False, "Email cannot be empty"
        if not password or len(password) < 1:
            return False, "Password cannot be empty"
        if len(email) > 255:
            return False, "Email is too long"
        
        email = email.strip()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "User already exists"
            
            # Insert new user
            password_hash = DatabaseManager.hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash)
            )
            conn.commit()
            conn.close()
            return True, "Registration successful"
        except Exception as e:
            conn.close()
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str]:
        """Authenticate user"""
        # Input validation
        if not email or not email.strip():
            return False, "Email cannot be empty"
        if not password:
            return False, "Password cannot be empty"
        
        email = email.strip()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, "User not found"
        
        password_hash = DatabaseManager.hash_password(password)
        if result['password_hash'] == password_hash:
            self.current_user = email
            return True, "Login successful"
        return False, "Incorrect password"
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
