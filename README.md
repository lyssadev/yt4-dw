# YT4 DW - Professional YouTube Downloader

<div align="center">

![YT4 DW Logo](https://raw.githubusercontent.com/lyssadev/yt4-dw/main/assets/logo.png)

A powerful and professional-grade YouTube downloader optimized for Linux and Termux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/lyssadev/yt4-dw/releases)

</div>

## 🌟 Professional Features

### 🎥 Video Processing
- **Advanced Quality Selection**
  - Up to 4K/2160p resolution support
  - Smart quality adaptation
  - Codec optimization (H.264/AVC, VP9)
  - Frame rate preservation (60fps support)
  - HDR content handling
  
### 🎵 Audio Engineering
- **Studio-Grade Audio**
  - Lossless WAV extraction
  - High-quality AAC encoding (256kbps)
  - Professional MP3 export (320kbps)
  - Multi-track audio support
  - Audio normalization

### 🎨 Enhanced Interface
- **Professional UI/UX**
  - Animated ASCII art
  - Rich color schemes
  - Progress visualization
  - System information display
  - Real-time statistics
  - Dynamic layouts

### 🚀 Performance
- **Optimized Engine**
  - Multi-threaded downloads
  - Smart chunk handling
  - Bandwidth optimization
  - Resource management
  - Cache utilization
  - Background processing

### 🛡️ Security Features
- **Enhanced Protection**
  - Secure cookie handling
  - Config file encryption
  - Automatic backups
  - Update verification
  - Safe mode operation

### ⚙️ Advanced Configuration
- **Professional Settings**
  - Custom download paths
  - Format preferences
  - Network optimization
  - Proxy support
  - Debug options
  - Logging system

## 🔧 System Requirements

### Minimum Requirements
- Python 3.7+
- 2GB RAM
- 1GB free disk space
- Internet connection

### Recommended
- Python 3.9+
- 4GB RAM
- SSD storage
- Broadband connection

## 📦 Installation

### One-Command Installation
```bash
curl -sSL https://raw.githubusercontent.com/lyssadev/yt4-dw/main/install.sh | bash
```

### Manual Installation

#### Linux
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip ffmpeg git

# Clone repository
git clone https://github.com/lyssadev/yt4-dw.git
cd yt4-dw

# Install Python packages
pip3 install -r requirements.txt
```

#### Termux
```bash
# Update system
pkg update && pkg upgrade

# Install dependencies
pkg install python ffmpeg git

# Setup storage
termux-setup-storage

# Clone and install
git clone https://github.com/lyssadev/yt4-dw.git
cd yt4-dw
pip install -r requirements.txt
```

## 🎮 Professional Usage

### Basic Operation
```bash
python3 src/main.py
```

### Command Line Options
```bash
python3 src/main.py [OPTIONS]

Options:
  --quality QUALITY    Set preferred quality
  --format FORMAT     Set output format
  --path PATH        Set download path
  --debug           Enable debug mode
  --config FILE     Use custom config
  --no-color       Disable colors
```

### Quality Presets
- **Video Qualities**
  - 2160p (4K Ultra HD)
  - 1440p (2K Quad HD)
  - 1080p (Full HD)
  - 720p (HD)
  - 480p (SD)
  - 360p (Low)
  - 240p (Mobile)
  - 144p (Minimal)

- **Audio Qualities**
  - WAV (Studio Lossless)
  - M4A (AAC 256kbps)
  - MP3 (320kbps)

## ⚙️ Advanced Configuration

### Configuration File
```json
{
    "download_settings": {
        "max_retries": 3,
        "timeout": 30,
        "chunk_size": 8192,
        "max_concurrent_downloads": 1,
        "use_aria2": false,
        "rate_limit": 0
    },
    "format_settings": {
        "prefer_quality": "1080p",
        "video_codec": "h264",
        "audio_codec": "aac",
        "container": "mp4"
    },
    "ui_settings": {
        "show_thumbnails": true,
        "color_scheme": "professional",
        "progress_bar_style": "smooth"
    }
}
```

### Environment Variables
```bash
YT4DW_CONFIG=/path/to/config.json
YT4DW_DOWNLOADS=/path/to/downloads
YT4DW_COOKIES=/path/to/cookies.txt
YT4DW_DEBUG=1
```

## 🔄 Update System

### Automatic Updates
- Version checking
- Changelog display
- File verification
- Backup creation
- Safe installation

### Manual Update
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 📊 Statistics

- Download history
- Speed analysis
- Quality metrics
- Error tracking
- Usage patterns

## 🤝 Professional Support

### Community
- GitHub Issues
- Feature Requests
- Bug Reports
- Documentation

### Development
- Pull Requests
- Code Reviews
- Testing
- Documentation

## 📄 License & Credits

### License
MIT License - see [LICENSE](LICENSE)

### Created by
- **Lead Developer**: [lyssadev](https://github.com/lyssadev)
- **Core Developer**: [Chifft](https://github.com/chifft)
- **Systems Engineer**: [Xzyyy](https://github.com/xzyyysh)

### Special Thanks
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) team
- Open source community
- All contributors

## ⚠️ Professional Guidelines

Please respect:
- YouTube's Terms of Service
- Content creators' rights
- Copyright laws
- Network policies
- Privacy regulations
