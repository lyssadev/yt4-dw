#!/usr/bin/env python3

import os
import sys
import json
import time
import shutil
import platform
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime

# Core functionality
import yt_dlp
import requests
import ffmpeg

# Enhanced CLI and UI
import typer
import click
import questionary
from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn,
    BarColumn, TaskProgressColumn, TimeRemainingColumn,
    DownloadColumn, TransferSpeedColumn
)
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.style import Style
from rich.theme import Theme
from rich.traceback import install as install_rich_traceback
from rich.prompt import Prompt, Confirm
from rich.status import Status

# Visual enhancements
from art import text2art
from colorama import init as colorama_init
from termcolor import colored
from pyfiglet import Figlet
from yaspin import yaspin
from halo import Halo
from alive_progress import alive_bar, config_handler
from blessed import Terminal
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Print
from asciimatics.renderers import FigletText, Rainbow

# Initialize enhancements
colorama_init(strip=False)
install_rich_traceback()
term = Terminal()

# Custom theme for Rich
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "command": "bold blue",
    "path": "bold magenta",
    "url": "underline blue",
    "version": "bold cyan",
    "header": "bold yellow",
})

# Initialize Rich console with custom theme
console = Console(theme=CUSTOM_THEME)

class YouTubeDownloader:
    def __init__(self):
        """Initialize YouTube Downloader with enhanced configuration"""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.cookies_dir = os.path.join(self.base_dir, 'cookies')
        self.cookies_path = os.path.join(self.cookies_dir, 'cookies.txt')
        self.version = "3.0.0"  # Major version update
        
        # Repository information
        self.repo_owner = "lyssadev"
        self.repo_name = "yt4-dw"
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.raw_content_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main"
        
        # System detection and setup
        self.system = platform.system().lower()
        self.is_termux = os.path.exists('/data/data/com.termux')
        
        # Set download path based on environment
        if self.is_termux:
            self.download_path = os.path.join('/storage/emulated/0/Download', 'yt4-dw')
        else:
            self.download_path = os.path.expanduser("~/Downloads/yt4-dw")
        
        # Create necessary directories
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        # Initialize configuration
        self.config = self.load_config()
        
        # Setup terminal
        self.term = term
        self.screen_width = self.term.width or 80
        self.screen_height = self.term.height or 24
        
        # Initialize progress tracking
        self.current_task = None
        self.download_start_time = None
        self.total_size = 0
        self.downloaded_size = 0
        
        # Setup download statistics
        self.stats = {
            'total_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0,
            'session_start': time.time()
        }
        
        # Initialize visual elements
        self.spinner = yaspin(color="cyan")
        self.halo = Halo(spinner='dots')

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with enhanced settings and validation"""
        default_config = {
            "cookies": self.cookies_path,
            "download_path": self.download_path,
            "last_used_quality": "1080p (Full HD)",
            "auto_update_check": True,
            "update_check_interval": 24,  # Hours between update checks
            "last_update_check": 0,  # Timestamp of last check
            "preferred_audio_format": "m4a",
            "download_settings": {
                "max_retries": 3,
                "timeout": 30,
                "chunk_size": 8192,
                "max_concurrent_downloads": 1,
                "use_aria2": False,
                "rate_limit": 0,  # 0 = unlimited
                "force_ipv4": False
            },
            "format_settings": {
                "prefer_quality": "1080p",
                "fallback_quality": "720p",
                "video_codec": "h264",
                "audio_codec": "aac",
                "container": "mp4",
                "force_60fps": False
            },
            "ui_settings": {
                "show_thumbnails": True,
                "show_progress_bar": True,
                "show_eta": True,
                "show_speed": True,
                "show_size": True,
                "color_scheme": "default",
                "progress_bar_style": "smooth",
                "use_animations": True
            },
            "update_settings": {
                "auto_notify": True,
                "check_beta_releases": False,
                "show_commit_history": True,
                "max_commits_shown": 5,
                "auto_backup": True
            },
            "notification_settings": {
                "notify_on_complete": True,
                "notify_on_error": True,
                "play_sounds": True,
                "desktop_notifications": True
            },
            "advanced_settings": {
                "debug_mode": False,
                "log_level": "INFO",
                "proxy": None,
                "custom_headers": {},
                "user_agent": None,
                "cookies_enabled": True
            }
        }
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            if os.path.exists(self.config_path):
                # Backup existing config before loading
                if self._should_backup_config():
                    self._backup_config()
                
                # Load and validate existing config
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    
                # Recursively update default config with loaded values
                self._update_config_recursive(default_config, config)
                
                # Validate the merged config
                validated_config = self._validate_config(default_config)
                
                # Save the validated config
                self.save_config(validated_config)
                return validated_config
            
            # If no config exists, save and return default
            self.save_config(default_config)
            return default_config
            
        except Exception as e:
            console.print(f"[error]! Warning: Could not load config: {str(e)}[/error]")
            console.print("[warning]! Using default configuration[/warning]")
            return default_config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration with backup and validation"""
        try:
            # Validate config before saving
            validated_config = self._validate_config(config)
            
            # Create backup if needed
            if self._should_backup_config():
                self._backup_config()
            
            # Save with pretty formatting
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(validated_config, file, indent=4, ensure_ascii=False)
            
            console.print("[success]✓ Configuration saved successfully[/success]")
        except Exception as e:
            console.print(f"[error]! Error saving config: {str(e)}[/error]")
            
    def _update_config_recursive(self, default: Dict, update: Dict) -> None:
        """Recursively update configuration while preserving structure"""
        for key, value in update.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._update_config_recursive(default[key], value)
                else:
                    default[key] = value

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration values"""
        validated = config.copy()
        
        # Validate paths
        validated['download_path'] = os.path.expanduser(config['download_path'])
        validated['cookies'] = os.path.expanduser(config['cookies'])
        
        # Validate quality settings
        valid_qualities = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p']
        if not any(q in config['last_used_quality'] for q in valid_qualities):
            validated['last_used_quality'] = '1080p (Full HD)'
        
        # Validate numeric values
        validated['update_check_interval'] = max(1, min(168, config['update_check_interval']))
        validated['download_settings']['max_retries'] = max(1, min(10, config['download_settings']['max_retries']))
        validated['download_settings']['timeout'] = max(5, min(300, config['download_settings']['timeout']))
        
        return validated

    def _should_backup_config(self) -> bool:
        """Determine if config backup is needed"""
        if not os.path.exists(self.config_path):
            return False
            
        # Check last backup time
        backup_path = f"{self.config_path}.backup"
        if not os.path.exists(backup_path):
            return True
            
        # Backup if file has changed in last 24 hours
        config_mtime = os.path.getmtime(self.config_path)
        backup_mtime = os.path.getmtime(backup_path)
        return (time.time() - config_mtime) < 86400 and config_mtime > backup_mtime

    def _backup_config(self) -> None:
        """Create a backup of the current config file"""
        if not os.path.exists(self.config_path):
            return
            
        backup_path = f"{self.config_path}.backup"
        try:
            shutil.copy2(self.config_path, backup_path)
            console.print("[info]ℹ Config backup created[/info]")
        except Exception as e:
            console.print(f"[warning]! Warning: Could not create config backup: {str(e)}[/warning]")

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
        """Enhanced update checker that checks core files directly"""
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
                
                # Files to check for updates
                core_files = [
                    'src/main.py',
                    'requirements.txt',
                    'README.md',
                    'config.json'
                ]
                
                headers = {
                    'Accept': 'application/vnd.github.v3.raw',
                    'User-Agent': f'yt4-dw/{self.version}'
                }
                
                # Check each core file
                updates_available = []
                for file in core_files:
                    try:
                        # Get remote file
                        remote_url = f"{self.raw_content_url}/{file}"
                        response = requests.get(remote_url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            remote_content = response.text
                            
                            # Special handling for main.py to extract version
                            if file == 'src/main.py':
                                remote_version = self._extract_version_from_content(remote_content)
                                if remote_version and self._compare_versions(remote_version, self.version) > 0:
                                    updates_available.append({
                                        'file': file,
                                        'type': 'version',
                                        'current': self.version,
                                        'new': remote_version
                                    })
                            
                            # Check if local file exists and compare content
                            local_path = os.path.join(self.base_dir, file)
                            if os.path.exists(local_path):
                                with open(local_path, 'r', encoding='utf-8') as f:
                                    local_content = f.read()
                                    if local_content.strip() != remote_content.strip():
                                        updates_available.append({
                                            'file': file,
                                            'type': 'content'
                                        })
                            else:
                                updates_available.append({
                                    'file': file,
                                    'type': 'missing'
                                })
                    except Exception as file_error:
                        console.print(f"[yellow]! Warning: Could not check {file}: {str(file_error)}[/yellow]")
                
                if updates_available:
                    # Create update notification panel
                    update_info = Table.grid(padding=1)
                    
                    # Show version update if available
                    version_update = next((u for u in updates_available if u['type'] == 'version'), None)
                    if version_update:
                        update_info.add_row(
                            f"[bold yellow]New version {version_update['new']} available![/bold yellow]"
                        )
                        update_info.add_row(
                            f"[white]Current version: {version_update['current']}[/white]"
                        )
                        update_info.add_row("")
                    
                    # Show file changes
                    update_info.add_row("[bold cyan]Updates available:[/bold cyan]")
                    for update in updates_available:
                        if update['type'] == 'content':
                            update_info.add_row(f"[white]• Modified: {update['file']}[/white]")
                        elif update['type'] == 'missing':
                            update_info.add_row(f"[white]• Missing: {update['file']}[/white]")
                    
                    # Add update instructions
                    update_info.add_row("")
                    update_info.add_row("[bold cyan]To update:[/bold cyan]")
                    update_info.add_row("[white]1. Backup your current config.json[/white]")
                    update_info.add_row("[white]2. Download the latest version:[/white]")
                    update_info.add_row(f"[white]   {self.repo_url}/archive/refs/heads/main.zip[/white]")
                    update_info.add_row("[white]3. Extract and replace your current files[/white]")
                    update_info.add_row("[white]4. Restore your backed up config.json[/white]")
                    update_info.add_row("[white]5. Run: pip install -r requirements.txt[/white]")
                    
                    # Display the update panel
                    console.print(Panel(
                        update_info,
                        title="[bold yellow]Updates Available[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 2)
                    ))
                else:
                    console.print("[green]✓ Your installation is up to date![/green]")
                
                # Update last check timestamp
                self.config['last_update_check'] = current_time
                self.save_config(self.config)
                
        except Exception as e:
            console.print(f"[red]! Failed to check for updates: {str(e)}[/red]")
            console.print("[yellow]You can manually check for updates at:[/yellow]")
            console.print(f"[blue]{self.repo_url}[/blue]")
    
    def _extract_version_from_content(self, content: str) -> Optional[str]:
        """Extract version number from main.py content"""
        try:
            for line in content.split('\n'):
                if 'self.version = ' in line:
                    # Extract everything between quotes
                    version_match = line.split('=')[1].strip()
                    # Remove any quotes and comments
                    version = version_match.strip('"').strip("'").split('#')[0].strip()
                    # Validate version format
                    if self._is_valid_version(version):
                        return version
            return None
        except Exception as e:
            console.print(f"[yellow]! Warning: Version extraction failed: {str(e)}[/yellow]")
            return None

    def _is_valid_version(self, version: str) -> bool:
        """Check if a string is a valid version number (e.g., '2.3.0')"""
        try:
            # Check if version matches X.Y.Z format
            parts = version.split('.')
            if len(parts) != 3:
                return False
            # Verify each part is a number
            for part in parts:
                if not part.isdigit():
                    return False
            return True
        except Exception:
            return False

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings and return:
           1  if version1 > version2
           0  if version1 == version2
           -1 if version1 < version2
        """
        try:
            if not self._is_valid_version(version1) or not self._is_valid_version(version2):
                raise ValueError("Invalid version format")

            def normalize(v):
                return [int(x) for x in v.split('.')]

            v1 = normalize(version1)
            v2 = normalize(version2)

            for a, b in zip(v1, v2):
                if a > b:
                    return 1
                elif a < b:
                    return -1
            return 0
        except Exception as e:
            console.print(f"[yellow]! Warning: Version comparison failed: {str(e)}[/yellow]")
            return 0  # Return equal if comparison fails

    def display_welcome(self) -> None:
        """Display enhanced welcome screen with animations and rich formatting"""
        # Clear screen with fade effect
        self._clear_screen_with_effect()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="title", size=10),
            Layout(name="info", size=15),
            Layout(name="status", size=3)
        )
        
        # Create title with figlet
        title = text2art("YT4-DW", font="block")
        version = text2art(f"v{self.version}", font="small")
        
        # Create main title panel
        title_text = Text()
        title_text.append(title, style="bold cyan")
        title_text.append(version, style="bold yellow")
        title_text.append("\nProfessional YouTube Downloader", style="italic yellow")
        
        title_panel = Panel(
            title_text,
            title="[bold]Welcome[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        # Create features panel with animation
        features = Table.grid(padding=1)
        features.add_row("[bold magenta]Enhanced Features:[/bold magenta]")
        
        feature_list = [
            "🎥 4K Video Support",
            "🎵 Studio Quality Audio",
            "🚀 Optimized Performance",
            "🎨 Beautiful Interface",
            "🔒 Enhanced Security",
            "⚡ Smart Downloads"
        ]
        
        for feature in feature_list:
            features.add_row(f"[green]✓[/green] {feature}")
        
        features_panel = Panel(
            features,
            title="[bold]Features[/bold]",
            border_style="green",
            padding=(1, 2)
        )
        
        # Create stats panel
        stats = Table.grid(padding=1)
        stats.add_row(
            f"[bold blue]Version:[/bold blue] [white]{self.version}[/white]",
            "[bold blue]Status:[/bold blue] [green]Active[/green]",
            f"[bold blue]Python:[/bold blue] [white]{sys.version.split()[0]}[/white]"
        )
        
        session_time = time.time() - self.stats['session_start']
        stats.add_row(
            f"[bold blue]Downloads:[/bold blue] [white]{self.stats['total_downloads']}[/white]",
            f"[bold blue]Total Size:[/bold blue] [white]{self._format_size(self.stats['total_size'])}[/white]",
            f"[bold blue]Session:[/bold blue] [white]{self._format_time(session_time)}[/white]"
        )
        
        stats_panel = Panel(
            stats,
            title="[bold]Statistics[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
        
        # Create system info panel
        sys_info = Table.grid(padding=1)
        sys_info.add_row("[bold magenta]System Information:[/bold magenta]")
        sys_info.add_row(f"[white]OS: {platform.system()} {platform.release()}[/white]")
        sys_info.add_row(f"[white]Terminal: {os.environ.get('TERM', 'Unknown')}[/white]")
        sys_info.add_row(f"[white]Resolution: {self.screen_width}x{self.screen_height}[/white]")
        
        sys_panel = Panel(
            sys_info,
            title="[bold]System[/bold]",
            border_style="magenta",
            padding=(1, 2)
        )
        
        # Layout panels
        layout["title"].update(title_panel)
        
        info_layout = Layout()
        info_layout.split_row(
            Layout(features_panel),
            Layout(sys_panel)
        )
        layout["info"].update(info_layout)
        layout["status"].update(stats_panel)
        
        # Render final layout
        console.print(layout)
        
        # Show update status if available
        if self.config['auto_update_check']:
            with console.status("[bold yellow]Checking for updates...[/bold yellow]"):
                self.check_for_updates()
    
    def _clear_screen_with_effect(self) -> None:
        """Clear screen with fade effect"""
        def fade_out(char: str = "░") -> None:
            for i in range(self.screen_height):
                sys.stdout.write(char * self.screen_width + "\n")
                sys.stdout.flush()
                time.sleep(0.01)
        
        fade_out()
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _format_size(self, size: int) -> str:
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.0f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

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

        # Ask user for choice using questionary instead of inquirer
        chosen_quality = questionary.select(
            'Select maximum quality (will automatically select best available up to this quality):',
            choices=choices,
            default=self.config.get('last_used_quality', '720p (HD)')
        ).ask()
        
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
        return questionary.select(
            'Would you like to download another video?',
            choices=['Yes', 'No (Exit)'],
            default='Yes'
        ).ask() == 'Yes'

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
