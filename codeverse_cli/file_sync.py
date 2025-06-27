"""
File synchronization between local and cloud
"""

import os
import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import aiofiles
import fnmatch

class FileSync:
    """Handles file synchronization between local and cloud"""
    
    def __init__(self, client):
        self.client = client
        self.ignore_patterns = self._load_gitignore()
        
    def _load_gitignore(self) -> List[str]:
        """Load .gitignore patterns"""
        patterns = [
            '.git', '__pycache__', '*.pyc', '.env', '.venv',
            'node_modules', 'dist', 'build', '.DS_Store',
            '*.log', '*.tmp', '.idea', '.vscode'
        ]
        
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def _should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        path_obj = Path(path)
        
        # Check each pattern
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_obj.name, pattern):
                return True
            if fnmatch.fnmatch(str(path_obj), pattern):
                return True
        
        return False
    
    async def sync_directory(self, directory: str) -> List[str]:
        """Sync entire directory to cloud"""
        synced_files = []
        
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if self._should_ignore(file_path):
                    continue
                
                # Get relative path
                rel_path = os.path.relpath(file_path, directory)
                
                # Read file content
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    # Upload to server
                    if await self.client.upload_file(rel_path, content):
                        synced_files.append(rel_path)
                except Exception:
                    # Skip binary or unreadable files
                    pass
        
        return synced_files
    
    async def sync_file(self, file_path: str) -> bool:
        """Sync a single file"""
        if self._should_ignore(file_path):
            return False
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            rel_path = os.path.relpath(file_path, os.getcwd())
            return await self.client.upload_file(rel_path, content)
        except Exception:
            return False
    
    async def watch_directory(self, directory: str):
        """Watch directory for changes and sync automatically"""
        event_handler = FileSyncHandler(self)
        observer = Observer()
        observer.schedule(event_handler, directory, recursive=True)
        observer.start()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
    
    async def apply_changes(self, response: str):
        """Apply file changes from server response"""
        # Parse file changes from response
        lines = response.split('\n')
        in_file_change = False
        current_file = None
        file_content = []
        
        for line in lines:
            if line.startswith('[FILE_CHANGE]'):
                # Save previous file if any
                if current_file and file_content:
                    await self._write_file(current_file, '\n'.join(file_content))
                
                # Parse new file
                parts = line.split(' ')
                current_file = parts[1].rstrip(':')
                action = parts[2]
                file_content = []
                in_file_change = True
            elif line.startswith('[/FILE_CHANGE]'):
                # Save current file
                if current_file and file_content:
                    await self._write_file(current_file, '\n'.join(file_content))
                
                in_file_change = False
                current_file = None
                file_content = []
            elif in_file_change:
                file_content.append(line)
    
    async def _write_file(self, file_path: str, content: str):
        """Write file locally"""
        full_path = Path(os.getcwd()) / file_path
        
        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)


class FileSyncHandler(FileSystemEventHandler):
    """Handle file system events for auto-sync"""
    
    def __init__(self, file_sync):
        self.file_sync = file_sync
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.loop.run_until_complete(self.file_sync.sync_file(event.src_path))
    
    def on_created(self, event):
        if not event.is_directory:
            self.loop.run_until_complete(self.file_sync.sync_file(event.src_path))