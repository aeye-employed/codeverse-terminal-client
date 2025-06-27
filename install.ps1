# CodeVerse CLI Installation Script for Windows
# PowerShell script for installing CodeVerse CLI

param(
    [switch]$Force = $false
)

# Colors for output (Windows 10+)
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Blue"
$HeaderColor = "Cyan"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "$Prefix " -ForegroundColor $Color -NoNewline
    }
    Write-Host $Message -ForegroundColor $Color
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput -Message "Error: $Message" -Color $ErrorColor -Prefix "❌"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput -Message $Message -Color $SuccessColor -Prefix "✅"
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-ColorOutput -Message $Message -Color $WarningColor -Prefix "⚠️"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput -Message $Message -Color $InfoColor -Prefix "ℹ️"
}

function Write-Header {
    param([string]$Message)
    Write-ColorOutput -Message $Message -Color $HeaderColor -Prefix "🚀"
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if Python 3.8+ is installed
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -eq 3 -and $minor -ge 8) {
                Write-Success "Python $($matches[0]) found"
                return $true
            } else {
                Write-Error-Custom "Python 3.8+ required, found $($matches[0])"
                return $false
            }
        }
    } catch {
        # Try python3
        try {
            $pythonVersion = python3 --version 2>$null
            if ($pythonVersion -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                
                if ($major -eq 3 -and $minor -ge 8) {
                    Write-Success "Python $($matches[0]) found"
                    return $true
                }
            }
        } catch {}
    }
    
    Write-Error-Custom "Python 3.8+ not found"
    return $false
}

# Install Python using winget or chocolatey
function Install-Python {
    Write-Info "Installing Python 3..."
    
    # Try winget first (Windows 10+)
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        try {
            winget install Python.Python.3.12
            Write-Success "Python installed via winget"
            return $true
        } catch {
            Write-Warning-Custom "Failed to install Python via winget"
        }
    }
    
    # Try chocolatey
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        try {
            choco install python3 -y
            Write-Success "Python installed via chocolatey"
            return $true
        } catch {
            Write-Warning-Custom "Failed to install Python via chocolatey"
        }
    }
    
    Write-Error-Custom "Unable to install Python automatically"
    Write-Info "Please install Python 3.8+ manually from https://python.org"
    return $false
}

# Check if pip is available
function Test-Pip {
    try {
        $pipVersion = pip --version 2>$null
        if ($pipVersion) {
            Write-Success "pip found"
            return $true
        }
    } catch {}
    
    Write-Error-Custom "pip not found"
    return $false
}

# Install CodeVerse CLI
function Install-CodeVerse {
    Write-Info "Installing CodeVerse CLI..."
    
    try {
        pip install codeverse-cli
        Write-Success "CodeVerse CLI installed successfully"
        return $true
    } catch {
        Write-Error-Custom "Failed to install CodeVerse CLI: $($_.Exception.Message)"
        return $false
    }
}

# Verify installation
function Test-Installation {
    Write-Info "Verifying installation..."
    
    try {
        $version = codeverse --version 2>$null
        if ($version) {
            Write-Success "CodeVerse CLI installed successfully!"
            Write-Info "Version: $version"
            return $true
        }
    } catch {}
    
    Write-Error-Custom "Installation verification failed"
    return $false
}

# Add to PATH if needed
function Add-ToPath {
    $pythonScripts = "$env:APPDATA\Python\Python311\Scripts"
    $pythonLocalScripts = "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
    
    $pathToAdd = $null
    
    if (Test-Path $pythonScripts) {
        $pathToAdd = $pythonScripts
    } elseif (Test-Path $pythonLocalScripts) {
        $pathToAdd = $pythonLocalScripts
    }
    
    if ($pathToAdd -and $env:PATH -notlike "*$pathToAdd*") {
        Write-Info "Adding $pathToAdd to PATH..."
        $env:PATH += ";$pathToAdd"
        
        # Add to user PATH permanently
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($userPath -notlike "*$pathToAdd*") {
            [Environment]::SetEnvironmentVariable("PATH", "$userPath;$pathToAdd", "User")
            Write-Success "Added to user PATH"
        }
    }
}

# Main installation function
function Install-Main {
    Write-Header "CodeVerse CLI Installation"
    Write-Host "AI-Powered Development Assistant" -ForegroundColor Gray
    Write-Host "© 2025 IBDA AI LTD" -ForegroundColor Gray
    Write-Host ""
    
    # Check for administrator privileges
    if (Test-Administrator) {
        Write-Warning-Custom "Running as administrator is not recommended"
    }
    
    # Check Python
    if (-not (Test-Python)) {
        Write-Warning-Custom "Python 3.8+ not found. Attempting to install..."
        
        if (-not (Install-Python)) {
            Write-Error-Custom "Failed to install Python"
            exit 1
        }
        
        # Refresh PATH and check again
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        if (-not (Test-Python)) {
            Write-Error-Custom "Python installation failed"
            exit 1
        }
    }
    
    # Check pip
    if (-not (Test-Pip)) {
        Write-Error-Custom "pip not found. Please ensure pip is installed with Python"
        exit 1
    }
    
    # Install CodeVerse CLI
    if (-not (Install-CodeVerse)) {
        Write-Error-Custom "Failed to install CodeVerse CLI"
        exit 1
    }
    
    # Add to PATH
    Add-ToPath
    
    # Verify installation
    if (Test-Installation) {
        Write-Host ""
        Write-Header "Installation Complete!"
        Write-Host ""
        Write-Info "Get started with these commands:"
        Write-Host "  " -NoNewline
        Write-Host "codeverse login" -ForegroundColor Green -NoNewline
        Write-Host "     - Login to your account"
        Write-Host "  " -NoNewline
        Write-Host "codeverse init" -ForegroundColor Green -NoNewline
        Write-Host "      - Initialize a new project"
        Write-Host "  " -NoNewline
        Write-Host "codeverse chat" -ForegroundColor Green -NoNewline
        Write-Host "      - Start chatting with AI"
        Write-Host "  " -NoNewline
        Write-Host "codeverse --help" -ForegroundColor Green -NoNewline
        Write-Host "    - Show all commands"
        Write-Host ""
        Write-Info "Documentation: https://docs.codeverse.ibda.me"
        Write-Info "Support: https://github.com/ibda-ai/codeverse-cli/issues"
        Write-Host ""
        Write-Warning-Custom "Restart your PowerShell/Command Prompt to use the CLI"
    } else {
        Write-Error-Custom "Installation failed. Please check the errors above."
        exit 1
    }
}

# Run installation
try {
    Install-Main
} catch {
    Write-Error-Custom "Installation failed with exception: $($_.Exception.Message)"
    exit 1
}