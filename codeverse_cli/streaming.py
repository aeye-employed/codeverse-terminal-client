"""
Streaming session management for CodeVerse CLI
Author: IBDA AI LTD
Website: https://codeverse.ibda.me
"""

import asyncio
import json
from typing import Optional, Dict, Any, Callable
import websockets
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from pathlib import Path


class StreamingSession:
    """Manage streaming WebSocket sessions with CodeVerse Terminal"""
    
    def __init__(self, client, file_sync):
        self.client = client
        self.file_sync = file_sync
        self.console = Console()
        self.websocket = None
        self.session_id = None
        self.is_connected = False
        
        # Message history
        self.history_file = Path.home() / ".codeverse" / "chat_history"
        self.prompt_session = PromptSession(history=FileHistory(str(self.history_file)))
        
        # Callbacks
        self.on_file_change = None
        self.on_agent_update = None
    
    async def connect(self) -> bool:
        """Connect to streaming WebSocket"""
        try:
            extra_headers = {"Authorization": f"Bearer {self.client.token}"}
            self.websocket = await websockets.connect(
                self.client.ws_url,
                extra_headers=extra_headers
            )
            
            # Send initial connection message
            await self.websocket.send(json.dumps({
                "type": "connect",
                "workspace": str(Path.cwd())
            }))
            
            # Wait for connection confirmation
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "connected":
                self.session_id = data.get("session_id")
                self.is_connected = True
                return True
                
            return False
            
        except Exception as e:
            self.console.print(f"[red]Connection failed: {e}[/red]")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.is_connected = False
    
    async def send_message(self, message: str, context: Optional[Dict] = None):
        """Send message through streaming session"""
        if not self.is_connected:
            await self.connect()
        
        # Send message
        await self.websocket.send(json.dumps({
            "type": "chat",
            "message": message,
            "context": context or {},
            "workspace": str(Path.cwd())
        }))
        
        # Handle streaming response
        await self._handle_stream_response()
    
    async def _handle_stream_response(self):
        """Handle streaming response from server"""
        response_text = ""
        code_block = ""
        in_code_block = False
        language = None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Processing...", total=None)
            
            async for message in self.websocket:
                data = json.loads(message)
                
                if data["type"] == "chunk":
                    content = data["content"]
                    response_text += content
                    
                    # Handle code blocks
                    if "```" in content:
                        if not in_code_block:
                            # Starting code block
                            in_code_block = True
                            # Extract language
                            lines = content.split("\n")
                            for line in lines:
                                if line.startswith("```"):
                                    language = line[3:].strip() or "text"
                                    break
                        else:
                            # Ending code block
                            in_code_block = False
                            if code_block:
                                self.console.print(Syntax(
                                    code_block,
                                    language or "text",
                                    theme="monokai",
                                    line_numbers=True
                                ))
                                code_block = ""
                    elif in_code_block:
                        code_block += content
                    else:
                        # Regular text
                        self.console.print(content, end="")
                
                elif data["type"] == "file_change":
                    # Handle file changes
                    progress.update(task, description=f"Updating {data['path']}...")
                    
                    if self.on_file_change:
                        await self.on_file_change(data)
                    else:
                        # Default file change handling
                        await self._handle_file_change(data)
                
                elif data["type"] == "agent_update":
                    # Handle agent status updates
                    agent = data.get("agent", "Unknown")
                    status = data.get("status", "")
                    progress.update(task, description=f"{agent}: {status}")
                    
                    if self.on_agent_update:
                        await self.on_agent_update(data)
                
                elif data["type"] == "error":
                    self.console.print(f"\n[red]Error: {data['message']}[/red]")
                    break
                
                elif data["type"] == "complete":
                    progress.update(task, description="Complete")
                    break
        
        # Final newline
        self.console.print()
    
    async def _handle_file_change(self, data: Dict[str, Any]):
        """Handle file change notification"""
        path = data.get("path")
        action = data.get("action")
        content = data.get("content", "")
        
        self.console.print(f"\n[yellow]File {action}: {path}[/yellow]")
        
        if action in ["create", "update"]:
            # Write file locally
            full_path = Path.cwd() / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Decode content if base64
            if data.get("encoded"):
                import base64
                content = base64.b64decode(content).decode()
            
            with open(full_path, "w") as f:
                f.write(content)
            
            self.console.print(f"[green]✓ File {action}d successfully[/green]")
        
        elif action == "delete":
            full_path = Path.cwd() / path
            if full_path.exists():
                full_path.unlink()
                self.console.print(f"[green]✓ File deleted successfully[/green]")
    
    async def run_agent_task(self, agent: str, task: str):
        """Run task with specific agent"""
        if not self.is_connected:
            await self.connect()
        
        # Send agent task
        await self.websocket.send(json.dumps({
            "type": "agent_task",
            "agent": agent,
            "task": task,
            "workspace": str(Path.cwd())
        }))
        
        # Handle streaming response
        await self._handle_stream_response()
    
    async def interactive_chat(self):
        """Run interactive chat session"""
        self.console.print(Panel.fit(
            "[bold cyan]CodeVerse Terminal - Interactive Mode[/bold cyan]\n"
            "Connected to cloud platform. Type 'exit' to quit.\n"
            "Type '/help' for available commands.",
            title="Welcome to CodeVerse by IBDA AI LTD"
        ))
        
        # Connect to server
        if not await self.connect():
            return
        
        # Start chat loop
        while True:
            try:
                # Get user input
                message = await self.prompt_session.prompt_async(
                    "You: ",
                    multiline=False
                )
                
                if message.lower() in ["exit", "quit", "/exit", "/quit"]:
                    break
                
                if message.startswith("/"):
                    await self._handle_command(message)
                    continue
                
                # Send message
                self.console.print("[dim]Assistant: [/dim]", end="")
                await self.send_message(message)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        # Disconnect
        await self.disconnect()
        self.console.print("\n[yellow]Goodbye![/yellow]")
    
    async def _handle_command(self, command: str):
        """Handle slash commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/help":
            self.console.print(Panel(
                "[bold]Available Commands:[/bold]\n\n"
                "/help - Show this help message\n"
                "/agents - List available agents\n"
                "/agent <name> <task> - Run task with specific agent\n"
                "/sync - Sync current directory with cloud\n"
                "/status - Show connection status\n"
                "/clear - Clear screen\n"
                "/exit - Exit interactive mode",
                title="Help"
            ))
        
        elif cmd == "/agents":
            agents = await self.client.list_agents()
            self.console.print("[bold]Available Agents:[/bold]")
            for agent in agents:
                self.console.print(f"  • {agent}")
        
        elif cmd == "/agent":
            if len(parts) < 3:
                self.console.print("[red]Usage: /agent <name> <task>[/red]")
            else:
                agent = parts[1]
                task = " ".join(parts[2:])
                await self.run_agent_task(agent, task)
        
        elif cmd == "/sync":
            self.console.print("[yellow]Syncing files...[/yellow]")
            files = await self.file_sync.sync_directory(".")
            self.console.print(f"[green]Synced {len(files)} files[/green]")
        
        elif cmd == "/status":
            status = await self.client.get_status()
            self.console.print(Panel(
                f"[bold]Connection Status:[/bold]\n\n"
                f"Connected: {self.is_connected}\n"
                f"Session ID: {self.session_id}\n"
                f"Server Status: {status.get('status', 'Unknown')}\n"
                f"Active Agents: {status.get('active_agents', 0)}",
                title="Status"
            ))
        
        elif cmd == "/clear":
            self.console.clear()
        
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")