from typing import List, Dict, Optional
from .DatabaseManager import DatabaseManager


class PasswordService:
    """Handles password entry CRUD operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._current_user: Optional[str] = None
    
    @property
    def current_user(self) -> Optional[str]:
        """Get current user"""
        return self._current_user
    
    @current_user.setter
    def current_user(self, email: Optional[str]):
        """Set current user"""
        self._current_user = email
    
    def add_password_entry(self, name: str, username: str, password: str, url: str = "") -> bool:
        """Add a new password entry for current user"""
        if not self.current_user:
            return False
        
        # Input validation
        if not name or not name.strip():
            print("Error: Entry name cannot be empty")
            return False
        if not username or not username.strip():
            print("Error: Username cannot be empty")
            return False
        if not password:
            print("Error: Password cannot be empty")
            return False
        
        # Trim whitespace
        name = name.strip()
        username = username.strip()
        url = url.strip() if url else ""
        
        # Length validation (reasonable limits)
        if len(name) > 64:
            print("Error: Entry name too long (max 64 characters)")
            return False
        if len(username) > 64:
            print("Error: Username too long (max 64 characters)")
            return False
        if len(url) > 2048:  # URLs can be longer
            print("Error: URL too long (max 2048 characters)")
            return False
        if len(password) > 64:
            print("Error: Password too long (max 64 characters)")
            return False
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the next order value
            cursor.execute(
                "SELECT COALESCE(MAX(custom_order), -1) + 1 FROM passwords WHERE user_email = ?",
                (self.current_user,)
            )
            next_order = cursor.fetchone()[0]
            
            # Encrypt the password before storing
            encrypted_password = self.db_manager.encrypt(password)
            
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
        
        conn = self.db_manager.get_connection()
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
                decrypted_password = self.db_manager.decrypt(row['password'])
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
        
        conn = self.db_manager.get_connection()
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
        
        conn = self.db_manager.get_connection()
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
        
        # Input validation
        if not name or not name.strip():
            print("Error: Entry name cannot be empty")
            return False
        if not username or not username.strip():
            print("Error: Username cannot be empty")
            return False
        if not password:
            print("Error: Password cannot be empty")
            return False
        
        # Trim whitespace
        name = name.strip()
        username = username.strip()
        url = url.strip() if url else ""
        
        # Length validation (reasonable limits)
        if len(name) > 64:
            print("Error: Entry name too long (max 64 characters)")
            return False
        if len(username) > 64:
            print("Error: Username too long (max 64 characters)")
            return False
        if len(url) > 2048:  # URLs can be longer
            print("Error: URL too long (max 2048 characters)")
            return False
        if len(password) > 64:
            print("Error: Password too long (max 64 characters)")
            return False
        
        conn = self.db_manager.get_connection()
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
            encrypted_password = self.db_manager.encrypt(password)
            
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
        
        conn = self.db_manager.get_connection()
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
        
        conn = self.db_manager.get_connection()
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
    
    def increment_copy_count(self, index: int) -> None:
        """Increment the copy_count for a password entry by index"""
        if not self.current_user:
            return
        
        conn = self.db_manager.get_connection()
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
    
    def get_sorted_entries(self, sort_type: str = "custom", search_query: str = "") -> List[Dict]:
        """Get password entries sorted by specified type and optionally filtered by search"""
        if not self.current_user:
            return []
        
        conn = self.db_manager.get_connection()
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
                decrypted_password = self.db_manager.decrypt(row['password'])
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
