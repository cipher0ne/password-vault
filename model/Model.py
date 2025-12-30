import json
import os
import hashlib
from typing import Optional, List, Dict


class PasswordVaultModel:
    """Data model for managing users and their password entries"""
    
    def __init__(self, data_file: str = "vault_data.json"):
        self.data_file = data_file
        self.current_user: Optional[str] = None
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"users": {}}
        return {"users": {}}
    
    def _save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        if email in self.data["users"]:
            return False, "User already exists"
        
        self.data["users"][email] = {
            "password_hash": self._hash_password(password),
            "passwords": []
        }
        self._save_data()
        return True, "Registration successful"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str]:
        """Authenticate user"""
        if email not in self.data["users"]:
            return False, "User not found"
        
        password_hash = self._hash_password(password)
        if self.data["users"][email]["password_hash"] == password_hash:
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
        
        # Get the next order value
        passwords = self.data["users"][self.current_user]["passwords"]
        next_order = len(passwords)
        
        entry = {
            "name": name,
            "username": username,
            "password": password,
            "url": url,
            "custom_order": next_order
        }
        self.data["users"][self.current_user]["passwords"].append(entry)
        self._save_data()
        return True
    
    def get_password_entries(self) -> List[Dict]:
        """Get all password entries for current user"""
        if not self.current_user:
            return []
        return self.data["users"][self.current_user]["passwords"]
    
    def delete_password_entry(self, index: int) -> bool:
        """Delete a password entry by index"""
        if not self.current_user:
            return False
        
        try:
            self.data["users"][self.current_user]["passwords"].pop(index)
            self._save_data()
            return True
        except IndexError:
            return False
    
    def delete_all_entries(self) -> bool:
        """Delete all password entries for current user"""
        if not self.current_user:
            return False
        
        self.data["users"][self.current_user]["passwords"] = []
        self._save_data()
        return True
    
    def move_entry_up(self, index: int) -> bool:
        """Move an entry up in custom order"""
        if not self.current_user or index <= 0:
            return False
        
        passwords = self.data["users"][self.current_user]["passwords"]
        if index >= len(passwords):
            return False
        
        # Swap custom_order values
        passwords[index]["custom_order"], passwords[index - 1]["custom_order"] = \
            passwords[index - 1]["custom_order"], passwords[index]["custom_order"]
        
        self._save_data()
        return True
    
    def move_entry_down(self, index: int) -> bool:
        """Move an entry down in custom order"""
        if not self.current_user:
            return False
        
        passwords = self.data["users"][self.current_user]["passwords"]
        if index < 0 or index >= len(passwords) - 1:
            return False
        
        # Swap custom_order values
        passwords[index]["custom_order"], passwords[index + 1]["custom_order"] = \
            passwords[index + 1]["custom_order"], passwords[index]["custom_order"]
        
        self._save_data()
        return True
    
    def get_sorted_entries(self, sort_type: str = "custom", search_query: str = "") -> List[Dict]:
        """Get password entries sorted by specified type and optionally filtered by search"""
        if not self.current_user:
            return []
        
        entries = self.data["users"][self.current_user]["passwords"].copy()
        
        # Add custom_order to old entries that don't have it
        for i, entry in enumerate(entries):
            if "custom_order" not in entry:
                entry["custom_order"] = i
        
        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            entries = [
                entry for entry in entries
                if search_lower in entry["name"].lower() or 
                   search_lower in entry["username"].lower() or
                   search_lower in entry.get("url", "").lower()
            ]
        
        # Apply sorting
        if sort_type == "alphabetical_asc":
            entries.sort(key=lambda x: x["name"].lower())
        elif sort_type == "alphabetical_desc":
            entries.sort(key=lambda x: x["name"].lower(), reverse=True)
        else:  # custom
            entries.sort(key=lambda x: x.get("custom_order", 0))
        
        return entries
