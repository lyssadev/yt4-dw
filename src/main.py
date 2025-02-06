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
        self.version = "2.3.0"  # Updated version number
        self.repo_url = "https://github.com/lyssadev/yt4-dw.git"
        self.api_url = "https://api.github.com/repos/lyssadev/yt4-dw"
        
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
            "auto_update_check": True,
            "update_check_interval": 24,  # Hours between update checks
            "last_update_check": 0  # Timestamp of last check
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
        """Enhanced update checker with detailed version comparison and notifications"""
        if not self.config.get('auto_update_check', True):
            return
            
        # Check if we should check for updates based on interval
        current_time = time.time()
        last_check = self.config.get('last_update_check', 0)
        check_interval = self.config.get('update_check_interval', 24) * 3600  # Convert hours to seconds
        
        if current_time - last_check < check_interval:
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[yellow]Checking for updates...[/yellow]"),
                transient=True,
            ) as progress:
                progress.add_task("", total=None)
                
                # Get update settings
                update_settings = self.config.get('update_settings', {})
                show_commits = update_settings.get('show_commit_history', True)
                max_commits = update_settings.get('max_commits_shown', 5)
                check_beta = update_settings.get('check_beta_releases', False)
                
                # Get latest release info
                if check_beta:
                    response = requests.get(f"{self.api_url}/releases")
                    if response.status_code == 200:
                        releases = response.json()
                        release_info = next((r for r in releases if not r['prerelease']), releases[0])
                else:
                    response = requests.get(f"{self.api_url}/releases/latest")
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch release info: {response.status_code}")
                    release_info = response.json()
                
                latest_version = release_info['tag_name'].replace('v', '')
                
                # Compare versions
                if self._compare_versions(latest_version, self.version) > 0:
                    # Create update notification panel
                    update_info = Table.grid(padding=1)
                    
                    # Show version info with release type
                    release_type = " (Beta)" if release_info.get('prerelease', False) else ""
                    update_info.add_row(
                        f"[bold yellow]New version {latest_version}{release_type} available![/bold yellow]"
                    )
                    update_info.add_row(
                        f"[white]Current version: {self.version}[/white]"
                    )
                    update_info.add_row("")
                    
                    # Add changelog
                    changes = release_info.get('body', 'No changelog available')
                    if changes:
                        update_info.add_row("[bold cyan]Changelog:[/bold cyan]")
                        for line in changes.split('\n'):
                            if line.strip():
                                update_info.add_row(f"[white]• {line.strip()}[/white]")
                    
                    # Add recent commits if enabled
                    if show_commits:
                        commits_response = requests.get(
                            f"{self.api_url}/commits",
                            params={'since': release_info['published_at']}
                        )
                        
                        if commits_response.status_code == 200:
                            commits = commits_response.json()
                            if commits:
                                update_info.add_row("")
                                update_info.add_row("[bold cyan]Recent changes:[/bold cyan]")
                                for commit in commits[:max_commits]:
                                    msg = commit['commit']['message'].split('\n')[0]
                                    update_info.add_row(f"[white]• {msg}[/white]")
                    
                    # Add update instructions
                    update_info.add_row("")
                    update_info.add_row("[bold cyan]To update:[/bold cyan]")
                    update_info.add_row("[white]1. Visit: https://github.com/lyssadev/yt4-dw/releases[/white]")
                    update_info.add_row("[white]2. Download the latest release[/white]")
                    update_info.add_row("[white]3. Follow the update instructions in the release notes[/white]")
                    
                    # Add auto-update reminder if disabled
                    if not self.config.get('auto_update_check', True):
                        update_info.add_row("")
                        update_info.add_row("[yellow]Note: Auto-updates are currently disabled[/yellow]")
                        update_info.add_row("[yellow]Enable them in config.json to receive automatic notifications[/yellow]")
                    
                    # Display the update panel
                    console.print(Panel(
                        update_info,
                        title="[bold yellow]Update Available[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 2)
                    ))
                
                # Update last check timestamp
                self.config['last_update_check'] = current_time
                self.save_config(self.config)
                
        except Exception as e:
            console.print(f"[red]! Failed to check for updates: {str(e)}[/red]")
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings and return:
           1  if version1 > version2
           0  if version1 == version2
           -1 if version1 < version2
        """
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        v1 = normalize(version1)
        v2 = normalize(version2)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        return 0

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
        # Predefined quality options with descriptions
        video_qualities = [
            "1440p (2K QHD)",
            "1080p (Full HD)",
            "720p (HD)",
            "480p (SD)",
            "360p (SD)",
            "240p (Low)",
            "144p (Very Low)"
        ]
        
        audio_qualities = [
            "Audio Only (WAV HIGH - Lossless)",
            "Audio Only (M4A Med-High - AAC 256kbps)",
            "Audio Only (MP3 320kbps - High Quality)"
        ]
        
        # Combine all choices
        choices = video_qualities + audio_qualities

        # Ask user for choice
        questions = [
            inquirer.List('format',
                         message='Select maximum quality (will automatically select best available up to this quality):',
                         choices=choices,
                         default=self.config.get('last_used_quality', '720p (HD)'))
        ]

        answers = inquirer.prompt(questions)
        chosen_quality = answers['format']
        
        # Clean up the quality string for internal use
        if '(' in chosen_quality:
            chosen_quality = chosen_quality.split(' (')[0]  # Extract just the quality value

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
                console.print("[yellow]ℹ Selecting best WAV audio quality[/yellow]")
            elif 'M4A' in chosen_quality:
                format_id = 'bestaudio[ext=m4a]/bestaudio/best'
                console.print("[yellow]ℹ Selecting best M4A audio quality[/yellow]")
            else:  # MP3
                format_id = 'bestaudio[ext=mp3]/bestaudio/best'
                console.print("[yellow]ℹ Selecting best MP3 audio quality (320kbps)[/yellow]")
            
            return format_id
        else:
            # Extract the height from the quality string (e.g., "1080p" -> 1080)
            target_height = int(chosen_quality.replace('p', ''))
            
            # First try to find formats with both video and audio
            video_formats = [f for f in formats 
                           if f.get('vcodec') != 'none' 
                           and f.get('acodec') != 'none'
                           and f.get('height', 0) <= target_height]
            
            if video_formats:
                # Sort by height, then by bitrate, then by filesize
                video_formats.sort(key=lambda x: (
                    x.get('height', 0),
                    x.get('tbr', 0),  # Total bitrate
                    x.get('filesize', 0)
                ), reverse=True)
                
                best_format = video_formats[0]
                actual_height = best_format.get('height', 0)
                actual_fps = best_format.get('fps', 0)
                actual_vcodec = best_format.get('vcodec', 'unknown')
                actual_acodec = best_format.get('acodec', 'unknown')
                
                # Show detailed format information
                console.print(f"[yellow]ℹ Best available quality details:[/yellow]")
                console.print(f"[yellow]  • Resolution: {actual_height}p[/yellow]")
                console.print(f"[yellow]  • FPS: {actual_fps}[/yellow]")
                console.print(f"[yellow]  • Video codec: {actual_vcodec}[/yellow]")
                console.print(f"[yellow]  • Audio codec: {actual_acodec}[/yellow]")
                
                return best_format['format_id']
            else:
                # If no combined format found, try separate video+audio approach
                console.print("[yellow]ℹ No combined format found, selecting best video and audio separately[/yellow]")
                
                # Get best video format below or equal to target height
                video_formats = [f for f in formats 
                               if f.get('vcodec') != 'none' 
                               and f.get('height', 0) <= target_height]
                
                if video_formats:
                    video_formats.sort(key=lambda x: (
                        x.get('height', 0),
                        x.get('tbr', 0),
                        x.get('filesize', 0)
                    ), reverse=True)
                    
                    best_video = video_formats[0]
                    actual_height = best_video.get('height', 0)
                    console.print(f"[yellow]ℹ Selected video quality: {actual_height}p[/yellow]")
                
                # Return format string for best video + best audio
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
