# YT4 DW - Advanced YouTube Downloader

<div align="center">

![YT4 DW Logo](https://raw.githubusercontent.com/lyssadev/yt4-dw/main/assets/logo.png)

A powerful and user-friendly YouTube downloader optimized for Linux and Termux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)

</div>

## ✨ Features

- 🎥 Smart video downloads:
  - Automatic quality selection (up to your chosen maximum)
  - Supports resolutions from 144p to 1440p
  - Shows best available quality before download
  - MP4 format for best compatibility
- 🎵 Multiple audio formats:
  - WAV (HIGH Quality)
  - M4A (Med-High Quality)
  - MP3 (320kbps)
- 🎨 Beautiful and intuitive CLI interface
- 🚀 Optimized for both Linux and Termux
- 📊 Real-time download progress tracking
- 🔒 Cookie support for age-restricted content
- 💾 Configurable download path
- 🔄 Automatic updates with changelog
- ⚡ Fast and efficient downloads using yt-dlp

## ⚠️ Limitations

- ▶️ Single video downloads only (no playlist support)
- 🔴 Live broadcasts cannot be downloaded
- 📱 Some videos may require cookies for access

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

2. Enter a single YouTube video URL when prompted
   - ✅ Regular videos: `https://www.youtube.com/watch?v=...`
   - ❌ No playlists or live broadcasts

3. Choose your maximum preferred quality:
   - Video Quality Options (will automatically select best available):
     - 1440p (if available)
     - 1080p
     - 720p
     - 480p
     - 360p
     - 240p
     - 144p
   - Audio Only Options:
     - WAV (HIGH Quality)
     - M4A (Med-High Quality)
     - MP3 (320kbps)

4. The system will:
   - Show the best available quality for your selection
   - Automatically start the download
   - Display real-time progress
   - Save the file in your configured download location

### Cookie Support

For age-restricted or private videos:

1. Install the "Get cookies.txt" browser extension
2. Visit YouTube and log in to your account
3. Export your cookies to a text file
4. Place the cookies.txt file in the `cookies` folder
5. The app will automatically detect and use your cookies

## 📝 Configuration

The script creates a `config.json` file to store your preferences:
- Download paths (automatically set based on your system)
- Last used quality preference
- Preferred audio format
- Cookie file location
- Auto-update settings

### Download Locations

- **Linux**: `~/Downloads/yt4-dw`
- **Termux**: `/storage/emulated/0/Download/yt4-dw`
  - Run `termux-setup-storage` first to grant storage access
  - Files will be accessible in your device's Download folder

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

Created by:
- [lyssadev](https://github.com/lyssadev) (Lead Developer)
- [Chifft](https://github.com/chifft) (Second Developer)
- [Xzyyy](https://github.com/xzyyysh) (Core Contributor)

Special thanks to the [yt-dlp](https://github.com/yt-dlp/yt-dlp) project.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and content creators' rights.
