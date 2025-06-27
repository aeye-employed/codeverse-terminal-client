"""
CodeVerse Authentication Manager
Handles secure authentication and token management
"""

import requests
import json
import os
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
import keyring
import base64

class AuthManager:
    """Manages authentication tokens and credentials"""
    
    def __init__(self, config):
        self.config = config
        self.token = None
        self.refresh_token = None
        self.username = None
        self.api_key = None
        
        # Initialize encryption
        self._init_encryption()
        
        # Load existing session
        self._load_session()
    
    def _init_encryption(self):
        """Initialize encryption for secure token storage"""
        try:
            # Try to get existing key from keyring
            key_data = keyring.get_password("codeverse-cli", "encryption_key")
            if key_data:
                self.cipher = Fernet(key_data.encode())
            else:
                # Generate new key
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
                keyring.set_password("codeverse-cli", "encryption_key", key.decode())
        except Exception:
            # Fallback to file-based key storage
            key_file = os.path.expanduser("~/.codeverse/.key")
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Secure permissions
            
            self.cipher = Fernet(key)
    
    def _get_config_file(self) -> str:
        """Get path to config file"""
        config_dir = os.path.expanduser("~/.codeverse")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "auth.json")
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def _save_session(self):
        """Save current session to encrypted file"""
        if not self.token:
            return
        
        session_data = {
            "token": self._encrypt_data(self.token),
            "username": self.username,
            "api_key": self._encrypt_data(self.api_key) if self.api_key else None
        }
        
        if self.refresh_token:
            session_data["refresh_token"] = self._encrypt_data(self.refresh_token)
        
        config_file = self._get_config_file()
        with open(config_file, 'w') as f:
            json.dump(session_data, f)
        
        # Secure file permissions
        os.chmod(config_file, 0o600)
    
    def _load_session(self):
        """Load existing session from encrypted file"""
        config_file = self._get_config_file()
        
        if not os.path.exists(config_file):
            return
        
        try:
            with open(config_file, 'r') as f:
                session_data = json.load(f)
            
            if "token" in session_data:
                self.token = self._decrypt_data(session_data["token"])
                self.username = session_data.get("username")
                
                if "refresh_token" in session_data:
                    self.refresh_token = self._decrypt_data(session_data["refresh_token"])
                
                if session_data.get("api_key"):
                    self.api_key = self._decrypt_data(session_data["api_key"])
                
                # Verify token is still valid
                if not self._verify_token():
                    self._clear_session()
                
        except Exception as e:
            # If we can't decrypt or load, clear the session
            self._clear_session()
    
    def _clear_session(self):
        """Clear current session"""
        self.token = None
        self.refresh_token = None
        self.username = None
        self.api_key = None
        
        config_file = self._get_config_file()
        if os.path.exists(config_file):
            os.remove(config_file)
    
    def _verify_token(self) -> bool:
        """Verify if current token is valid"""
        if not self.token:
            return False
        
        try:
            api_url = self.config.get('api_url')
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{api_url}/api/auth/verify", headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Login with email and password"""
        try:
            api_url = self.config.get('api_url')
            
            data = {
                "username": email,  # API expects username field
                "password": password
            }
            
            response = requests.post(
                f"{api_url}/api/auth/login",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                
                self.token = auth_data.get('access_token')
                self.refresh_token = auth_data.get('refresh_token')
                self.username = email
                
                # Get API key
                self._fetch_api_key()
                
                # Save session
                self._save_session()
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def _fetch_api_key(self):
        """Fetch user's API key"""
        if not self.token:
            return
        
        try:
            api_url = self.config.get('api_url')
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(f"{api_url}/api/auth/apikey", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.api_key = data.get('api_key')
                
        except Exception:
            pass  # API key is optional
    
    def logout(self):
        """Logout and clear session"""
        self._clear_session()
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.token is not None and self._verify_token()
    
    def get_token(self) -> Optional[str]:
        """Get current access token"""
        return self.token
    
    def get_api_key(self) -> Optional[str]:
        """Get current API key"""
        return self.api_key
    
    def get_username(self) -> Optional[str]:
        """Get current username"""
        return self.username
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return False
        
        try:
            api_url = self.config.get('api_url')
            
            response = requests.post(
                f"{api_url}/api/auth/refresh",
                params={"refresh_token": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get('access_token')
                self.refresh_token = auth_data.get('refresh_token')
                
                self._save_session()
                return True
            else:
                self._clear_session()
                return False
                
        except Exception:
            return False