"""
CodeVerse Client - API Communication Module
Handles all communication with the CodeVerse platform
"""

import requests
import websocket
import json
import base64
import os
from typing import List, Dict, Optional, Any
from rich.console import Console

console = Console()

class CodeVerseClient:
    """Main client for CodeVerse API communication"""
    
    def __init__(self, config, auth_manager):
        self.config = config
        self.auth = auth_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CodeVerse-CLI/1.0.0',
            'Content-Type': 'application/json'
        })
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {}
        if self.auth.is_authenticated():
            token = self.auth.get_token()
            headers['Authorization'] = f'Bearer {token}'
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, use_agents_url: bool = False) -> Dict:
        """Make authenticated API request"""
        base_url = self.config.get('agents_url') if use_agents_url else self.config.get('api_url')
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=data)
            else:
                response = self.session.request(method.upper(), url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def send_message(self, message: str, agent: str = "general", context: List[Dict] = None, workspace: str = None) -> str:
        """Send message to AI agent"""
        if not workspace:
            workspace = os.path.basename(os.getcwd())
        
        data = {
            "message": message,
            "agent": agent,
            "context": context or [],
            "workspace": workspace,
            "stream": False
        }
        
        try:
            response = self._make_request('POST', '/api/chat', data)
            return response.get('response', 'No response received')
        except Exception as e:
            return f"Error: {e}"
    
    def get_agents(self) -> Dict:
        """Get list of available AI agents"""
        return self._make_request('GET', '/api/agents')
    
    def get_status(self) -> Dict:
        """Get platform status"""
        return self._make_request('GET', '/api/status')
    
    def upload_file(self, filename: str, content: str, path: str = "") -> Dict:
        """Upload file to workspace"""
        # Encode content as base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "filename": filename,
            "content": encoded_content,
            "path": path
        }
        
        return self._make_request('POST', '/api/files/upload', data)
    
    def download_file(self, filename: str, path: str = "") -> Dict:
        """Download file from workspace"""
        params = {
            "filename": filename,
            "path": path
        }
        
        response = self._make_request('GET', '/api/files/download', params)
        
        # Decode base64 content
        if 'content' in response:
            response['content'] = base64.b64decode(response['content']).decode('utf-8')
        
        return response
    
    def sync_files(self, file_paths: List[str], workspace: str) -> Dict:
        """Sync multiple files to workspace"""
        files_data = []
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Encode content as base64
                encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                
                files_data.append({
                    "filename": os.path.basename(file_path),
                    "content": encoded_content,
                    "path": os.path.dirname(file_path)
                })
        
        data = {
            "files": files_data,
            "workspace": workspace
        }
        
        return self._make_request('POST', '/api/files/sync', data)
    
    def start_websocket_session(self, on_message_callback=None):
        """Start WebSocket session for real-time communication"""
        ws_url = self.config.get('websocket_url')
        token = self.auth.get_token()
        
        def on_message(ws, message):
            data = json.loads(message)
            if on_message_callback:
                on_message_callback(data)
            else:
                console.print(f"[cyan]WebSocket:[/cyan] {data.get('message', message)}")
        
        def on_error(ws, error):
            console.print(f"[red]WebSocket Error:[/red] {error}")
        
        def on_close(ws, close_status_code, close_msg):
            console.print("[yellow]WebSocket connection closed[/yellow]")
        
        def on_open(ws):
            console.print("[green]WebSocket connected[/green]")
            # Send authentication
            ws.send(json.dumps({
                "type": "auth",
                "token": token
            }))
        
        # Add token to URL if available
        if token:
            ws_url += f"?token={token}"
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        return ws
    
    def send_websocket_message(self, ws, message_type: str, data: Dict):
        """Send message via WebSocket"""
        message = {
            "type": message_type,
            **data
        }
        ws.send(json.dumps(message))

class StreamingResponse:
    """Handle streaming responses from agents"""
    
    def __init__(self, client, endpoint, data):
        self.client = client
        self.endpoint = endpoint
        self.data = data
    
    def __iter__(self):
        """Stream response chunks"""
        # For now, return single response
        # TODO: Implement actual streaming
        response = self.client._make_request('POST', self.endpoint, self.data)
        yield response.get('response', '')
    
    def get_full_response(self) -> str:
        """Get complete response as string"""
        return ''.join(self)