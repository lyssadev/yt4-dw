# YT4 DW - Advanced YouTube Downloader

<div align="center">

![YT4 DW Logo](https://raw.githubusercontent.com/lyssadev/yt4-dw/main/assets/logo.jpg)

A powerful and user-friendly YouTube downloader optimized for Linux and Termux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)

</div>

## ✨ Features

- 🎥 Download YouTube videos in multiple formats:
  - MP4 video (360p, 480p, 720p, 1080p)
  - MP3 audio extraction
- 🎨 Beautiful and intuitive CLI interface
- 🚀 Optimized for both Linux and Termux
- 📊 Real-time download progress tracking
- 🔒 Cookie support for age-restricted content
- 💾 Configurable download path
- ⚡ Fast and efficient downloads using yt-dlp

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- ffmpeg (required for audio extraction and video processing)

### Linux Installation

```bash
# Clone the repository
git clone https://github.com/lyssadev/yt4-dw.git
cd yt4-dw

# Install ffmpeg (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# Install Python dependencies
pip install -r requirements.txt
```

### Termux Installation

```bash
# Install required packages
pkg update
pkg install python ffmpeg git

# Clone the repository
git clone https://github.com/lyssadev/yt4-dw.git
cd yt4-dw

# Install Python dependencies
pip install -r requirements.txt
```

## 🎮 Usage

1. Run the script:
   ```bash
   python src/main.py
   ```

2. Enter the YouTube video URL when prompted

3. Choose your preferred download format:
   - MP3 (Audio Only)
   - MP4 - 360p
   - MP4 - 480p
   - MP4 - 720p
   - MP4 - 1080p

4. Wait for the download to complete!

### Cookie Support

For age-restricted videos or private content:

1. Export your YouTube cookies to a text file (using browser extensions like "Get cookies.txt")
2. Place the cookies file in the project directory
3. Enter the path to the cookies file when prompted

## 📝 Configuration

The script creates a `config.json` file to store your preferences:
- Cookies file location
- Default download path (~/Downloads/yt4-dw)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

Created by:
- [Chifft](https://github.com/chifft)
- [Xzyyy](https://github.com/xzyyy)
- [lyssadev](https://github.com/lyssadev)

Special thanks to the [yt-dlp](https://github.com/yt-dlp/yt-dlp) project.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and content creators' rights.
