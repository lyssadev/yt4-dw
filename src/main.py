#!/usr/bin/env python3

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import yt_dlp
import inquirer
import requests
import ffmpeg
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from art import text2art

# Initialize Rich console
console = Console()

class YouTubeDownloader:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.cookies_dir = os.path.join(self.base_dir, 'cookies')
        self.cookies_path = os.path.join(self.cookies_dir, 'cookies.txt')
        self.version = "2.2.0"  # Updated version number
        
        # Set download path based on environment
        if os.path.exists('/data/data/com.termux'):  # Check if running in Termux
            self.download_path = os.path.join('/storage/emulated/0/Download', 'yt4-dw')
        else:  # Default Linux path
            self.download_path = os.path.expanduser("~/Downloads/yt4-dw")
        
        # Create necessary directories
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        # Initialize config
        self.config = self.load_config()
        self.console = Console()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        default_config = {
            "cookies": self.cookies_path,
            "download_path": self.download_path,
            "last_used_quality": "720p",
            "auto_update_check": True
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = json.load(file)
                    # Update default config with loaded values
                    default_config.update(config)
            
            # Save the config (this will create it if it doesn't exist)
            self.save_config(default_config)
            return default_config
            
        except Exception as e:
            console.print(f"[yellow]! Warning: Could not load config: {str(e)}[/yellow]")
            console.print("[yellow]! Using default configuration[/yellow]")
            return default_config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to config.json"""
        try:
            with open(self.config_path, 'w') as file:
                json.dump(config, file, indent=4)
            console.print("[green]✓ Configuration saved successfully[/green]")
        except Exception as e:
            console.print(f"[yellow]! Warning: Could not save config: {str(e)}[/yellow]")

    def check_internet(self) -> bool:
        """Check internet connectivity"""
        try:
            requests.get("https://www.youtube.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed using multiple detection methods"""
        console.print("\n[yellow]Checking ffmpeg installation...[/yellow]")
        
        # Method 1: Check using ffmpeg-python
        try:
            ffmpeg.probe('dummy')
            console.print("[green]✓ ffmpeg detected via ffmpeg-python[/green]")
            return True
        except (ffmpeg.Error, FileNotFoundError):
            console.print("[yellow]! Could not detect ffmpeg via ffmpeg-python[/yellow]")
        
        # Method 2: Check using system command
        try:
            result = os.system('ffmpeg -version > /dev/null 2>&1')
            if result == 0:
                console.print("[green]✓ ffmpeg detected via system command[/green]")
                return True
            console.print("[yellow]! Could not detect ffmpeg via system command[/yellow]")
        except Exception:
            console.print("[yellow]! Error checking ffmpeg via system command[/yellow]")
        
        # Method 3: Check specific paths
        common_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/data/data/com.termux/files/usr/bin/ffmpeg'  # Termux path
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                console.print(f"[green]✓ ffmpeg found at: {path}[/green]")
                return True
        
        # If we get here, ffmpeg was not found
        console.print("\n[red]✗ ffmpeg installation not detected![/red]")
        console.print("\n[yellow]Debugging information:[/yellow]")
        console.print("1. Current PATH environment:", os.environ.get('PATH', 'Not set'))
        console.print("2. Try running 'which ffmpeg' in your terminal")
        console.print("3. Try running 'ffmpeg -version' in your terminal")
        
        # Show installation instructions
        console.print("\n[yellow]Installation instructions for ffmpeg:[/yellow]")
        
        # Create installation guide panel
        guide = Table.grid(padding=1)
        
        # Linux (Debian/Ubuntu)
        guide.add_row("[bold cyan]For Ubuntu/Debian Linux:[/bold cyan]")
        guide.add_row("[white]sudo apt update[/white]")
        guide.add_row("[white]sudo apt install ffmpeg[/white]")
        guide.add_row("")
        
        # Termux
        guide.add_row("[bold cyan]For Termux:[/bold cyan]")
        guide.add_row("[white]pkg update && pkg upgrade[/white]")
        guide.add_row("[white]pkg install ffmpeg[/white]")
        guide.add_row("[white]termux-setup-storage  # Grant storage permission[/white]")
        guide.add_row("")
        
        # Manual verification
        guide.add_row("[bold cyan]After installation, verify with:[/bold cyan]")
        guide.add_row("[white]1. ffmpeg -version[/white]")
        guide.add_row("[white]2. which ffmpeg[/white]")
        guide.add_row("")
        
        # Troubleshooting
        guide.add_row("[bold cyan]Troubleshooting:[/bold cyan]")
        guide.add_row("1. Try closing and reopening your terminal")
        guide.add_row("2. Check if ffmpeg is in your PATH")
        guide.add_row("3. Try running: hash -r (to clear command cache)")
        
        # Create and display the panel
        install_panel = Panel(
            guide,
            title="[bold red]FFmpeg Installation Guide[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(install_panel)
        
        return False

    def check_for_updates(self) -> None:
        """Check for updates by comparing versions with GitHub repository"""
        if not self.config.get('auto_update_check', True):
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[yellow]Checking for updates...[/yellow]"),
                transient=True,
            ) as progress:
                progress.add_task("", total=None)
                response = requests.get('https://api.github.com/repos/lyssadev/yt4-dw/releases/latest')
                if response.status_code == 200:
                    latest_version = response.json()['tag_name'].replace('v', '')
                    if latest_version > self.version:
                        console.print(f"\n[yellow]! New version {latest_version} available![/yellow]")
                        console.print("[yellow]! Visit: https://github.com/lyssadev/yt4-dw/releases[/yellow]")
                        console.print("[yellow]! Changes in this version:[/yellow]")
                        changes = response.json().get('body', 'No changelog available')
                        console.print(Panel(changes, title="Changelog", border_style="yellow"))
        except Exception as e:
            console.print("[red]! Failed to check for updates[/red]")

    def display_welcome(self) -> None:
        """Display welcome screen with ASCII art and info"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create main title with large ASCII art
        title_art = text2art("YT4-DW", font='block')
        subtitle_art = text2art("YouTube Downloader", font='small')
        
        # Create a styled panel for the title
        title_panel = Panel(
            Text(title_art + "\n" + subtitle_art, style="bold cyan", justify="center"),
            border_style="cyan",
            padding=(1, 4)
        )
        console.print(title_panel)
        
        # Create credits panel
        credits = Table.grid(padding=1)
        credits.add_row("[bold magenta]Created with ♥ by:[/bold magenta]")
        credits.add_row("[yellow]• lyssadev[/yellow] ([cyan]Lead Developer[/cyan])")
        credits.add_row("[yellow]• Chifft[/yellow] ([cyan]Second Developer[/cyan])")
        credits.add_row("[yellow]• Xzyyy[/yellow] ([cyan]Core Contributor[/cyan])")
        
        credits_panel = Panel(
            credits,
            title="[bold]Credits[/bold]",
            border_style="magenta",
            padding=(1, 2)
        )
        
        # Create features panel
        features = Table.grid(padding=1)
        features.add_row("[green]✓[/green] High-quality video downloads (up to 1080p)")
        features.add_row("[green]✓[/green] MP3 audio extraction with best quality")
        features.add_row("[green]✓[/green] Real-time progress tracking")
        features.add_row("[green]✓[/green] Age-restricted content support")
        features.add_row("[green]✓[/green] Optimized for Termux & Linux")
        
        features_panel = Panel(
            features,
            title="[bold]Features[/bold]",
            border_style="green",
            padding=(1, 2)
        )
        
        # Create a grid layout for panels
        grid = Table.grid(padding=1)
        grid.add_row(credits_panel, features_panel)
        console.print(grid)
        
        # Add version and status info
        status = Table.grid(padding=1)
        status.add_row(
            f"[bold blue]Version:[/bold blue] [white]{self.version}[/white]",
            "[bold blue]Status:[/bold blue] [green]Active[/green]",
            "[bold blue]Updates:[/bold blue] [yellow]Auto-check enabled[/yellow]"
        )
        console.print(Panel(status, border_style="blue"))
        console.print()

    def get_video_info(self, url: str, cookies: Optional[str] = None) -> Dict[str, Any]:
        """Get video information including available formats"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'no_playlist': True,  # Prevent playlist downloads
        }
        if cookies:
            ydl_opts['cookiefile'] = cookies

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # Check if it's a playlist
                if info.get('_type') == 'playlist':
                    console.print("[red]✗ Error: Playlists are not supported. Please provide a single video URL.[/red]")
                    return None
                
                # Check if it's a live broadcast
                if info.get('is_live', False):
                    console.print("[red]✗ Error: Live broadcasts cannot be downloaded. Please wait until the stream ends.[/red]")
                    return None
                
                return info
            except Exception as e:
                console.print(f"[red]Error getting video info: {str(e)}[/red]")
                return None

    def download_video(self, url: str, format_id: str, cookies: Optional[str] = None) -> None:
        """Download video in specified format"""
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'cookiefile': cookies if cookies else None,
            'progress_hooks': [self.progress_hook],
            'merge_output_format': 'mp4',  # Force MP4 output
            'no_playlist': True,  # Prevent playlist downloads
            'noplaylist': True,   # Additional playlist prevention
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Force MP4 conversion
            }],
        }

        # For MP3, add specific audio options
        if format_id == "bestaudio/best":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Highest quality MP3
            }]
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['merge_output_format'] = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            self.progress = progress
            self.task = progress.add_task("Downloading...", total=None)
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                console.print("[green]✓ Download completed successfully![/green]")
            except Exception as e:
                console.print(f"[red]Error during download: {str(e)}[/red]")

    def progress_hook(self, d: Dict[str, Any]) -> None:
        """Update download progress"""
        if d['status'] == 'downloading':
            if '_percent_str' in d:
                self.progress.update(
                    self.task,
                    description=f"Downloading... {d['_percent_str']} of {d.get('_total_bytes_str', 'Unknown size')}"
                )
        elif d['status'] == 'finished':
            self.progress.update(self.task, description="Processing download...")

    def extract_audio(self, video_path: str) -> None:
        """Extract audio from video file"""
        output_path = video_path.rsplit('.', 1)[0] + '.mp3'
        try:
            ffmpeg.input(video_path).output(output_path, acodec='libmp3lame', q=0).run(capture_stdout=True, capture_stderr=True)
            os.remove(video_path)
            console.print("[green]✓ Audio extraction completed![/green]")
        except ffmpeg.Error as e:
            console.print(f"[red]Error extracting audio: {str(e)}[/red]")

    def get_format_choice(self) -> str:
        """Get user's preferred format choice before fetching video info"""
        # Predefined quality options
        video_qualities = [
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p",
            "240p",
            "144p"
        ]
        
        audio_qualities = [
            "Audio Only (WAV HIGH)",
            "Audio Only (M4A Med-High)",
            "Audio Only (MP3 320kbps)"
        ]
        
        # Combine all choices
        choices = video_qualities + audio_qualities

        # Ask user for choice
        questions = [
            inquirer.List('format',
                         message='Select maximum quality (will automatically select best available up to this quality):',
                         choices=choices,
                         default=self.config.get('last_used_quality', '720p'))
        ]

        answers = inquirer.prompt(questions)
        chosen_quality = answers['format']

        # Save the choice
        self.config['last_used_quality'] = chosen_quality
        self.save_config(self.config)

        return chosen_quality

    def get_best_format_for_quality(self, formats: list, chosen_quality: str) -> str:
        """Get the best available format that matches the user's quality preference"""
        if 'Audio Only' in chosen_quality:
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if 'WAV' in chosen_quality:
                format_id = 'bestaudio[ext=wav]/bestaudio/best'
            elif 'M4A' in chosen_quality:
                format_id = 'bestaudio[ext=m4a]/bestaudio/best'
            else:  # MP3
                format_id = 'bestaudio[ext=mp3]/bestaudio/best'
            
            return format_id
        else:
            # Extract the height from the quality string (e.g., "1080p" -> 1080)
            target_height = int(chosen_quality.replace('p', ''))
            
            # Get all video formats with both video and audio
            video_formats = [f for f in formats 
                           if f.get('vcodec') != 'none' 
                           and f.get('acodec') != 'none'
                           and f.get('height', 0) <= target_height]
            
            if video_formats:
                # Sort by height and get the best quality that's <= target_height
                video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
                best_format = video_formats[0]
                actual_height = best_format.get('height', 0)
                console.print(f"[yellow]ℹ Best available quality: {actual_height}p[/yellow]")
                return best_format['format_id']
            else:
                # Fallback format string if no exact match found
                return f"bestvideo[height<={target_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={target_height}]/best"

    def get_cookies_path(self) -> Optional[str]:
        """Get the path to cookies file"""
        # First check the cookies directory for any .txt file
        if os.path.exists(self.cookies_dir):
            for file in os.listdir(self.cookies_dir):
                if file.endswith('.txt'):
                    cookie_path = os.path.join(self.cookies_dir, file)
                    # Update config with found cookie path
                    self.config['cookies'] = cookie_path
                    self.save_config(self.config)
                    return cookie_path
        
        # Then try the path from config
        config_cookie_path = self.config.get('cookies')
        if config_cookie_path and os.path.exists(config_cookie_path):
            return config_cookie_path
        
        return None

    def ask_continue(self) -> bool:
        """Ask user if they want to continue downloading"""
        questions = [
            inquirer.List('continue',
                         message='Would you like to download another video?',
                         choices=['Yes', 'No (Exit)'],
                         default='Yes')
        ]

        answers = inquirer.prompt(questions)
        return answers['continue'] == 'Yes'

    def run(self) -> None:
        """Main execution flow"""
        self.display_welcome()
        self.check_for_updates()

        # Check system requirements with styled output
        with console.status("[bold yellow]Checking system requirements...[/bold yellow]"):
            if not self.check_internet():
                console.print("[red]✗ Error: No internet connection detected![/red]")
                sys.exit(1)
            console.print("[green]✓ Internet connection: OK[/green]")

            if not self.check_ffmpeg():
                console.print("[red]✗ Error: ffmpeg not found![/red]")
                console.print("[yellow]Please install ffmpeg to enable all features:[/yellow]")
                console.print("[blue]https://ffmpeg.org/download.html[/blue]")
                sys.exit(1)
            console.print("[green]✓ ffmpeg installation: OK[/green]")
            console.print()

        while True:
            # Get video URL with styled prompt
            url = console.input("[bold cyan]╭─[/bold cyan] Enter YouTube URL\n[bold cyan]╰─>[/bold cyan] ")
            
            # Get format choice before fetching video info
            chosen_quality = self.get_format_choice()
            
            # Handle cookies automatically
            cookies = self.get_cookies_path()
            if cookies:
                console.print(f"[green]✓ Using cookies from: {cookies}[/green]")
            else:
                console.print("[yellow]! No cookies file found. Some videos may be restricted.[/yellow]")
                console.print("[yellow]! Place a cookies.txt file in the 'cookies' folder to enable restricted video access.[/yellow]")

            # Get video information with styled progress
            with console.status("[bold yellow]Fetching video information...[/bold yellow]") as status:
                video_info = self.get_video_info(url, cookies)
                if not video_info:
                    console.print("[red]✗ Failed to get video information. Please check the URL and try again.[/red]")
                    if not cookies:
                        console.print("\n[yellow]Tip: This video might require authentication.[/yellow]")
                        console.print("[yellow]1. Export cookies from your browser using 'Get cookies.txt' extension[/yellow]")
                        console.print("[yellow]2. Place the cookies.txt file in the 'cookies' folder[/yellow]")
                        console.print("[yellow]3. Try downloading again[/yellow]")
                    if not self.ask_continue():
                        break
                    continue
                status.update("[green]✓ Video information retrieved![/green]")

            # Get best format based on chosen quality
            format_id = self.get_best_format_for_quality(video_info.get('formats', []), chosen_quality)
            
            # Set audio only flag
            audio_only = 'Audio Only' in chosen_quality
            
            # Download with styled progress
            console.print("\n[bold cyan]╭─[/bold cyan] Download Progress")
            self.download_video(url, format_id, cookies)
            
            if audio_only:
                console.print("[green]✓ Audio extraction completed automatically![/green]")

            # Show completion message
            console.print("\n[bold green]Download completed successfully![/bold green]")
            console.print(f"[yellow]Files saved in:[/yellow] {self.download_path}")
            
            # Ask if user wants to continue
            if not self.ask_continue():
                break
            
            # Clear screen for next download
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_welcome()

        # Show exit message
        console.print("\n[cyan]Thank you for using YT4-DW! ♥[/cyan]")

def main():
    try:
        downloader = YouTubeDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {str(e)}[/red]")

if __name__ == "__main__":
    main()
