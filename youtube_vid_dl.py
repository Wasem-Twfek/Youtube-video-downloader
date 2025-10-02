import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from threading import Thread
from datetime import datetime
import re
import yt_dlp
import json

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube & YouTube Music Downloader Pro")
        self.root.geometry('900x750')
        self.root.minsize(600, 400)  # Set minimum window size
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # Config file path
        self.config_file = os.path.join(os.path.expanduser("~"), ".youtube_downloader_config.json")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), background='#f0f0f0')
        self.style.configure('TFrame', background='#f0f0f0')
        
        # Variables
        self.url = tk.StringVar()
        self.download_path = tk.StringVar()
        self.download_type = tk.StringVar()
        self.video_quality = tk.StringVar()
        self.audio_format = tk.StringVar()
        self.content_type = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to download")
        self.downloading = False
        self.current_progress = 0
        self.is_youtube_music = False
        
        # Load saved preferences
        self.load_preferences()
        
        # Stop/Resume functionality
        self.stop_download_flag = False
        self.download_thread = None
        self.current_download_url = None
        self.current_download_path = None
        self.current_quality = None
        self.can_resume = False
        self.partial_files = []
        self.ydl_instance = None  # Store yt-dlp instance for quick termination
        
        self.setup_ui()
        
        # Save preferences when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.root, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = ttk.Frame(canvas, padding="20")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the content horizontally
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - frame_width) // 2)
            canvas.coords(canvas_window, x_position, 0)
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Recenter when canvas is resized
        canvas.bind("<Configure>", lambda e: on_frame_configure(None))
        
        # Use scrollable_frame as main_frame
        main_frame = scrollable_frame
        
        # Header
        header = ttk.Label(
            main_frame, 
            text="YouTube & YouTube Music Downloader Pro", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # URL Entry
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="Paste YouTube or YouTube Music URL:").pack(anchor='w')
        url_entry = ttk.Entry(url_frame, textvariable=self.url, width=60)
        url_entry.pack(fill=tk.X, pady=5)
        url_entry.bind('<KeyRelease>', self.detect_url_type)
        
        # URL Type Indicator
        self.url_type_label = ttk.Label(url_frame, text="", foreground="#0066cc")
        self.url_type_label.pack(anchor='w', pady=2)
        
        # Content Type Selection
        content_frame = ttk.LabelFrame(main_frame, text="Content Type", padding=10)
        content_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(
            content_frame, 
            text="Auto Detect", 
            variable=self.content_type, 
            value="auto",
            command=self.update_quality_options
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            content_frame, 
            text="Single Video/Song", 
            variable=self.content_type, 
            value="single",
            command=self.update_quality_options
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            content_frame, 
            text="Playlist", 
            variable=self.content_type, 
            value="playlist",
            command=self.update_quality_options
        ).pack(side=tk.LEFT, padx=10)
        
        # Download Type
        type_frame = ttk.LabelFrame(main_frame, text="Download Format", padding=10)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(
            type_frame, 
            text="Video (MP4)", 
            variable=self.download_type, 
            value="video",
            command=self.update_quality_options
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            type_frame, 
            text="Audio Only", 
            variable=self.download_type, 
            value="audio",
            command=self.update_quality_options
        ).pack(side=tk.LEFT, padx=10)
        
        # Quality Selection
        self.quality_frame = ttk.LabelFrame(main_frame, text="Quality Options", padding=10)
        self.quality_frame.pack(fill=tk.X, pady=10)
        
        self.video_quality_combo = ttk.Combobox(
            self.quality_frame, 
            textvariable=self.video_quality,
            values=["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "Highest"],
            state="readonly",
            width=15
        )
        self.video_quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Audio format selection
        ttk.Label(self.quality_frame, text="Audio Format:").pack(side=tk.LEFT, padx=5)
        self.audio_format_combo = ttk.Combobox(
            self.quality_frame, 
            textvariable=self.audio_format,
            values=["mp3", "m4a", "opus", "best"],
            state="readonly",
            width=10
        )
        self.audio_format_combo.pack(side=tk.LEFT, padx=5)
        
        # Download Path
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="Download Location:").pack(anchor='w')
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(path_entry_frame, textvariable=self.download_path).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(
            path_entry_frame, 
            text="Browse", 
            command=self.browse_directory
        ).pack(side=tk.RIGHT)
        
        # Progress
        self.progress_frame = ttk.LabelFrame(main_frame, text="Download Progress", padding=10)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(
            self.progress_frame, 
            textvariable=self.status_text,
            wraplength=700
        )
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Download Buttons - Make them prominent
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Create a sub-frame to hold buttons side by side
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack()
        
        self.download_btn = ttk.Button(
            buttons_container, 
            text="▶ Start Download", 
            command=self.start_download
        )
        self.download_btn.pack(side=tk.LEFT, padx=5, pady=10, ipadx=20, ipady=10)
        
        self.stop_btn = ttk.Button(
            buttons_container, 
            text="⏹ Stop Download", 
            command=self.stop_download,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=10, ipadx=20, ipady=10)
        
        self.resume_btn = ttk.Button(
            buttons_container, 
            text="⏯ Resume Download", 
            command=self.resume_download,
            state=tk.DISABLED
        )
        self.resume_btn.pack(side=tk.LEFT, padx=5, pady=10, ipadx=20, ipady=10)
        
        # Set initial state
        self.update_quality_options()
        
        # Trace changes to save preferences automatically
        self.download_type.trace('w', lambda *args: self.save_preferences())
        self.video_quality.trace('w', lambda *args: self.save_preferences())
        self.audio_format.trace('w', lambda *args: self.save_preferences())
        self.content_type.trace('w', lambda *args: self.save_preferences())
        self.download_path.trace('w', lambda *args: self.save_preferences())
    
    def detect_url_type(self, event=None):
        url = self.url.get().strip()
        if not url:
            self.url_type_label.config(text="")
            self.is_youtube_music = False
            return
        
        if "music.youtube.com" in url:
            self.is_youtube_music = True
            if "playlist" in url:
                self.url_type_label.config(text="✓ YouTube Music Playlist detected")
            else:
                self.url_type_label.config(text="✓ YouTube Music Song detected")
        elif "youtube.com" in url or "youtu.be" in url:
            self.is_youtube_music = False
            if "playlist" in url:
                self.url_type_label.config(text="✓ YouTube Playlist detected")
            else:
                self.url_type_label.config(text="✓ YouTube Video detected")
        else:
            self.url_type_label.config(text="⚠ Unknown URL type")
            self.is_youtube_music = False
    
    def update_quality_options(self):
        # Clear all widgets first
        for widget in self.quality_frame.winfo_children():
            widget.pack_forget()
        
        if self.download_type.get() == "video":
            ttk.Label(self.quality_frame, text="Video Quality:").pack(side=tk.LEFT, padx=5)
            self.video_quality_combo.pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(self.quality_frame, text="Audio Format:").pack(side=tk.LEFT, padx=5)
            self.audio_format_combo.pack(side=tk.LEFT, padx=5)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path.set(directory)
            self.save_preferences()
    
    def load_preferences(self):
        """Load user preferences from config file"""
        default_prefs = {
            'download_path': os.path.expanduser("~/Downloads"),
            'download_type': 'video',
            'video_quality': '720p',
            'audio_format': 'mp3',
            'content_type': 'auto'
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    prefs = json.load(f)
                    # Validate and set preferences
                    self.download_path.set(prefs.get('download_path', default_prefs['download_path']))
                    self.download_type.set(prefs.get('download_type', default_prefs['download_type']))
                    self.video_quality.set(prefs.get('video_quality', default_prefs['video_quality']))
                    self.audio_format.set(prefs.get('audio_format', default_prefs['audio_format']))
                    self.content_type.set(prefs.get('content_type', default_prefs['content_type']))
            else:
                # Set defaults
                self.download_path.set(default_prefs['download_path'])
                self.download_type.set(default_prefs['download_type'])
                self.video_quality.set(default_prefs['video_quality'])
                self.audio_format.set(default_prefs['audio_format'])
                self.content_type.set(default_prefs['content_type'])
        except Exception as e:
            print(f"Error loading preferences: {e}")
            # Set defaults on error
            self.download_path.set(default_prefs['download_path'])
            self.download_type.set(default_prefs['download_type'])
            self.video_quality.set(default_prefs['video_quality'])
            self.audio_format.set(default_prefs['audio_format'])
            self.content_type.set(default_prefs['content_type'])
    
    def save_preferences(self):
        """Save user preferences to config file"""
        try:
            prefs = {
                'download_path': self.download_path.get(),
                'download_type': self.download_type.get(),
                'video_quality': self.video_quality.get(),
                'audio_format': self.audio_format.get(),
                'content_type': self.content_type.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(prefs, f, indent=4)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def on_closing(self):
        """Handle window close event"""
        self.save_preferences()
        self.root.destroy()
    
    def on_progress(self, d):
        # Check if download should be stopped - check frequently for fast response
        if self.stop_download_flag:
            # Force immediate stop
            raise KeyboardInterrupt("Download stopped by user")
            
        if d['status'] == 'downloading':
            if 'total_bytes' in d or 'total_bytes_estimate' in d:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.progress_bar['value'] = percentage
                    self.status_text.set(f"Downloading: {int(percentage)}%")
                    self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.status_text.set("Processing download...")
            self.root.update_idletasks()
    
    def download_video(self, url, path, quality):
        try:
            # Detect if it's YouTube Music
            is_music = "music.youtube.com" in url
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.on_progress],
                'quiet': True,
                'no_warnings': True,
                'continuedl': True,  # Enable resume capability
                'noprogress': False,
                'socket_timeout': 10,  # Faster timeout for responsiveness
            }
            
            # Add metadata extraction for music
            if is_music or self.download_type.get() == "audio":
                ydl_opts['writethumbnail'] = False
                ydl_opts['embedthumbnail'] = False
                ydl_opts['add_metadata'] = True
            
            if self.download_type.get() == "video":
                # Video download options (not recommended for YouTube Music)
                if is_music:
                    self.root.after(0, self.status_text.set, "Note: YouTube Music links work best with Audio format")
                
                if quality == "Highest":
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    # Extract resolution number (e.g., "720p" -> "720")
                    res = quality.replace('p', '')
                    ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'
            else:
                # Audio-only download
                audio_format = self.audio_format.get()
                ydl_opts['format'] = 'bestaudio/best'
                
                if audio_format != "best":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '192',
                    }]
                    
                    # Add metadata postprocessor
                    if is_music:
                        ydl_opts['postprocessors'].append({
                            'key': 'FFmpegMetadata',
                            'add_metadata': True,
                        })
            
            # Download the content
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_instance = ydl  # Store for quick stop
                info = ydl.extract_info(url, download=True)
                self.ydl_instance = None  # Clear after download
                filename = ydl.prepare_filename(info)
                
                # For audio, the extension changes based on format
                if self.download_type.get() == "audio" and self.audio_format.get() != "best":
                    filename = os.path.splitext(filename)[0] + f'.{self.audio_format.get()}'
                
                # Get metadata for display
                title = info.get('title', 'Unknown')
                artist = info.get('artist') or info.get('uploader', 'Unknown')
                
                if is_music:
                    return True, f"Successfully downloaded: {title}\nArtist: {artist}"
                else:
                    return True, f"Successfully downloaded: {os.path.basename(filename)}"
            
        except KeyboardInterrupt:
            self.ydl_instance = None
            return False, "Download stopped by user"
        except Exception as e:
            self.ydl_instance = None
            error_msg = str(e)
            if "stopped by user" in error_msg.lower() or "keyboard" in error_msg.lower():
                return False, "Download stopped by user"
            if "music.youtube.com" in url and "not available" in error_msg.lower():
                return False, f"YouTube Music Error: This content may be region-locked or unavailable.\n\nDetails: {error_msg}"
            return False, f"Error downloading: {error_msg}"
    
    def start_download(self):
        if self.downloading:
            return
            
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube or YouTube Music URL")
            return
            
        if not any(x in url for x in ["youtube.com", "youtu.be", "music.youtube.com"]):
            messagebox.showerror("Error", "Please enter a valid YouTube or YouTube Music URL")
            return
        
        # Detect URL type automatically if auto mode is selected
        if self.content_type.get() == "auto":
            self.detect_url_type()
            
        download_path = self.download_path.get()
        if not os.path.isdir(download_path):
            try:
                os.makedirs(download_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create directory: {str(e)}")
                return
        
        # Store download info for resume
        self.current_download_url = url
        self.current_download_path = download_path
        self.current_quality = self.video_quality.get() if self.download_type.get() == "video" else self.audio_format.get()
        
        # Reset flags and instances
        self.stop_download_flag = False
        self.downloading = True
        self.can_resume = False
        self.ydl_instance = None
        
        # Update UI immediately
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.resume_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.status_text.set("▶ Starting download...")
        self.root.update_idletasks()  # Force UI update
        
        # Start download in a separate thread immediately
        self.download_thread = Thread(
            target=self.process_download,
            args=(url, download_path),
            daemon=True
        )
        self.download_thread.start()
    
    def stop_download(self):
        """Stop the current download immediately"""
        if not self.downloading:
            return
        
        self.stop_download_flag = True
        self.status_text.set("Stopping download...")
        self.stop_btn.config(state=tk.DISABLED)
        
        # Force immediate stop if yt-dlp instance exists
        if self.ydl_instance:
            try:
                # This will cause yt-dlp to stop immediately
                self.ydl_instance._download_retcode = 1
            except:
                pass
        
        # Check stop status quickly
        self.root.after(500, self.check_download_stopped)
    
    def check_download_stopped(self):
        """Check if download has stopped and update UI"""
        if not self.downloading:
            self.status_text.set("⏸ Download stopped")
            self.can_resume = True
            self.download_btn.config(state=tk.NORMAL)
            self.resume_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        else:
            # Still downloading, check again quickly
            self.root.after(200, self.check_download_stopped)
    
    def resume_download(self):
        """Resume a stopped download"""
        if not self.can_resume or not self.current_download_url:
            messagebox.showwarning("Cannot Resume", "No download to resume")
            return
        
        # Reset flags and instances
        self.stop_download_flag = False
        self.downloading = True
        self.can_resume = False
        self.ydl_instance = None
        
        # Update UI immediately
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.resume_btn.config(state=tk.DISABLED)
        self.status_text.set("⏯ Resuming download...")
        self.root.update_idletasks()  # Force UI update
        
        # Start download in a separate thread immediately
        self.download_thread = Thread(
            target=self.process_download,
            args=(self.current_download_url, self.current_download_path),
            daemon=True
        )
        self.download_thread.start()
    
    def process_download(self, url, download_path):
        try:
            quality = self.current_quality or (self.video_quality.get() if self.download_type.get() == "video" else self.audio_format.get())
            
            # Check if it's a playlist
            is_playlist = "playlist" in url or self.content_type.get() == "playlist"
            
            if is_playlist:
                self.download_playlist(url, download_path, quality)
            else:
                success, message = self.download_video(url, download_path, quality)
                
                if self.stop_download_flag:
                    self.root.after(0, self.show_download_result, False, "Download stopped by user")
                else:
                    self.root.after(0, self.show_download_result, success, message)
                
        except KeyboardInterrupt:
            self.root.after(0, self.show_download_result, False, "Download stopped by user")
        except Exception as e:
            if "stopped by user" in str(e).lower() or "keyboard" in str(e).lower():
                self.root.after(0, self.show_download_result, False, "Download stopped by user")
            else:
                self.root.after(0, self.show_download_result, False, f"An error occurred: {str(e)}")
        finally:
            self.downloading = False
            self.ydl_instance = None  # Always clear instance
            if not self.stop_download_flag:
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.resume_btn.config(state=tk.DISABLED))
    
    def download_playlist(self, playlist_url, download_path, quality):
        try:
            is_music = "music.youtube.com" in playlist_url
            
            # Configure yt-dlp for playlist
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(playlist)s', '%(title)s.%(ext)s'),
                'progress_hooks': [self.on_progress],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,  # Continue on errors
                'continuedl': True,  # Enable resume capability
                'socket_timeout': 10,  # Faster timeout
            }
            
            if is_music:
                ydl_opts['add_metadata'] = True
            
            if self.download_type.get() == "video":
                if quality == "Highest":
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    res = quality.replace('p', '')
                    ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'
            else:
                audio_format = self.audio_format.get()
                ydl_opts['format'] = 'bestaudio/best'
                
                if audio_format != "best":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '192',
                    }]
                    
                    if is_music:
                        ydl_opts['postprocessors'].append({
                            'key': 'FFmpegMetadata',
                            'add_metadata': True,
                        })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_instance = ydl  # Store for quick stop
                
                info = ydl.extract_info(playlist_url, download=False)
                total_items = len(info.get('entries', []))
                
                if total_items == 0:
                    self.ydl_instance = None
                    self.root.after(0, self.show_download_result, False, "No items found in the playlist")
                    return
                
                content_name = "songs" if is_music else "videos"
                playlist_name = info.get('title', 'playlist')
                playlist_folder = os.path.join(download_path, playlist_name)
                
                self.root.after(0, self.status_text.set, f"Downloading playlist with {total_items} {content_name}...")
                
                # Download the playlist
                ydl.download([playlist_url])
                self.ydl_instance = None  # Clear after download
                
                # Check if download was stopped (YouTube Music specific handling)
                if is_music and self.stop_download_flag:
                    # Clean up partial files for YouTube Music
                    self.cleanup_partial_files(playlist_folder)
                    raise Exception("Playlist download stopped by user")
                
                # Verify completion for YouTube Music
                if is_music:
                    completed_files = self.count_completed_files(playlist_folder)
                    if completed_files < total_items and self.stop_download_flag:
                        self.cleanup_partial_files(playlist_folder)
                        raise Exception("Playlist download stopped by user")
                    
                    # Report actual completion
                    self.root.after(0, self.show_download_result, True, 
                                  f"Successfully downloaded: {playlist_name}\n{completed_files} of {total_items} {content_name} completed")
                else:
                    # For regular YouTube, use original behavior
                    self.root.after(0, self.show_download_result, True, 
                                  f"Successfully downloaded: {playlist_name}\n{total_items} {content_name} processed")
            
        except KeyboardInterrupt:
            self.ydl_instance = None
            if is_music:
                self.cleanup_partial_files(playlist_folder)
            self.root.after(0, self.show_download_result, False, "Playlist download stopped by user")
        except Exception as e:
            self.ydl_instance = None
            if "stopped by user" in str(e).lower() or "keyboard" in str(e).lower():
                if is_music:
                    self.cleanup_partial_files(playlist_folder)
                self.root.after(0, self.show_download_result, False, "Playlist download stopped by user")
            else:
                self.root.after(0, self.show_download_result, False, f"Error processing playlist: {str(e)}")
    
    def cleanup_partial_files(self, folder_path):
        """Clean up .part files in the specified folder (YouTube Music specific)"""
        if not os.path.exists(folder_path):
            return
        
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith('.part') or filename.endswith('.ytdl'):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up partial file: {filename}")
                    except Exception as e:
                        print(f"Could not remove {filename}: {e}")
        except Exception as e:
            print(f"Error cleaning up partial files: {e}")
    
    def count_completed_files(self, folder_path):
        """Count completed (non-partial) files in folder"""
        if not os.path.exists(folder_path):
            return 0
        
        try:
            completed = 0
            for filename in os.listdir(folder_path):
                # Count files that are not partial downloads
                if not filename.endswith('.part') and not filename.endswith('.ytdl'):
                    # Check for actual media files
                    if any(filename.endswith(ext) for ext in ['.mp3', '.m4a', '.opus', '.mp4', '.webm', '.mkv']):
                        completed += 1
            return completed
        except Exception as e:
            print(f"Error counting files: {e}")
            return 0
    
    def show_download_result(self, success, message):
        if success:
            messagebox.showinfo("Success", message)
            self.status_text.set("✓ Download completed successfully")
            self.progress_bar['value'] = 100
            self.can_resume = False
            self.download_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.DISABLED)
        else:
            if "stopped by user" in message.lower():
                # Don't show error dialog for user-initiated stops
                self.status_text.set("⏸ Download stopped - Click Resume to continue")
                self.can_resume = True
                self.download_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.resume_btn.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", message)
                self.status_text.set("✗ Download failed")
                self.progress_bar['value'] = 0
                self.download_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.resume_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    
    # Set window icon if available
    try:
        root.iconbitmap('youtube_icon.ico')  # Optional: Add an icon file
    except:
        pass
    
    # Center the window
    window_width = 800
    window_height = 650
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()