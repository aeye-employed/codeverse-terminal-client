"""
Configuration management for CodeVerse CLI
"""

import os
import json
from pathlib import Path
from typing import Any, Optional
from cryptography.fernet import Fernet

class Config:
    """Manage CLI configuration and credentials"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.codeverse'
        self.config_file = self.config_dir / 'config.json'
        self.key_file = self.config_dir / '.key'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create encryption key
        self.cipher = self._get_cipher()
        
        # Load config
        self.config = self._load_config()
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher for sensitive data"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Make key file readable only by owner
            os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        # Make config file readable only by owner
        os.chmod(self.config_file, 0o600)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        value = self.config.get(key, default)
        
        # Decrypt sensitive values
        if key == 'token' and value and value.startswith('enc:'):
            try:
                encrypted_data = value[4:].encode()
                return self.cipher.decrypt(encrypted_data).decode()
            except Exception:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        # Encrypt sensitive values
        if key == 'token':
            encrypted_data = self.cipher.encrypt(value.encode())
            value = f"enc:{encrypted_data.decode()}"
        
        self.config[key] = value
    
    def is_configured(self) -> bool:
        """Check if CLI is configured"""
        return all(key in self.config for key in ['host', 'port', 'token'])
    
    def clear(self):
        """Clear all configuration"""
        self.config = {}
        if self.config_file.exists():
            self.config_file.unlink()
    
    def get_workspace_config(self) -> dict:
        """Get workspace-specific configuration"""
        workspace_config = Path.cwd() / '.codeverse.json'
        if workspace_config.exists():
            with open(workspace_config, 'r') as f:
                return json.load(f)
        return {}
    
    def set_workspace_config(self, config: dict):
        """Set workspace-specific configuration"""
        workspace_config = Path.cwd() / '.codeverse.json'
        with open(workspace_config, 'w') as f:
            json.dump(config, f, indent=2)