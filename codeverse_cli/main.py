#!/usr/bin/env python3
"""
CodeVerse CLI - Main entry point
Similar to Claude Code but connects to your cloud CodeVerse Terminal
"""

import click
import asyncio
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import yaml

from .client import CodeVerseClient
from .config import Config
from .file_sync import FileSync
from .auth import AuthManager
from .streaming import StreamingSession

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CodeVerse Terminal CLI - AI-powered development from anywhere"""
    pass

@cli.command()
@click.option('--host', prompt='CodeVerse server host', help='Server hostname or IP')
@click.option('--port', prompt='API port', default='8000', help='API Gateway port')
@click.option('--token', prompt='API token', hide_input=True, help='Authentication token')
def init(host, port, token):
    """Initialize connection to CodeVerse Terminal server"""
    config = Config()
    config.set('host', host)
    config.set('port', port)
    config.set('token', token)
    config.save()
    
    console.print(f"[green]✓[/green] Configuration saved to {config.config_file}")
    console.print(f"[blue]Server:[/blue] {host}:{port}")
    
    # Test connection
    client = CodeVerseClient(host, port, token)
    if asyncio.run(client.test_connection()):
        console.print("[green]✓[/green] Successfully connected to CodeVerse Terminal!")
    else:
        console.print("[red]✗[/red] Failed to connect. Please check your settings.")

@cli.command()
@click.option('--host', prompt='CodeVerse server host', help='Server hostname or IP')
@click.option('--port', prompt='API port', default='8000', help='API Gateway port')
@click.option('--username', '-u', help='Username (will prompt if not provided)')
def login(host, port, username):
    """Login to CodeVerse Terminal server"""
    config = Config()
    auth_manager = AuthManager(config)
    
    if asyncio.run(auth_manager.login(host, port, username)):
        console.print("[green]✓[/green] Successfully logged in to CodeVerse Terminal!")
        console.print(f"[blue]Configuration saved to:[/blue] {config.config_file}")
    else:
        console.print("[red]✗[/red] Login failed. Please check your credentials.")

@cli.command()
@click.argument('message', nargs=-1)
@click.option('--context', '-c', help='Additional context file', multiple=True)
@click.option('--no-stream', is_flag=True, help='Disable streaming output')
@click.option('--sync-files', '-s', is_flag=True, help='Sync current directory files')
def chat(message, context, no_stream, sync_files):
    """Send a message to CodeVerse Terminal (like Claude Code)"""
    config = Config()
    if not config.is_configured():
        console.print("[red]Not configured. Run 'codeverse init' first.[/red]")
        return
    
    # Join message parts
    message_text = ' '.join(message) if message else None
    
    # Interactive mode if no message provided
    if not message_text:
        console.print("[bold blue]CodeVerse Terminal[/bold blue] - Interactive Mode")
        console.print("Type 'exit' to quit, 'help' for commands\n")
        
        history = FileHistory(Path.home() / '.codeverse_history')
        
        while True:
            try:
                message_text = prompt(
                    "You: ",
                    history=history,
                    auto_suggest=AutoSuggestFromHistory(),
                    multiline=False
                )
                
                if message_text.lower() in ['exit', 'quit']:
                    break
                elif message_text.lower() == 'help':
                    show_help()
                    continue
                
                # Process the message
                asyncio.run(process_message(config, message_text, context, no_stream, sync_files))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except EOFError:
                break
    else:
        # Single message mode
        asyncio.run(process_message(config, message_text, context, no_stream, sync_files))

async def process_message(config, message, context_files, no_stream, sync_files):
    """Process a single message"""
    client = CodeVerseClient(
        config.get('host'),
        config.get('port'),
        config.get('token')
    )
    
    # Sync files if requested
    if sync_files:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Syncing files...", total=None)
            
            file_sync = FileSync(client)
            synced_files = await file_sync.sync_directory(os.getcwd())
            
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Synced {len(synced_files)} files")
    
    # Add context files
    context_data = []
    for ctx_file in context_files:
        if os.path.exists(ctx_file):
            with open(ctx_file, 'r') as f:
                context_data.append({
                    'file': ctx_file,
                    'content': f.read()
                })
    
    # Send message
    if no_stream:
        # Non-streaming mode
        response = await client.send_message(message, context_data)
        console.print(Markdown(response))
    else:
        # Streaming mode (like Claude Code)
        console.print("\n[bold green]CodeVerse:[/bold green]")
        
        session = StreamingSession(client, FileSync(client))
        await session.send_message(message, context_data)

@cli.command()
@click.option('--watch', '-w', is_flag=True, help='Watch for file changes')
def sync(watch):
    """Sync local files with CodeVerse Terminal"""
    config = Config()
    if not config.is_configured():
        console.print("[red]Not configured. Run 'codeverse init' first.[/red]")
        return
    
    client = CodeVerseClient(
        config.get('host'),
        config.get('port'),
        config.get('token')
    )
    
    file_sync = FileSync(client)
    
    if watch:
        console.print("[blue]Watching for file changes...[/blue]")
        asyncio.run(file_sync.watch_directory(os.getcwd()))
    else:
        asyncio.run(sync_once(file_sync))

async def sync_once(file_sync):
    """Sync files once"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Syncing files...", total=None)
        
        synced_files = await file_sync.sync_directory(os.getcwd())
        
        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Synced {len(synced_files)} files")

@cli.command()
def status():
    """Show connection status and configuration"""
    config = Config()
    
    if not config.is_configured():
        console.print("[red]Not configured. Run 'codeverse init' first.[/red]")
        return
    
    console.print("[bold]CodeVerse Terminal Configuration[/bold]")
    console.print(f"Host: {config.get('host')}")
    console.print(f"Port: {config.get('port')}")
    console.print(f"Config file: {config.config_file}")
    
    # Test connection
    client = CodeVerseClient(
        config.get('host'),
        config.get('port'),
        config.get('token')
    )
    
    if asyncio.run(client.test_connection()):
        console.print("\n[green]✓[/green] Connected to CodeVerse Terminal")
        
        # Get server status
        status = asyncio.run(client.get_status())
        if status:
            console.print(f"\nServices: {status.get('total_services', 'Unknown')}")
            console.print(f"Orchestrator: {status.get('orchestrator_status', 'Unknown')}")
            console.print(f"Models: {', '.join(status.get('available_models', []))}")
    else:
        console.print("\n[red]✗[/red] Cannot connect to server")

@cli.command()
@click.argument('task')
@click.option('--agent', '-a', help='Specific agent to use')
def run(task, agent):
    """Run a specific task (e.g., 'generate tests', 'review code')"""
    config = Config()
    if not config.is_configured():
        console.print("[red]Not configured. Run 'codeverse init' first.[/red]")
        return
    
    client = CodeVerseClient(
        config.get('host'),
        config.get('port'),
        config.get('token')
    )
    
    # Map common tasks to agents
    task_agent_map = {
        'test': 'testing',
        'tests': 'testing',
        'review': 'code_reviewer',
        'generate': 'code_generator',
        'document': 'documentation',
        'analyze': 'code_analysis',
        'format': 'formatter_linter',
        'migrate': 'project_migration',
        'optimize': 'performance_optimization',
    }
    
    # Determine agent
    if not agent:
        for key, value in task_agent_map.items():
            if key in task.lower():
                agent = value
                break
    
    if not agent:
        agent = 'orchestrator'  # Default to orchestrator
    
    console.print(f"[blue]Running task with {agent} agent...[/blue]")
    
    asyncio.run(run_task(client, task, agent))

async def run_task(client, task, agent):
    """Execute a task with specific agent"""
    # Sync current directory
    file_sync = FileSync(client)
    await file_sync.sync_directory(os.getcwd())
    
    # Run task
    session = StreamingSession(client, file_sync)
    console.print(f"\n[bold green]{agent}:[/bold green]")
    await session.run_agent_task(agent, task)

def show_help():
    """Show interactive mode help"""
    help_text = """
[bold]Interactive Mode Commands:[/bold]
  exit/quit     - Exit interactive mode
  help          - Show this help
  /sync         - Sync current directory
  /context <file> - Add file to context
  /clear        - Clear context
  /agent <name> - Use specific agent
  
[bold]Example Usage:[/bold]
  > Generate a REST API for user management
  > /context schema.sql
  > Create tests for the UserService class
  > /agent documentation
  > Document all public methods
    """
    console.print(Markdown(help_text))

if __name__ == "__main__":
    cli()