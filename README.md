# YT4-DW v3.2.0

A professional YouTube downloader with enhanced features and a beautiful CLI interface.

## Features

- 🎥 High Quality Video Downloads (up to 8K)
- 🎵 Studio Quality Audio (WAV, M4A, MP3)
- 🚀 Fast Downloads with Concurrent Processing
- 🎨 Beautiful Terminal Interface
- 📊 Detailed Progress Information
- 🔒 Cookie Support for Private Videos
- 🎯 Smart Format Selection
- 💾 Automatic Metadata Embedding
- 🖼️ Thumbnail Embedding
- 🔄 Auto-Update Checking

## Requirements

- Python 3.8 or higher
- FFmpeg
- Internet connection

## Installation

### Quick Install (Linux/macOS)

```bash
# Clone the repository
git clone https://github.com/lyssadev/yt4-dw.git
cd yt4-dw

# Run installer
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg:
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Fedora: `sudo dnf install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

3. Make the script executable:
```bash
chmod +x src/main.py
```

## Usage

1. Basic usage:
```bash
./src/main.py
```

2. Follow the interactive prompts:
   - Enter YouTube URL
   - Select quality
   - Wait for download to complete

## Quality Options

### Video
- 1440p (2K QHD)
- 1080p (Full HD)
- 720p (HD)
- 480p (SD)
- 360p (SD)
- 240p (Low)
- 144p (Very Low)

### Audio
- WAV (Lossless)
- M4A (AAC 256kbps)
- MP3 (320kbps)

## Configuration

The `config.json` file contains various settings:

```json
{
    "download_path": "downloads",
    "last_used_quality": "1080p (Full HD)",
    "auto_update_check": true,
    "preferred_audio_format": "m4a",
    ...
}
```

## Private Videos

To download private or age-restricted videos:

1. Install a browser extension like "Get cookies.txt"
2. Export cookies from YouTube
3. Place the cookies.txt file in the `cookies` directory

## Updates

The script automatically checks for updates. You can also manually update:

```bash
git pull origin main
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in your PATH
   - Try reinstalling FFmpeg

2. **Download fails**
   - Check your internet connection
   - Verify the video URL
   - Try using cookies for restricted content

3. **Quality not available**
   - The script will automatically select the best available quality
   - Some videos may not have all quality options

### Debug Mode

Enable debug mode in config.json:
```json
{
    "advanced_settings": {
        "debug_mode": true
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the core downloading functionality
- [FFmpeg](https://ffmpeg.org/) for media processing
- All contributors and users of YT4-DW

## Support

If you find this tool useful, please consider:
- Star the repository
- Report bugs
- Share with others
- Contribute to the code

## Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and content creators' rights.
