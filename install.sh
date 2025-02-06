#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored text
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to print section header
print_header() {
    echo
    print_color $MAGENTA "======================================"
    print_color $MAGENTA "   $1"
    print_color $MAGENTA "======================================"
    echo
}

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

# Function to detect system type
detect_system() {
    if [ -f /data/data/com.termux/files/usr/bin/termux-info ]; then
        echo "termux"
    else
        echo "linux"
    fi
}

# Function to check Python version
check_python_version() {
    if ! check_command python3; then
        return 1
    fi
    
    version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if (( $(echo "$version < 3.7" | bc -l) )); then
        return 1
    fi
    return 0
}

# Function to install dependencies for Linux
install_linux_deps() {
    print_header "Installing Linux Dependencies"
    
    # Check for sudo
    if ! check_command sudo; then
        print_color $RED "Error: 'sudo' is required but not installed."
        exit 1
    fi
    
    # Update package lists
    print_color $YELLOW "Updating package lists..."
    sudo apt update || {
        print_color $RED "Failed to update package lists"
        exit 1
    }
    
    # Install required packages
    print_color $YELLOW "Installing required packages..."
    sudo apt install -y python3 python3-pip ffmpeg git || {
        print_color $RED "Failed to install required packages"
        exit 1
    }
}

# Function to install dependencies for Termux
install_termux_deps() {
    print_header "Installing Termux Dependencies"
    
    # Update package lists
    print_color $YELLOW "Updating package lists..."
    pkg update && pkg upgrade -y || {
        print_color $RED "Failed to update Termux packages"
        exit 1
    }
    
    # Install required packages
    print_color $YELLOW "Installing required packages..."
    pkg install -y python ffmpeg git || {
        print_color $RED "Failed to install required packages"
        exit 1
    }
    
    # Setup storage
    print_color $YELLOW "Setting up storage access..."
    termux-setup-storage || {
        print_color $YELLOW "Warning: Could not setup storage. You may need to grant permissions manually."
    }
}

# Main installation function
main() {
    print_header "YT4-DW Professional Installer"
    print_color $CYAN "Version: 3.0.0"
    echo
    
    # Detect system type
    SYSTEM_TYPE=$(detect_system)
    print_color $YELLOW "Detected system type: $SYSTEM_TYPE"
    
    # Install system-specific dependencies
    if [ "$SYSTEM_TYPE" = "termux" ]; then
        install_termux_deps
    else
        install_linux_deps
    fi
    
    # Check Python version
    print_color $YELLOW "Checking Python version..."
    if ! check_python_version; then
        print_color $RED "Error: Python 3.7 or higher is required"
        exit 1
    fi
    print_color $GREEN "✓ Python version check passed"
    
    # Create installation directory
    print_header "Setting up YT4-DW"
    INSTALL_DIR="$HOME/yt4-dw"
    
    # Remove existing installation if present
    if [ -d "$INSTALL_DIR" ]; then
        print_color $YELLOW "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    print_color $YELLOW "Cloning YT4-DW repository..."
    git clone https://github.com/lyssadev/yt4-dw.git "$INSTALL_DIR" || {
        print_color $RED "Failed to clone repository"
        exit 1
    }
    
    # Change to installation directory
    cd "$INSTALL_DIR" || {
        print_color $RED "Failed to access installation directory"
        exit 1
    }
    
    # Install Python dependencies
    print_header "Installing Python Dependencies"
    print_color $YELLOW "Installing required Python packages..."
    pip3 install -r requirements.txt || {
        print_color $RED "Failed to install Python dependencies"
        exit 1
    }
    
    # Create necessary directories
    print_color $YELLOW "Creating required directories..."
    mkdir -p "$HOME/Downloads/yt4-dw"
    mkdir -p "$INSTALL_DIR/cookies"
    
    # Set executable permissions
    chmod +x "$INSTALL_DIR/src/main.py"
    
    # Create symbolic link (Linux only)
    if [ "$SYSTEM_TYPE" = "linux" ]; then
        print_color $YELLOW "Creating command shortcut..."
        sudo ln -sf "$INSTALL_DIR/src/main.py" /usr/local/bin/yt4-dw
    fi
    
    # Installation complete
    print_header "Installation Complete!"
    print_color $GREEN "✓ YT4-DW has been successfully installed!"
    echo
    print_color $CYAN "Usage Instructions:"
    if [ "$SYSTEM_TYPE" = "linux" ]; then
        echo "  Run 'yt4-dw' or 'python3 $INSTALL_DIR/src/main.py'"
    else
        echo "  Run 'python3 $INSTALL_DIR/src/main.py'"
    fi
    echo
    print_color $YELLOW "Note: For downloading age-restricted videos, place a cookies.txt file in:"
    echo "      $INSTALL_DIR/cookies/"
    echo
    print_color $MAGENTA "Thank you for installing YT4-DW! ♥"
}

# Run main installation
main 