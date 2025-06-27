"""
Authentication management for CodeVerse CLI
Author: IBDA AI LTD
Website: https://codeverse.ibda.me
"""

import httpx
import asyncio
import getpass
from typing import Optional, Dict
import json


class AuthManager:
    """Manage authentication with CodeVerse Terminal server"""
    
    def __init__(self, config):
        self.config = config
    
    async def login(self, host: str, port: str, username: Optional[str] = None) -> bool:
        """Login to CodeVerse Terminal server"""
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ")
        
        password = getpass.getpass("Password: ")
        
        # Attempt authentication
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://{host}:{port}/api/auth/login",
                    json={
                        "username": username,
                        "password": password
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token")
                    
                    # Save configuration
                    self.config.set("host", host)
                    self.config.set("port", port)
                    self.config.set("token", token)
                    self.config.set("username", username)
                    self.config.save()
                    
                    return True
                else:
                    return False
                    
            except Exception as e:
                print(f"Authentication failed: {str(e)}")
                return False
    
    async def verify_token(self) -> bool:
        """Verify current token is valid"""
        if not self.config.is_configured():
            return False
        
        host = self.config.get("host")
        port = self.config.get("port")
        token = self.config.get("token")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"http://{host}:{port}/api/auth/verify",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                return response.status_code == 200
            except Exception:
                return False
    
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""
        if not self.config.is_configured():
            return False
        
        host = self.config.get("host")
        port = self.config.get("port")
        token = self.config.get("token")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://{host}:{port}/api/auth/refresh",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    new_token = data.get("token")
                    self.config.set("token", new_token)
                    self.config.save()
                    return True
                    
                return False
                
            except Exception:
                return False
    
    def logout(self):
        """Logout and clear stored credentials"""
        self.config.clear()
    
    async def get_api_key(self) -> Optional[str]:
        """Get API key for programmatic access"""
        if not self.config.is_configured():
            return None
        
        host = self.config.get("host")
        port = self.config.get("port")
        token = self.config.get("token")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://{host}:{port}/api/auth/apikey",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("api_key")
                    
                return None
                
            except Exception:
                return None
    
    async def register(self, host: str, port: str) -> bool:
        """Register new user account"""
        username = input("Choose username: ")
        email = input("Email: ")
        password = getpass.getpass("Choose password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords do not match")
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://{host}:{port}/api/auth/register",
                    json={
                        "username": username,
                        "email": email,
                        "password": password
                    },
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    print("Registration successful! Please login.")
                    return True
                else:
                    error = response.json().get("error", "Registration failed")
                    print(f"Error: {error}")
                    return False
                    
            except Exception as e:
                print(f"Registration failed: {str(e)}")
                return False