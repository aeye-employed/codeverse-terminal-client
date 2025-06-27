"""
CodeVerse Configuration Manager
Handles application configuration and settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for CodeVerse CLI"""
    
    def __init__(self, config_path: str = None, defaults: Dict[str, Any] = None):
        self.config_path = config_path or os.path.expanduser("~/.codeverse/config.json")
        self.defaults = defaults or {}
        self.data = {}
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        # Start with defaults
        self.data = self.defaults.copy()
        
        # Load from file if it exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    self.data.update(file_config)
            except (json.JSONDecodeError, IOError):
                # If config file is corrupted, use defaults
                pass
        
        # Load environment variable overrides
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables"""
        env_mappings = {
            'CODEVERSE_API_URL': 'api_url',
            'CODEVERSE_AGENTS_URL': 'agents_url',
            'CODEVERSE_WEBSOCKET_URL': 'websocket_url',
            'CODEVERSE_TIMEOUT': 'timeout',
            'CODEVERSE_MAX_RETRIES': 'max_retries',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                # Try to convert to appropriate type
                if config_key in ['timeout', 'max_retries']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                self.data[config_key] = value
    
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            
            # Secure file permissions
            os.chmod(self.config_path, 0o600)
            
        except IOError as e:
            raise Exception(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.data.update(updates)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.data = self.defaults.copy()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data"""
        return self.data.copy()
    
    def validate(self) -> bool:
        """Validate current configuration"""
        required_keys = ['api_url', 'agents_url', 'websocket_url']
        
        for key in required_keys:
            if not self.get(key):
                return False
        
        # Validate URLs
        for url_key in ['api_url', 'agents_url']:
            url = self.get(url_key)
            if url and not (url.startswith('http://') or url.startswith('https://')):
                return False
        
        # Validate WebSocket URL
        ws_url = self.get('websocket_url')
        if ws_url and not (ws_url.startswith('ws://') or ws_url.startswith('wss://')):
            return False
        
        return True
    
    def get_project_config(self, project_path: str = None) -> Dict[str, Any]:
        """Get project-specific configuration"""
        if not project_path:
            project_path = os.getcwd()
        
        config_file = os.path.join(project_path, '.codeverse.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {}
    
    def create_project_config(self, project_path: str, config_data: Dict[str, Any]):
        """Create project-specific configuration"""
        config_file = os.path.join(project_path, '.codeverse.json')
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to create project config: {e}")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"CodeVerse Config: {self.config_path}"
    
    def __repr__(self) -> str:
        """Detailed representation of configuration"""
        return f"Config(path='{self.config_path}', data={self.data})"