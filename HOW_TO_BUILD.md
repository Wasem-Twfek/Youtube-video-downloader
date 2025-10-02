# How to Build Your .exe

## The Simple Truth

**PyInstaller doesn't work with Python 3.10.0** - it's a known bug.

**Solution: Use Nuitka instead**

---

## Build Command (One Line)

```bash
python -m pip install nuitka
python -m nuitka --onefile --windows-disable-console --enable-plugin=tk-inter --output-filename=YouTube_Downloader_Pro.exe youtube_vid_dl.py
```

**Wait 10-15 minutes** (first build only)

Your .exe will be in the same folder: `YouTube_Downloader_Pro.exe`

---

## That's It!

- ✅ Works with Python 3.10.0
- ✅ Creates a single .exe file
- ✅ No console window
- ✅ Users just double-click to run

---

## To Rebuild After Code Changes

Just run the same command again:
```bash
python -m nuitka --onefile --windows-disable-console --enable-plugin=tk-inter --output-filename=YouTube_Downloader_Pro.exe youtube_vid_dl.py
```

Done! 🎉
