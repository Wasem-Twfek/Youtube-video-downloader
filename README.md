# YouTube & YouTube Music Downloader Pro

A powerful desktop application for downloading content from both YouTube and YouTube Music with a modern interface and advanced features.

## Features

### Core Features
- **Modern & Clean UI**: A responsive and intuitive interface built with Tkinter's themed widgets.
- **Dual Platform Support**: Download from both YouTube and YouTube Music seamlessly.
- **Auto-Detection**: Automatically detects whether the URL is from YouTube or YouTube Music.
- **Smart Content Recognition**: Identifies single videos/songs vs playlists automatically.

### Download Options
- **Video Downloads (MP4)**: Choose from multiple quality options (144p to 4K).
- **Audio Downloads**: Multiple format options:
  - **MP3**: Universal compatibility
  - **M4A**: High quality, smaller file size
  - **Opus**: Modern codec with excellent quality
  - **Best**: Keep original audio format
- **Playlist Support**: Download entire playlists from both YouTube and YouTube Music.

### YouTube Music Features
- **Metadata Preservation**: Automatically extracts and embeds artist, title, and other metadata.
- **Music-Optimized**: Detects YouTube Music links and suggests audio format for best results.
- **Playlist Downloads**: Download full albums or playlists with proper organization.

### Additional Features
- **Progress Tracking**: Real-time progress bar and status updates during downloads.
- **Non-Blocking UI**: The application remains responsive during downloads (multi-threaded).
- **Error Handling**: Clear, user-friendly error messages for invalid URLs or network issues.
- **Custom Download Location**: Browse and select where you want to save your files.
- **Smart File Management**: Automatically handles invalid filename characters and duplicate files.

## Prerequisites

- Python 3.6+
- **Note**: This app uses `yt-dlp` (a more reliable alternative to pytube) for downloading videos

## How to Install and Run

1.  **Clone or download the repository** to your local machine.

2.  **Navigate to the project directory**:
    ```bash
    cd "path\to\Youtube video downloader"
    ```

3.  **Install the required packages** using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    python youtube_vid_dl.py
    ```

## How to Use

### Basic Usage

1.  **Paste the URL**: Copy and paste a YouTube or YouTube Music URL into the input field.
    - The app will automatically detect the type (YouTube/YouTube Music, Video/Song/Playlist)
    
2.  **Select Content Type** (optional):
    - **Auto Detect**: Let the app automatically determine if it's a single item or playlist
    - **Single Video/Song**: Force download as a single item
    - **Playlist**: Force download as a playlist
    
3.  **Choose Download Format**:
    - **Video (MP4)**: Download as video file
    - **Audio Only**: Download audio in your chosen format
    
4.  **Select Quality/Format**:
    - For videos: Choose resolution (144p to 4K or Highest)
    - For audio: Choose format (MP3, M4A, Opus, or Best)
    
5.  **Select Download Location**: Default is your `Downloads` folder. Click `Browse` to change.

6.  **Click `Start Download`** and watch the progress bar!

### YouTube Music Tips

- For YouTube Music links, **Audio Only** format is recommended for best results
- Metadata (artist, title, album) is automatically embedded in audio files
- Playlists are organized in their own folders

### Examples

**YouTube Video**:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**YouTube Music Song**:
```
https://music.youtube.com/watch?v=dQw4w9WgXcQ
```

**YouTube Playlist**:
```
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxx
```

**YouTube Music Playlist**:
```
https://music.youtube.com/playlist?list=PLxxxxxxxxxxxxxxx
```

## Notes

- **FFmpeg Required for Audio Conversion**: To convert audio to MP3/M4A/Opus, you need FFmpeg installed on your system. Without it, use the "best" option to keep the original format.
- **Playlists**: Downloaded into a subfolder named after the playlist title.
- **YouTube Music**: Works best with audio-only downloads; video downloads may have limited quality options.