import hashlib
import sqlite3
import base64
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordVaultModel:
    """Data model for managing users and their password entries using encrypted SQLite"""

    def increment_copy_count(self, index: int) -> None:
        """Increment the copy_count for a password entry by index"""
        if not self.current_user:
            return
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM passwords WHERE user_email = ? ORDER BY custom_order LIMIT 1 OFFSET ?",
            (self.current_user, index)
        )
        result = cursor.fetchone()
        if result:
            entry_id = result['id']
            cursor.execute("UPDATE passwords SET copy_count = copy_count + 1 WHERE id = ?", (entry_id,))
            conn.commit()
        conn.close()
    
    @staticmethod
    def _get_data_directory():
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
            data_dir = self._get_data_directory()
            self.db_file = str(data_dir / "vault_data.db")
        else:
            self.db_file = db_file
        self.master_key = master_key
        self.current_user: Optional[str] = None
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
    
    def _encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self._cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self._cipher.decrypt(encrypted_data.encode()).decode()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
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
        # Add copy_count column to passwords table
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
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "User already exists"
            
            # Insert new user
            password_hash = self._hash_password(password)
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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, "User not found"
        
        password_hash = self._hash_password(password)
        if result['password_hash'] == password_hash:
            self.current_user = email
            return True, "Login successful"
        return False, "Incorrect password"
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def add_password_entry(self, name: str, username: str, password: str, url: str = "") -> bool:
        """Add a new password entry for current user"""
        if not self.current_user:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the next order value
            cursor.execute(
                "SELECT COALESCE(MAX(custom_order), -1) + 1 FROM passwords WHERE user_email = ?",
                (self.current_user,)
            )
            next_order = cursor.fetchone()[0]
            
            # Encrypt the password before storing
            encrypted_password = self._encrypt(password)
            
            # Insert new password entry
            cursor.execute(
                """INSERT INTO passwords (user_email, name, username, password, url, custom_order)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.current_user, name, username, encrypted_password, url, next_order)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding password entry: {e}")
            return False
    
    def get_password_entries(self) -> List[Dict]:
        """Get all password entries for current user"""
        if not self.current_user:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT name, username, password, url, custom_order, copy_count 
               FROM passwords WHERE user_email = ? ORDER BY custom_order""",
            (self.current_user,)
        )
        
        entries = []
        for row in cursor.fetchall():
            # Decrypt password before returning
            try:
                decrypted_password = self._decrypt(row['password'])
            except:
                decrypted_password = ""  # Handle decryption errors gracefully
            
            entries.append({
                'name': row['name'],
                'username': row['username'],
                'password': decrypted_password,
                'url': row['url'],
                'custom_order': row['custom_order'],
                'copy_count': row['copy_count']
            })
        
        conn.close()
        return entries
    
    def delete_password_entry(self, index: int) -> bool:
        """Delete a password entry by index"""
        if not self.current_user:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get all entries to find the one at the given index
            cursor.execute(
                """SELECT id FROM passwords WHERE user_email = ? 
                   ORDER BY custom_order LIMIT 1 OFFSET ?""",
                (self.current_user, index)
            )
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            entry_id = result['id']
            
            # Delete the entry
            cursor.execute("DELETE FROM passwords WHERE id = ?", (entry_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error deleting password entry: {e}")
            return False
    
    def delete_all_entries(self) -> bool:
        """Delete all password entries for current user"""
        if not self.current_user:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM passwords WHERE user_email = ?", (self.current_user,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error deleting all entries: {e}")
            return False
    
    def update_password_entry(self, index: int, name: str, username: str, password: str, url: str = "") -> bool:
        """Update a password entry by index"""
        if not self.current_user:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the entry id at the given index
            cursor.execute(
                """SELECT id FROM passwords WHERE user_email = ? 
                   ORDER BY custom_order LIMIT 1 OFFSET ?""",
                (self.current_user, index)
            )
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            entry_id = result['id']
            
            # Encrypt the password before storing
            encrypted_password = self._encrypt(password)
            
            # Update the entry
            cursor.execute(
                """UPDATE passwords 
                   SET name = ?, username = ?, password = ?, url = ?
                   WHERE id = ?""",
                (name, username, encrypted_password, url, entry_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error updating password entry: {e}")
            return False
    
    def move_entry_up(self, index: int) -> bool:
        """Move an entry up in custom order"""
        if not self.current_user or index <= 0:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the two entries to swap
            cursor.execute(
                """SELECT id, custom_order FROM passwords WHERE user_email = ? 
                   ORDER BY custom_order LIMIT 2 OFFSET ?""",
                (self.current_user, index - 1)
            )
            results = cursor.fetchall()
            
            if len(results) < 2:
                conn.close()
                return False
            
            id1, order1 = results[0]['id'], results[0]['custom_order']
            id2, order2 = results[1]['id'], results[1]['custom_order']
            
            # Swap custom_order values
            cursor.execute("UPDATE passwords SET custom_order = ? WHERE id = ?", (order2, id1))
            cursor.execute("UPDATE passwords SET custom_order = ? WHERE id = ?", (order1, id2))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error moving entry up: {e}")
            return False
    
    def move_entry_down(self, index: int) -> bool:
        """Move an entry down in custom order"""
        if not self.current_user:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the two entries to swap
            cursor.execute(
                """SELECT id, custom_order FROM passwords WHERE user_email = ? 
                   ORDER BY custom_order LIMIT 2 OFFSET ?""",
                (self.current_user, index)
            )
            results = cursor.fetchall()
            
            if len(results) < 2:
                conn.close()
                return False
            
            id1, order1 = results[0]['id'], results[0]['custom_order']
            id2, order2 = results[1]['id'], results[1]['custom_order']
            
            # Swap custom_order values
            cursor.execute("UPDATE passwords SET custom_order = ? WHERE id = ?", (order2, id1))
            cursor.execute("UPDATE passwords SET custom_order = ? WHERE id = ?", (order1, id2))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error moving entry down: {e}")
            return False
    
    def get_sorted_entries(self, sort_type: str = "custom", search_query: str = "") -> List[Dict]:
        """Get password entries sorted by specified type and optionally filtered by search"""
        if not self.current_user:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build query based on search
        if search_query:
            search_pattern = f"%{search_query}%"
            cursor.execute(
                """SELECT name, username, password, url, custom_order, copy_count 
                   FROM passwords WHERE user_email = ? 
                   AND (name LIKE ? OR username LIKE ? OR url LIKE ?)""",
                (self.current_user, search_pattern, search_pattern, search_pattern)
            )
        else:
            cursor.execute(
                """SELECT name, username, password, url, custom_order, copy_count 
                   FROM passwords WHERE user_email = ?""",
                (self.current_user,)
            )
        entries = []
        for row in cursor.fetchall():
            # Decrypt password before returning
            try:
                decrypted_password = self._decrypt(row['password'])
            except:
                decrypted_password = ""  # Handle decryption errors gracefully
            
            entries.append({
                'name': row['name'],
                'username': row['username'],
                'password': decrypted_password,
                'url': row['url'],
                'custom_order': row['custom_order'],
                'copy_count': row['copy_count']
            })
        conn.close()
        
        # Apply sorting in Python (could be moved to SQL for better performance)
        if sort_type == "alphabetical_asc":
            entries.sort(key=lambda x: x["name"].lower())
        elif sort_type == "alphabetical_desc":
            entries.sort(key=lambda x: x["name"].lower(), reverse=True)
        elif sort_type == "frequently_used":
            entries.sort(key=lambda x: x.get("copy_count", 0), reverse=True)
        else:  # custom
            entries.sort(key=lambda x: x.get("custom_order", 0))
        
        return entries
