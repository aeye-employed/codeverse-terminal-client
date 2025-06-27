#!/usr/bin/env python3
"""
CodeVerse CLI - Main Entry Point
Production-ready AI development assistant
"""

import click
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .client import CodeVerseClient
from .auth import AuthManager
from .config import Config
from .utils import print_version, print_logo, handle_error

console = Console()

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "https://userapi-codeverse.ibda.me",
    "agents_url": "https://api-codeverse.ibda.me", 
    "websocket_url": "wss://userapi-codeverse.ibda.me/ws",
    "timeout": 30,
    "max_retries": 3
}

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--config', type=click.Path(), help='Config file path')
@click.pass_context
def main(ctx, version, config):
    """
    🚀 CodeVerse CLI - AI-Powered Development Assistant
    
    Transform your development workflow with 54 specialized AI agents.
    Build 10x faster with intelligent code generation, review, and optimization.
    """
    ctx.ensure_object(dict)
    
    if version:
        print_version()
        return
    
    # Initialize configuration
    config_path = config or os.path.expanduser("~/.codeverse/config.json")
    ctx.obj['config'] = Config(config_path, DEFAULT_CONFIG)
    ctx.obj['auth'] = AuthManager(ctx.obj['config'])
    ctx.obj['client'] = CodeVerseClient(ctx.obj['config'], ctx.obj['auth'])
    
    if ctx.invoked_subcommand is None:
        print_logo()
        console.print(Panel.fit(
            "[bold cyan]Welcome to CodeVerse CLI![/bold cyan]\n\n"
            "Get started with these commands:\n"
            "• [green]codeverse login[/green] - Authenticate with your account\n"
            "• [green]codeverse chat[/green] - Start an AI conversation\n"
            "• [green]codeverse agents[/green] - List available AI agents\n"
            "• [green]codeverse --help[/green] - Show all commands\n\n"
            "[dim]Visit https://codeverse.ibda.me for documentation[/dim]",
            title="🚀 CodeVerse CLI",
            border_style="cyan"
        ))

@main.command()
@click.option('--email', prompt=True, help='Your email address')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
@click.pass_context
def login(ctx, email, password):
    """🔐 Login to your CodeVerse account"""
    auth_manager = ctx.obj['auth']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Authenticating...", total=None)
        
        try:
            success = auth_manager.login(email, password)
            if success:
                progress.update(task, description="✅ Login successful!")
                console.print("\\n[green]Successfully logged in![/green]")
                console.print(f"Welcome back, [cyan]{auth_manager.get_username()}[/cyan]!")
            else:
                progress.update(task, description="❌ Login failed!")
                console.print("\\n[red]Login failed. Please check your credentials.[/red]")
                sys.exit(1)
        except Exception as e:
            handle_error(f"Login error: {e}")

@main.command()
@click.pass_context
def logout(ctx):
    """🚪 Logout from your CodeVerse account"""
    auth_manager = ctx.obj['auth']
    auth_manager.logout()
    console.print("[green]Logged out successfully![/green]")

@main.command()
@click.option('--agent', '-a', default='general', help='AI agent to chat with')
@click.option('--message', '-m', help='Message to send')
@click.option('--file', '-f', multiple=True, help='Files to include as context')
@click.option('--stream', is_flag=True, default=True, help='Stream responses')
@click.pass_context
def chat(ctx, agent, message, file, stream):
    """💬 Chat with AI agents"""
    client = ctx.obj['client']
    
    if not client.auth.is_authenticated():
        console.print("[red]Please login first with 'codeverse login'[/red]")
        sys.exit(1)
    
    # Include files as context
    context = []
    for file_path in file:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                context.append({
                    "filename": os.path.basename(file_path),
                    "content": f.read(),
                    "path": file_path
                })
    
    if message:
        # Single message mode
        response = client.send_message(message, agent=agent, context=context)
        console.print(f"\\n[cyan]{agent.title()} Agent:[/cyan] {response}")
    else:
        # Interactive chat mode
        console.print(f"\\n[green]Starting chat with {agent.title()} agent...[/green]")
        console.print("[dim]Type 'exit' to quit, 'help' for commands[/dim]\\n")
        
        while True:
            try:
                user_message = Prompt.ask("[bold blue]You[/bold blue]")
                
                if user_message.lower() in ['exit', 'quit', 'bye']:
                    console.print("[green]Goodbye![/green]")
                    break
                elif user_message.lower() == 'help':
                    console.print("""
[cyan]Available commands:[/cyan]
• [green]exit/quit/bye[/green] - End the conversation
• [green]help[/green] - Show this help
• [green]agent <name>[/green] - Switch to different agent
• [green]file <path>[/green] - Add file to context
                    """)
                    continue
                elif user_message.lower().startswith('agent '):
                    agent = user_message.split(' ', 1)[1]
                    console.print(f"[green]Switched to {agent.title()} agent[/green]")
                    continue
                elif user_message.lower().startswith('file '):
                    file_path = user_message.split(' ', 1)[1]
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            context.append({
                                "filename": os.path.basename(file_path),
                                "content": f.read(),
                                "path": file_path
                            })
                        console.print(f"[green]Added {file_path} to context[/green]")
                    else:
                        console.print(f"[red]File not found: {file_path}[/red]")
                    continue
                
                # Send message to AI
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"Thinking...", total=None)
                    response = client.send_message(user_message, agent=agent, context=context)
                
                console.print(f"\\n[cyan]{agent.title()} Agent:[/cyan] {response}\\n")
                
            except KeyboardInterrupt:
                console.print("\\n[yellow]Chat interrupted[/yellow]")
                break
            except Exception as e:
                handle_error(f"Chat error: {e}")

@main.command()
@click.pass_context
def agents(ctx):
    """🤖 List available AI agents"""
    client = ctx.obj['client']
    
    if not client.auth.is_authenticated():
        console.print("[red]Please login first with 'codeverse login'[/red]")
        sys.exit(1)
    
    try:
        agents_list = client.get_agents()
        
        console.print("\\n[bold cyan]Available AI Agents:[/bold cyan]\\n")
        
        for agent in agents_list.get('agents', []):
            status = "🟢" if agent.get('status') == 'active' else "🔴"
            console.print(f"{status} [green]{agent['name']}[/green] - {agent.get('description', 'No description')}")
        
        console.print(f"\\n[dim]Total: {agents_list.get('total', 0)} agents available[/dim]")
        
    except Exception as e:
        handle_error(f"Failed to fetch agents: {e}")

@main.command()
@click.pass_context
def status(ctx):
    """📊 Check CodeVerse platform status"""
    client = ctx.obj['client']
    
    try:
        status_info = client.get_status()
        
        console.print("\\n[bold cyan]CodeVerse Platform Status:[/bold cyan]\\n")
        console.print(f"Status: [green]{status_info.get('status', 'unknown')}[/green]")
        console.print(f"Service: {status_info.get('service', 'unknown')}")
        console.print(f"Version: {status_info.get('version', 'unknown')}")
        console.print(f"Agents Available: {status_info.get('agents_available', 0)}")
        
        infrastructure = status_info.get('infrastructure', {})
        if infrastructure:
            console.print("\\n[cyan]Infrastructure:[/cyan]")
            for service, status in infrastructure.items():
                emoji = "🟢" if status == 'active' else "🔴"
                console.print(f"  {emoji} {service}: [green]{status}[/green]")
        
    except Exception as e:
        handle_error(f"Failed to check status: {e}")

@main.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--watch', is_flag=True, help='Watch files for changes')
@click.pass_context
def sync(ctx, files, watch):
    """📁 Sync files with CodeVerse workspace"""
    client = ctx.obj['client']
    
    if not client.auth.is_authenticated():
        console.print("[red]Please login first with 'codeverse login'[/red]")
        sys.exit(1)
    
    if not files:
        console.print("[yellow]No files specified. Usage: codeverse sync <file1> <file2> ...[/yellow]")
        return
    
    try:
        workspace = os.path.basename(os.getcwd())
        result = client.sync_files(list(files), workspace)
        
        console.print(f"\\n[green]✅ {result['message']}[/green]")
        
        for file_info in result.get('files', []):
            console.print(f"  📄 {file_info['filename']} ({file_info['size']} bytes)")
        
        if watch:
            console.print("\\n[cyan]👀 Watching for file changes... (Press Ctrl+C to stop)[/cyan]")
            # TODO: Implement file watching
            
    except Exception as e:
        handle_error(f"Sync error: {e}")

@main.command()
@click.pass_context
def init(ctx):
    """🚀 Initialize CodeVerse in current directory"""
    config_file = ".codeverse.json"
    
    if os.path.exists(config_file):
        if not Confirm.ask(f"[yellow]{config_file} already exists. Overwrite?[/yellow]"):
            return
    
    project_name = Prompt.ask("Project name", default=os.path.basename(os.getcwd()))
    description = Prompt.ask("Description", default="A CodeVerse project")
    
    config_data = {
        "name": project_name,
        "description": description,
        "version": "1.0.0",
        "created": str(Path.cwd()),
        "agents": {
            "preferred": ["code_generator", "code_reviewer", "debugger"],
            "excluded": []
        },
        "sync": {
            "include": ["*.py", "*.js", "*.ts", "*.md", "*.txt"],
            "exclude": ["node_modules", "__pycache__", ".git", "*.pyc"]
        }
    }
    
    with open(config_file, 'w') as f:
        import json
        json.dump(config_data, f, indent=2)
    
    console.print(f"\\n[green]✅ Initialized CodeVerse project: {project_name}[/green]")
    console.print(f"📄 Created {config_file}")
    console.print("\\n[cyan]Next steps:[/cyan]")
    console.print("1. [green]codeverse login[/green] - Authenticate")
    console.print("2. [green]codeverse sync *.py[/green] - Sync your files")
    console.print("3. [green]codeverse chat[/green] - Start coding with AI")

if __name__ == "__main__":
    main()