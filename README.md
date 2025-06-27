# CodeVerse CLI - AI-Powered Development Assistant

🚀 **Transform your development workflow with 54 specialized AI agents**

CodeVerse CLI is a production-ready command-line interface that brings the power of AI directly to your terminal. Build 10x faster with intelligent code generation, review, debugging, and optimization.

## ✨ Features

- **54 Specialized AI Agents** - Code generation, review, debugging, testing, and more
- **Real-time Streaming** - WebSocket-powered live responses
- **File Synchronization** - Seamless workspace sync
- **Secure Authentication** - Encrypted token storage
- **Cross-platform** - Windows, macOS, Linux support
- **Rich CLI Experience** - Beautiful terminal UI with Rich

## 🚀 Quick Installation

### Option 1: pip (Recommended)
```bash
pip install codeverse-cli
```

### Option 2: npm
```bash
npm install -g @codeverse/cli
```

### Option 3: Direct Download
```bash
# Linux/macOS
curl -fsSL https://install.codeverse.ibda.me | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://install.codeverse.ibda.me/install.ps1" | Invoke-Expression
```

## 🎯 Quick Start

1. **Login to your account**
   ```bash
   codeverse login
   ```

2. **Initialize a project**
   ```bash
   codeverse init
   ```

3. **Start chatting with AI**
   ```bash
   codeverse chat
   ```

4. **Sync your files**
   ```bash
   codeverse sync *.py
   ```

## 💡 Usage Examples

### Interactive AI Chat
```bash
# Start general chat
codeverse chat

# Chat with specific agent
codeverse chat --agent code_generator

# Send direct message
codeverse chat -m "Generate a Python class for user authentication"

# Include files as context
codeverse chat -f app.py -f config.py
```

### File Operations
```bash
# Sync files to workspace
codeverse sync src/*.py tests/*.py

# Watch files for changes
codeverse sync --watch src/

# Download files from workspace
codeverse download results.txt
```

### Agent Management
```bash
# List all available agents
codeverse agents

# Check platform status
codeverse status
```

### Project Management
```bash
# Initialize CodeVerse project
codeverse init

# Show project information
codeverse info

# Configure project settings
codeverse config
```

## 🤖 Available AI Agents

| Agent | Description |
|-------|-------------|
| **code_generator** | Generate code from natural language descriptions |
| **code_reviewer** | Review code for best practices and potential issues |
| **debugger** | Help debug code and find issues |
| **testing** | Generate and run tests for your code |
| **documentation** | Create comprehensive documentation |
| **refactoring** | Optimize and refactor existing code |
| **security_scanner** | Scan for security vulnerabilities |
| **performance_optimization** | Optimize code performance |
| **api_designer** | Design REST APIs and GraphQL schemas |
| **database_designer** | Design database schemas and queries |
| ... and 44 more specialized agents!

## 📁 Project Configuration

Create a `.codeverse.json` file in your project root:

```json
{
  "name": "my-project",
  "description": "A CodeVerse-powered project",
  "version": "1.0.0",
  "agents": {
    "preferred": ["code_generator", "code_reviewer", "debugger"],
    "excluded": []
  },
  "sync": {
    "include": ["*.py", "*.js", "*.ts", "*.md"],
    "exclude": ["node_modules", "__pycache__", ".git"]
  }
}
```

## 🔧 Configuration

### Global Configuration
Located at `~/.codeverse/config.json`:

```json
{
  "api_url": "https://userapi-codeverse.ibda.me",
  "agents_url": "https://api-codeverse.ibda.me",
  "websocket_url": "wss://userapi-codeverse.ibda.me/ws",
  "timeout": 30,
  "max_retries": 3
}
```

### Environment Variables
```bash
export CODEVERSE_API_URL="https://userapi-codeverse.ibda.me"
export CODEVERSE_AGENTS_URL="https://api-codeverse.ibda.me"
export CODEVERSE_WEBSOCKET_URL="wss://userapi-codeverse.ibda.me/ws"
```

## 🔐 Authentication

CodeVerse CLI uses secure token-based authentication:

- **Encrypted Storage** - Tokens are encrypted using Fernet encryption
- **Keyring Integration** - Uses system keyring when available
- **Auto-refresh** - Automatically refreshes expired tokens
- **Secure Permissions** - Config files have restrictive permissions (600)

## 🌐 API Endpoints

The CLI communicates with these endpoints:

- **Authentication**: `POST /api/auth/login`
- **Chat**: `POST /api/chat`
- **File Upload**: `POST /api/files/upload`
- **File Download**: `GET /api/files/download`
- **File Sync**: `POST /api/files/sync`
- **Agents List**: `GET /api/agents`
- **Status**: `GET /api/status`
- **WebSocket**: `WSS /ws`

## 🚀 Advanced Usage

### Streaming Responses
```bash
# Enable streaming for real-time responses
codeverse chat --stream "Explain how React hooks work"
```

### Batch Operations
```bash
# Process multiple files
codeverse review src/*.py --agent code_reviewer

# Generate tests for all Python files
codeverse generate-tests src/*.py
```

### Custom Workflows
```bash
# Code review workflow
codeverse sync src/
codeverse chat -a code_reviewer -m "Review the uploaded code for issues"

# Documentation workflow  
codeverse sync src/ docs/
codeverse chat -a documentation -m "Update documentation based on code changes"
```

## 🛠️ Development

### Local Development
```bash
# Clone repository
git clone https://github.com/ibda-ai/codeverse-cli.git
cd codeverse-cli

# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Format code
black codeverse_cli/
isort codeverse_cli/
```

### Building Distribution
```bash
# Build wheel
python setup.py bdist_wheel

# Upload to PyPI
twine upload dist/*
```

## 📚 Documentation

- **Website**: https://codeverse.ibda.me
- **Documentation**: https://docs.codeverse.ibda.me
- **API Reference**: https://api.codeverse.ibda.me/docs
- **GitHub**: https://github.com/ibda-ai/codeverse-cli

## 🆘 Support

- **Issues**: https://github.com/ibda-ai/codeverse-cli/issues
- **Discussions**: https://github.com/ibda-ai/codeverse-cli/discussions
- **Email**: support@ibda.me
- **Discord**: https://discord.gg/codeverse

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏢 About IBDA AI

CodeVerse CLI is developed by [IBDA AI LTD](https://ibda.me), a leading AI company focused on transforming software development with intelligent automation.

---

**© 2025 IBDA AI LTD. All rights reserved.**