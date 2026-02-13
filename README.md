# 🎮 **VideoGame Overlay** ⭐

**Make ANY video unique** for YouTube, TikTok & Instagram by adding **live gameplay** to the bottom screen!

<div align="center">
  <img src="resource/Original.png" width="60%">
</div>

## ✨ **Features**
- 🎯 **Automatically** overlays gameplay on the bottom of your videos
- 🕹️ **Games**: Fortnite, Subway Surfers, Minecraft + custom videos
- 📱 **Platforms**: YouTube Shorts, TikTok, Instagram Reels
- ⚡ **FFmpeg-powered** — fast & high quality
- 🤖 **Optional subtitles** (OpenAI integration)

## 🚀 **Quick Setup (30 seconds)**

```bash
git clone https://github.com/jjjohny228/video-uniqualizer-public.git
cd video-uniqualizer-public

# Linux/macOS
chmod +x *.sh && ./setup.sh

# Windows  
setup.bat
```

## 📁 **How to Use**

1. **Download game videos** → put in `bottom_videos/`
2. **Configure `.env`** (OpenAI key for subtitles)
3. Put source videos into [source_videos](source_videos)
3. **Run** → get unique videos!

```
macOS/Linux:  macos_start.command (double-click)
Windows:      windows_start.bat (double-click)
CLI:          uv run python main.py
```

## 🎯 **Why Use It?**
```
❌ Regular video → YouTube: "Reused content" strike
✅ With gameplay → ✅ Unique + High retention
```

## 🔧 **Development**

```bash
# Linting
uv run ruff check .
uv run ruff check . --fix

# Run dev server
uv run python main.py
```

## 🤝 **Support the Project**
⭐ **Star this repo** — helps a lot!  
🐛 **Issues** — bugs/features  
💬 **Discord** — questions

---
#Python #YouTube #TikTok #VideoEditing #GameplayOverlay
