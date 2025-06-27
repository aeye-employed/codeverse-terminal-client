# CodeVerse CLI

Local CLI client for CodeVerse Terminal - AI-powered development platform by IBDA AI LTD

🌐 Website: [https://codeverse.ibda.me](https://codeverse.ibda.me)  
🏢 Company: [IBDA AI LTD](https://ibda.me)

## Overview

CodeVerse CLI enables you to code on your local machine while leveraging the full power of the CodeVerse Terminal cloud platform. Similar to Claude Code, it provides an intuitive interface for AI-assisted development with 54 specialized agents working in unison.

## Features

- 🤖 **AI-Powered Development**: Access all 54 specialized agents from your terminal
- 📁 **Automatic File Sync**: Real-time bidirectional file synchronization
- 🔐 **Secure Authentication**: Encrypted credential storage
- 💬 **Interactive Chat**: Natural language programming interface
- 🌊 **Streaming Responses**: Real-time streaming output like Claude Code
- 🎯 **Agent-Specific Tasks**: Direct access to specialized agents
- 📊 **Live File Updates**: Automatic application of code changes
- 🔄 **Watch Mode**: Auto-sync file changes as you code

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Access to a CodeVerse Terminal server

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/codeverse-terminal.git
cd codeverse-terminal/client/codeverse-cli

# Install in development mode
pip install -e .
```

### Install via pip (when published)

```bash
pip install codeverse-cli
```

## Quick Start

### 1. Initialize Connection

```bash
# With prompts
codeverse init

# Or directly
codeverse init --host your-server.com --port 8000 --token your-api-token
```

### 2. Login (Alternative to token)

```bash
codeverse login --host your-server.com --port 8000
```

### 3. Start Coding

```bash
# Interactive chat mode (like Claude Code)
codeverse chat

# Send a single message
codeverse chat "Create a REST API for user management"

# With file context
codeverse chat "Refactor this code for better performance" -c main.py -c utils.py

# Sync files before chatting
codeverse chat "Add tests for all functions" --sync-files
```

## Commands

### `codeverse init`
Initialize connection to CodeVerse Terminal server.

```bash
codeverse init --host <host> --port <port> --token <token>
```

### `codeverse login`
Authenticate with username and password.

```bash
codeverse login --host <host> --port <port> --username <username>
```

### `codeverse chat`
Interactive AI chat interface (main command).

```bash
# Interactive mode
codeverse chat

# Single message
codeverse chat "Your message here"

# With context files
codeverse chat "Explain this code" -c file1.py -c file2.js

# Sync files first
codeverse chat "Debug this issue" --sync-files

# Non-streaming mode
codeverse chat "Generate documentation" --no-stream
```

### `codeverse sync`
Synchronize files between local and cloud.

```bash
# Sync once
codeverse sync

# Watch for changes
codeverse sync --watch
```

### `codeverse run`
Run specific tasks with specialized agents.

```bash
# Auto-detect agent
codeverse run "generate unit tests"

# Specify agent
codeverse run "optimize database queries" --agent performance_optimization
```

### `codeverse status`
Check connection and server status.

```bash
codeverse status
```

## Interactive Mode Commands

When in interactive chat mode, you can use these commands:

- `/help` - Show available commands
- `/agents` - List all available agents
- `/agent <name> <task>` - Run task with specific agent
- `/sync` - Sync current directory
- `/status` - Show connection status
- `/clear` - Clear screen
- `/exit` or `exit` - Exit interactive mode

## Available Agents

The platform includes 54 specialized agents:

### Core Development Agents
- `api_designer` - API design and OpenAPI specs
- `database_designer` - Database schema design
- `figma_agent` - UI/UX design integration
- `github_agent` - GitHub operations
- `solution_architect` - System architecture
- `blockchain_agent` - Blockchain development
- `file_monitoring` - File system operations
- `loop_prevention` - Prevent infinite loops
- `permission_management` - Access control
- `saas_expert` - SaaS best practices
- `open_source_expert` - Open source guidelines

### Specialized Agents
- `code_generator` - Generate code
- `code_reviewer` - Review code quality
- `testing` - Create and run tests
- `documentation` - Generate docs
- `performance_optimization` - Optimize code
- `security_scanner` - Security analysis
- `formatter_linter` - Code formatting
- `debugger` - Debug issues
- `refactoring` - Refactor code
- `git_operations` - Git workflows
- `dependency_manager` - Manage dependencies
- `ci_cd` - CI/CD pipelines
- `containerization` - Docker/K8s
- `api_integration` - API integration
- `database_operations` - Database queries
- `testing_automation` - Test automation
- `code_analysis` - Static analysis
- `project_migration` - Migrate projects
- `config_management` - Configuration
- `monitoring_logging` - Observability

## Configuration

Configuration is stored in `~/.codeverse/config.json` with encrypted credentials.

### Environment Variables

- `CODEVERSE_HOST` - Server hostname
- `CODEVERSE_PORT` - Server port
- `CODEVERSE_TOKEN` - API token

### Workspace Configuration

Create `.codeverse.json` in your project root:

```json
{
  "ignore": [
    "node_modules",
    "*.log",
    ".env"
  ],
  "default_agent": "orchestrator",
  "auto_sync": true
}
```

## File Synchronization

The CLI automatically syncs files between your local machine and the cloud platform:

1. **Automatic Sync**: Files are synced when you run commands
2. **Watch Mode**: `codeverse sync --watch` monitors changes
3. **Ignore Patterns**: Respects `.gitignore` and `.codeverse.json`
4. **Bidirectional**: Changes from agents are applied locally

## Security

- Credentials are encrypted using Fernet encryption
- Config files have restricted permissions (600)
- Supports secure WebSocket connections
- Token-based authentication with refresh capability

## Examples

### Create a New Feature

```bash
codeverse chat "Create a user authentication system with JWT tokens, including login, register, and password reset endpoints"
```

### Review and Improve Code

```bash
codeverse chat "Review this code for security vulnerabilities and performance issues" -c src/api.py
```

### Generate Tests

```bash
codeverse run "generate comprehensive unit tests with 100% coverage"
```

### Fix Bugs

```bash
codeverse chat "Debug why the API returns 500 errors on POST requests" --sync-files
```

### Use Specific Agent

```bash
codeverse run "analyze and improve database query performance" --agent database_operations
```

## Troubleshooting

### Connection Issues

```bash
# Check status
codeverse status

# Re-initialize
codeverse init

# Verify server is accessible
curl http://your-server:8000/health
```

### Authentication Failed

```bash
# Try login instead of token
codeverse login

# Or regenerate token
codeverse init --token new-token
```

### File Sync Issues

```bash
# Check ignore patterns
cat .gitignore
cat .codeverse.json

# Force sync
codeverse sync

# Check file permissions
ls -la
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building

```bash
python setup.py build
```

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

- 📧 Email: contact@ibda.me
- 🌐 Website: https://codeverse.ibda.me
- 📖 Documentation: https://docs.codeverse.ibda.me
- 🐛 Issues: https://github.com/your-org/codeverse-terminal/issues

## License

Copyright © 2024 IBDA AI LTD. All rights reserved.

---

Made with ❤️ by [IBDA AI LTD](https://ibda.me)