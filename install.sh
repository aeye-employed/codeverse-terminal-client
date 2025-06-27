#!/bin/bash
# CodeVerse CLI Installation Script
# Author: IBDA AI LTD
# Website: https://codeverse.ibda.me

set -e

echo "======================================"
echo "CodeVerse CLI Installer"
echo "by IBDA AI LTD"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python $python_version found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install the package
echo ""
echo "Installing CodeVerse CLI..."
pip install -e .

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "To get started:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Initialize connection to your server:"
echo "   codeverse init"
echo ""
echo "3. Start coding with AI assistance:"
echo "   codeverse chat"
echo ""
echo "For more information, see README.md"
echo ""
echo "Website: https://codeverse.ibda.me"
echo "Company: https://ibda.me"
echo ""