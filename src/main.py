import os
import sys
import time
import json
import requests
import yt_dlp
from colorama import Fore, Style, init
from art import text2art

init(autoreset=True)

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def check_ffmpeg():
    if os.system("ffmpeg -version") != 0:
        print(Fore.YELLOW + "Please install ffmpeg to proceed.")
        sys.exit(1)

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def display_welcome():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + text2art("YT4 DW"))
    print(Fore.MAGENTA + "Y T 4  D W")
    print(Fore.YELLOW + "Coded By Chifft, Xzyyy & lyssadev")
    print(Fore.WHITE + "This script allows you to download YouTube videos with audio in mp4 format.")
    print()

def detect_audio():
    print(Fore.WHITE + "Detecting Audio", end='', flush=True)
    for _ in range(3):
        print(".", end='', flush=True)
        time.sleep(0.5)
    print(Fore.GREEN + "\nAudio Detected! ✅")
    print()

def download_video(video_url, cookies=None):
    print(Fore.WHITE + "Downloading Best Quality video...", end='', flush=True)
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }, {
            'key': 'FFmpegEmbedSubtitle'
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }
    if cookies:
        ydl_opts['cookiefile'] = cookies
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(Fore.GREEN + "\nVideo Downloaded Successfully ✅")
    except yt_dlp.utils.DownloadError as e:
        if 'ffmpeg' in str(e).lower():
            print(Fore.YELLOW + "Please install ffmpeg to proceed.")
        elif 'Sign in to confirm you’re not a bot' in str(e):
            print(Fore.RED + f"\nError: {str(e)}")
            print(Fore.YELLOW + "Please follow the instructions to pass cookies for authentication.")
            print(Fore.YELLOW + "See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp for more details.")
            cookies = input(Fore.WHITE + "Enter the path to your cookies file: ").strip()
            if cookies:
                download_video(video_url, cookies)
        else:
            print(Fore.RED + f"\nError: {str(e)}")
            print(Fore.YELLOW + "Please follow the instructions to pass cookies for authentication.")
            print(Fore.YELLOW + "See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp for more details.")
        sys.exit(1)
    print()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    if not check_internet():
        print(Fore.RED + "A fatal error has occurred, please try again later or check your internet ❌")
        sys.exit(1)

    check_ffmpeg()

    config = load_config()
    display_welcome()
    video_url = input(Fore.WHITE + "Enter the YouTube video URL: ")
    cookies = config.get('cookies')
    if cookies:
        print(Fore.WHITE + f"Using cookies file from config: {cookies}")
        if not os.path.exists(cookies):
            print(Fore.RED + f"Cookies file not found: {cookies}")
            sys.exit(1)
        time.sleep(4)
    else:
        cookies = input(Fore.WHITE + "Enter the path to your cookies file (or press Enter to skip): ").strip()
        if cookies:
            config['cookies'] = cookies
            save_config(config)
    print()
    detect_audio()
    download_video(video_url, cookies if cookies else None)

if __name__ == "__main__":
    main()