import base64
import hashlib
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DatabaseManager:
    """Manages database connections, encryption, and schema initialization"""

    @staticmethod
    def get_data_directory():
        """Get the appropriate data directory for the current OS"""
        if sys.platform == "win32":
            # Windows: %APPDATA%/PasswordVault
            appdata = os.getenv('APPDATA')
            data_dir = Path(appdata) / "PasswordVault"
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/PasswordVault
            data_dir = Path.home() / "Library" / "Application Support" / "PasswordVault"
        else:
            # Linux: ~/.local/share/PasswordVault
            data_dir = Path.home() / ".local" / "share" / "PasswordVault"
        
        # Create directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def __init__(self, db_file: Optional[str] = None, master_key: str = "default_secure_key_change_in_production"):
        # Use default location if no db_file specified
        if db_file is None:
            data_dir = self.get_data_directory()
            self.db_file = str(data_dir / "vault_data.db")
        else:
            self.db_file = db_file
        self.master_key = master_key
        self._cipher = self._create_cipher(master_key)
        self._init_database()
    
    def _create_cipher(self, password: str):
        """Create Fernet cipher from password"""
        # Derive a key from the password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'password_vault_salt',  # In production, use a random salt stored separately
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self._cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self._cipher.decrypt(encrypted_data.encode()).decode()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        
        # Create passwords table (password field will be encrypted)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                url TEXT,
                custom_order INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        
        # Add copy_count column to passwords table if it doesn't exist
        cursor.execute("PRAGMA table_info(passwords)")
        columns = [row[1] for row in cursor.fetchall()]
        if "copy_count" not in columns:
            cursor.execute("ALTER TABLE passwords ADD COLUMN copy_count INTEGER NOT NULL DEFAULT 0")
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_passwords_user 
            ON passwords(user_email)
        """)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
