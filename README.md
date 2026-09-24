# YouTube & YouTube Music Downloader

A Python desktop application that provides a graphical workflow for downloading publicly accessible YouTube and YouTube Music media through yt-dlp.

## Features

- YouTube and YouTube Music URL handling
- Video and audio-only download modes
- Quality and format selection
- Single-item and playlist workflows
- Progress reporting
- Non-blocking downloads using background execution
- Custom download locations
- Basic metadata handling for audio
- Input and download error handling

## Technology

- Python
- Tkinter
- yt-dlp
- FFmpeg

## Getting started

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Run the desktop application:

~~~bash
python youtube_vid_dl.py
~~~

FFmpeg is required for operations that need media conversion or stream merging.

## Project structure

~~~text
.
├── youtube_vid_dl.py
├── requirements.txt
├── HOW_TO_BUILD.md
├── build.spec
└── README.md
~~~

## Scope and responsible use

This is a desktop utility project. Users are responsible for complying with the terms of service, copyright rules, and access restrictions applicable to the content they download.
