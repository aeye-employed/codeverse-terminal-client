"""
CodeVerse Client - Handles communication with CodeVerse Terminal server
"""

import httpx
import websockets
import json
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from pathlib import Path
import base64

class CodeVerseClient:
    """Client for communicating with CodeVerse Terminal server"""
    
    def __init__(self, host: str, port: str, token: str):
        self.host = host
        self.port = port
        self.token = token
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}/ws"
        
        # HTTP client with auth
        self.http_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=60.0
        )
    
    async def test_connection(self) -> bool:
        """Test connection to server"""
        try:
            response = await self.http_client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def send_message(self, message: str, context: List[Dict] = None) -> str:
        """Send a message and get response (non-streaming)"""
        payload = {
            "message": message,
            "context": context or [],
            "workspace": str(Path.cwd())
        }
        
        response = await self.http_client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Server error: {response.status_code}")
    
    async def stream_message(self, message: str, context: List[Dict] = None) -> AsyncGenerator[str, None]:
        """Stream message response via WebSocket"""
        async with websockets.connect(
            self.ws_url,
            extra_headers={"Authorization": f"Bearer {self.token}"}
        ) as websocket:
            
            # Send message
            await websocket.send(json.dumps({
                "type": "chat",
                "message": message,
                "context": context or [],
                "workspace": str(Path.cwd())
            }))
            
            # Stream response
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "chunk":
                    yield data["content"]
                elif data["type"] == "error":
                    raise Exception(data["message"])
                elif data["type"] == "complete":
                    break
    
    async def upload_file(self, file_path: str, content: str) -> bool:
        """Upload a file to the server"""
        response = await self.http_client.post(
            f"{self.base_url}/api/files/upload",
            json={
                "path": file_path,
                "content": base64.b64encode(content.encode()).decode(),
                "workspace": str(Path.cwd())
            }
        )
        return response.status_code == 200
    
    async def download_file(self, file_path: str) -> Optional[str]:
        """Download a file from the server"""
        response = await self.http_client.get(
            f"{self.base_url}/api/files/download",
            params={"path": file_path, "workspace": str(Path.cwd())}
        )
        
        if response.status_code == 200:
            content = response.json()["content"]
            return base64.b64decode(content).decode()
        return None
    
    async def sync_files(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Sync multiple files at once"""
        response = await self.http_client.post(
            f"{self.base_url}/api/files/sync",
            json={
                "files": files,
                "workspace": str(Path.cwd())
            }
        )
        return response.json()
    
    async def run_agent_task(self, agent: str, task: str) -> AsyncGenerator[str, None]:
        """Run a task with a specific agent"""
        async with websockets.connect(
            self.ws_url,
            extra_headers={"Authorization": f"Bearer {self.token}"}
        ) as websocket:
            
            # Send task
            await websocket.send(json.dumps({
                "type": "agent_task",
                "agent": agent,
                "task": task,
                "workspace": str(Path.cwd())
            }))
            
            # Stream response
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "chunk":
                    yield data["content"]
                elif data["type"] == "file_change":
                    # Handle file changes
                    yield f"\n[FILE_CHANGE] {data['path']}: {data['action']}\n"
                elif data["type"] == "error":
                    raise Exception(data["message"])
                elif data["type"] == "complete":
                    break
    
    async def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        response = await self.http_client.get(f"{self.base_url}/api/status")
        if response.status_code == 200:
            return response.json()
        return {}
    
    async def list_agents(self) -> List[str]:
        """List available agents"""
        response = await self.http_client.get(f"{self.base_url}/api/agents")
        if response.status_code == 200:
            return response.json()["agents"]
        return []
    
    async def close(self):
        """Close the client"""
        await self.http_client.aclose()