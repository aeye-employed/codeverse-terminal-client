#!/bin/bash
# CodeVerse CLI Installation Script
# Works on Linux and macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print with colors
print_error() { echo -e "${RED}❌ Error: $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_header() { echo -e "${CYAN}🚀 $1${NC}"; }

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

print_header "CodeVerse CLI Installation"
echo "AI-Powered Development Assistant"
echo "© 2025 IBDA AI LTD"
echo

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_info "Detected OS: $OS"

# Check if Python 3.8+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Install Python if needed
install_python() {
    print_info "Installing Python 3..."
    
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S python python-pip
        else
            print_error "Unable to install Python automatically. Please install Python 3.8+ manually."
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install python3
        else
            print_error "Homebrew not found. Please install Python 3.8+ manually or install Homebrew first."
            exit 1
        fi
    fi
}

# Check and install pip
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        return 0
    elif command -v pip &> /dev/null; then
        # Check if pip is for Python 3
        PIP_VERSION=$(pip --version | grep -o 'python [0-9.]*' | grep -o '[0-9.]*')
        if [[ $PIP_VERSION == 3.* ]]; then
            print_success "pip (Python 3) found"
            return 0
        fi
    fi
    
    print_error "pip for Python 3 not found"
    return 1
}

# Install CodeVerse CLI
install_codeverse() {
    print_info "Installing CodeVerse CLI..."
    
    # Try pip3 first, then pip
    if command -v pip3 &> /dev/null; then
        pip3 install --user codeverse-cli
    elif command -v pip &> /dev/null; then
        pip install --user codeverse-cli
    else
        print_error "pip not found"
        exit 1
    fi
}

# Add to PATH if needed
setup_path() {
    USER_BIN_DIR="$HOME/.local/bin"
    
    if [[ ":$PATH:" != *":$USER_BIN_DIR:"* ]]; then
        print_info "Adding $USER_BIN_DIR to PATH..."
        
        # Add to appropriate shell config
        if [[ -f "$HOME/.bashrc" ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            print_success "Added to ~/.bashrc"
        fi
        
        if [[ -f "$HOME/.zshrc" ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            print_success "Added to ~/.zshrc"
        fi
        
        # Export for current session
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    if command -v codeverse &> /dev/null; then
        VERSION=$(codeverse --version 2>/dev/null | head -n 1 || echo "unknown")
        print_success "CodeVerse CLI installed successfully!"
        print_info "Version: $VERSION"
        return 0
    else
        print_error "Installation verification failed"
        return 1
    fi
}

# Main installation process
main() {
    # Check Python
    if ! check_python; then
        print_warning "Python 3.8+ not found. Attempting to install..."
        install_python
        
        if ! check_python; then
            print_error "Failed to install Python 3.8+"
            exit 1
        fi
    fi
    
    # Check pip
    if ! check_pip; then
        print_error "Please install pip for Python 3"
        exit 1
    fi
    
    # Install CodeVerse CLI
    install_codeverse
    
    # Setup PATH
    setup_path
    
    # Verify installation
    if verify_installation; then
        echo
        print_header "Installation Complete!"
        echo
        print_info "Get started with these commands:"
        echo "  ${GREEN}codeverse login${NC}     - Login to your account"
        echo "  ${GREEN}codeverse init${NC}      - Initialize a new project"
        echo "  ${GREEN}codeverse chat${NC}      - Start chatting with AI"
        echo "  ${GREEN}codeverse --help${NC}    - Show all commands"
        echo
        print_info "Documentation: https://docs.codeverse.ibda.me"
        print_info "Support: https://github.com/ibda-ai/codeverse-cli/issues"
        echo
        print_warning "Restart your terminal or run 'source ~/.bashrc' to use the CLI"
    else
        print_error "Installation failed. Please check the errors above."
        exit 1
    fi
}

# Run main function
main "$@"