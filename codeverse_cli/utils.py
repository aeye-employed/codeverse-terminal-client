"""
CodeVerse CLI Utilities
Helper functions and utilities
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

def print_version():
    """Print version information"""
    from . import __version__, __author__, __email__
    
    console.print(f"""
[bold cyan]CodeVerse CLI[/bold cyan] [green]v{__version__}[/green]

[dim]AI-Powered Development Assistant[/dim]
Author: {__author__}
Email: {__email__}
Website: https://codeverse.ibda.me
Documentation: https://docs.codeverse.ibda.me

[yellow]Features:[/yellow]
• 54 specialized AI agents
• Real-time code generation
• Intelligent code review
• File synchronization
• WebSocket streaming
• Secure authentication

[dim]© 2025 IBDA AI LTD. All rights reserved.[/dim]
    """)

def print_logo():
    """Print CodeVerse ASCII logo"""
    logo = Text("""
 ██████╗ ██████╗ ██████╗ ███████╗██╗   ██╗███████╗██████╗ ███████╗███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝
██║     ██║   ██║██║  ██║█████╗  ██║   ██║█████╗  ██████╔╝███████╗█████╗  
██║     ██║   ██║██║  ██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══╝  
╚██████╗╚██████╔╝██████╔╝███████╗ ╚████╔╝ ███████╗██║  ██║███████║███████╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
    """, style="bold cyan")
    
    console.print(logo)
    console.print("[dim]AI-Powered Development Assistant[/dim]", justify="center")
    console.print()

def handle_error(message: str, exit_code: int = 1):
    """Handle and display errors"""
    console.print(f"[red]❌ Error:[/red] {message}")
    sys.exit(exit_code)

def handle_warning(message: str):
    """Handle and display warnings"""
    console.print(f"[yellow]⚠️  Warning:[/yellow] {message}")

def handle_success(message: str):
    """Handle and display success messages"""
    console.print(f"[green]✅ Success:[/green] {message}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def create_status_table(data: dict) -> Table:
    """Create a formatted status table"""
    table = Table(title="CodeVerse Platform Status", box=box.ROUNDED)
    
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")
    
    # Add main status
    status = data.get('status', 'unknown')
    status_emoji = "🟢" if status == 'healthy' else "🔴"
    table.add_row(
        "Platform",
        f"{status_emoji} {status.title()}",
        f"v{data.get('version', 'unknown')}"
    )
    
    # Add infrastructure status
    infrastructure = data.get('infrastructure', {})
    for service, status in infrastructure.items():
        status_emoji = "🟢" if status == 'active' else "🔴"
        table.add_row(
            service.replace('_', ' ').title(),
            f"{status_emoji} {status.title()}",
            ""
        )
    
    return table

def create_agents_table(agents_data: dict) -> Table:
    """Create a formatted agents table"""
    table = Table(title="Available AI Agents", box=box.ROUNDED)
    
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Description", style="dim")
    
    agents = agents_data.get('agents', [])
    for agent in agents:
        status = agent.get('status', 'unknown')
        status_emoji = "🟢" if status == 'active' else "🔴"
        
        table.add_row(
            agent.get('name', 'unknown'),
            f"{status_emoji} {status.title()}",
            agent.get('type', 'unknown').title(),
            agent.get('description', 'No description')[:50] + "..." if len(agent.get('description', '')) > 50 else agent.get('description', '')
        )
    
    return table

def create_files_table(files_data: list) -> Table:
    """Create a formatted files table"""
    table = Table(title="Synced Files", box=box.ROUNDED)
    
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Size", style="green")
    table.add_column("Path", style="dim")
    
    for file_info in files_data:
        filename = file_info.get('filename', 'unknown')
        size = format_file_size(file_info.get('size', 0))
        path = file_info.get('path', '')
        
        # Truncate long paths
        if len(path) > 40:
            path = "..." + path[-37:]
        
        table.add_row(filename, size, path)
    
    return table

def validate_project_structure(project_path: str = None) -> bool:
    """Validate if current directory is a valid CodeVerse project"""
    if not project_path:
        project_path = os.getcwd()
    
    config_file = os.path.join(project_path, '.codeverse.json')
    return os.path.exists(config_file)

def get_project_info(project_path: str = None) -> dict:
    """Get project information from .codeverse.json"""
    if not project_path:
        project_path = os.getcwd()
    
    config_file = os.path.join(project_path, '.codeverse.json')
    
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    return {}

def find_files_by_pattern(directory: str, patterns: list) -> list:
    """Find files matching patterns in directory"""
    import glob
    
    matched_files = []
    
    for pattern in patterns:
        # Use glob to find matching files
        matches = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
        matched_files.extend(matches)
    
    return list(set(matched_files))  # Remove duplicates

def is_text_file(file_path: str) -> bool:
    """Check if file is a text file"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' not in chunk
    except IOError:
        return False

def get_file_content_preview(file_path: str, max_lines: int = 10) -> str:
    """Get a preview of file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) <= max_lines:
            return ''.join(lines)
        else:
            preview = ''.join(lines[:max_lines])
            preview += f"\n... ({len(lines) - max_lines} more lines)"
            return preview
            
    except (IOError, UnicodeDecodeError):
        return "Unable to preview file content"

def create_progress_callback(console, description: str):
    """Create a progress callback for long operations"""
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    def callback(current: int, total: int):
        percentage = (current / total) * 100 if total > 0 else 0
        console.print(f"\r{description}: {percentage:.1f}%", end="")
    
    return callback