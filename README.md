# YT4 DW

## Description
YT4 DW is a Python script designed to download YouTube videos with audio in MP4 format. The script is compatible with Termux and Linux environments.

## Features
- Download videos from YouTube with audio.
- Choose from available quality options.
- Animated text outputs for a better user experience.
- Colorful terminal output for enhanced visibility.

## Requirements
To run this script, you need to install the following dependencies:

- `yt-dlp`: A youtube-dl fork with additional features and fixes.
- `colorama`: A library for colored terminal text.
- `requests`: A simple, yet elegant HTTP library.
- `art`: A library for ASCII art.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/lyssadev/yt4-dw.git
   cd yt4-dw
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

   Alternatively, you can install the packages manually:
   ```sh
   pip install yt-dlp colorama requests art
   ```

## Usage
To use the script, run the following command in your terminal:
```sh
python src/main.py
```

Follow the on-screen instructions to download your desired YouTube video.

### Handling Authentication
If you encounter an error requiring you to sign in to confirm you're not a bot, you will need to pass cookies for authentication. Follow these steps:

1. **Extract cookies from your browser:**
   - For Chrome on Linux:
     ```sh
     yt-dlp --cookies-from-browser chrome
     ```
   - For Chrome installed via Flatpak:
     ```sh
     yt-dlp --cookies-from-browser chrome:~/.var/app/com.google.Chrome/
     ```

2. **Save cookies to a file:**
   ```sh
   yt-dlp --cookies-from-browser chrome --cookies cookies.txt
   ```

3. **Use the saved cookies file:**
   ```sh
   yt-dlp --cookies cookies.txt <video_url>
   ```

4. **Configure `config.json`:**
   - Create a `config.json` file in the same directory as `main.py`.
   - Add the path to your cookies file:
     ```json
     {
       "cookies": "/path/to/cookies.txt"
     }
     ```

5. **Run the script:**
   ```sh
   python src/main.py
   ```

   The script will automatically use the cookies file specified in `config.json`.

For more details, refer to the [yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp).

## Authors
Coded By Chifft, Xzyyy & lyssadev

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
