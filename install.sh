#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}YT4-DW Installer v3.2.0${NC}"
echo "=============================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo -e "\n${YELLOW}Checking Python installation...${NC}"
if command_exists python3; then
    python_version=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $python_version${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8 or higher${NC}"
    exit 1
fi

# Check pip
echo -e "\n${YELLOW}Checking pip installation...${NC}"
if command_exists pip3; then
    pip_version=$(pip3 --version)
    echo -e "${GREEN}✓ pip found: $pip_version${NC}"
else
    echo -e "${RED}✗ pip not found. Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Check FFmpeg
echo -e "\n${YELLOW}Checking FFmpeg installation...${NC}"
if command_exists ffmpeg; then
    ffmpeg_version=$(ffmpeg -version | head -n1)
    echo -e "${GREEN}✓ FFmpeg found: $ffmpeg_version${NC}"
else
    echo -e "${RED}✗ FFmpeg not found${NC}"
    echo -e "${YELLOW}Installing FFmpeg...${NC}"
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y ffmpeg
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y ffmpeg
    elif [ -f /etc/arch-release ]; then
        sudo pacman -S ffmpeg
    elif command_exists brew; then
        brew install ffmpeg
    else
        echo -e "${RED}✗ Could not install FFmpeg automatically. Please install it manually.${NC}"
        exit 1
    fi
fi

# Create virtual environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p downloads
mkdir -p cookies
mkdir -p logs

# Copy config if it doesn't exist
if [ ! -f config.json ]; then
    echo -e "\n${YELLOW}Creating default configuration...${NC}"
    cp config.json.example config.json
fi

# Set permissions
echo -e "\n${YELLOW}Setting permissions...${NC}"
chmod +x src/main.py

echo -e "\n${GREEN}Installation completed successfully!${NC}"
echo -e "You can now run YT4-DW with: ${YELLOW}./src/main.py${NC}"
echo -e "Or activate the virtual environment first with: ${YELLOW}source venv/bin/activate${NC}" 