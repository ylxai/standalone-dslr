# 📸 HafiPortrait DSLR Auto-Upload System

**Standalone system untuk auto-upload foto DSLR ke HafiPortrait web project.**

## 🎯 Overview
- **gphoto2** integration untuk Nikon D7100
- **Adobe Lightroom preset** support (.xmp files)
- **Auto watermark** application
- **Real-time upload** ke web project
- **Portable** - bisa dijalankan di laptop/komputer manapun

## 📋 Requirements
- **Linux/Mac/Windows** dengan Python 3.8+
- **Nikon D7100** connected via USB
- **gphoto2** installed
- **Internet connection** untuk upload

## 🚀 Quick Start
```bash
# 1. Setup dependencies
./setup.sh          # Linux/Mac
# atau
setup.bat           # Windows

# 2. Configure
nano config.json    # Edit web project URL

# 3. Run
python run.py
```

## 📁 Structure
```
standalone-dslr/
├── run.py              # Main script
├── config.json        # Configuration
├── presets/           # Adobe Lightroom XMP files
├── watermark.png      # Your watermark file
├── requirements.txt   # Python dependencies
├── setup.sh          # Linux/Mac setup
├── setup.bat         # Windows setup
└── lib/
    ├── camera.py      # gphoto2 integration
    ├── processor.py   # Image processing
    ├── uploader.py    # Upload to web
    └── utils.py       # Helper functions
```

## 🔧 Setup Steps
1. [gphoto2 Installation](#gphoto2-setup) ← **START HERE**
2. [Python Dependencies](#python-setup)
3. [Configuration](#configuration)
4. [Adobe Presets](#presets)
5. [Watermark](#watermark)
6. [Testing](#testing)

---

## 📷 gphoto2 Setup

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install gphoto2 libgphoto2-dev
```

### macOS
```bash
brew install gphoto2
```

### Windows
Download dari: http://www.gphoto.org/download/

### Test gphoto2
```bash
# Connect Nikon D7100 via USB
gphoto2 --auto-detect

# Should show:
# Model                          Port
# Nikon DSC D7100                usb:001,002
```

---

*Next steps akan ditambahkan setelah gphoto2 setup berhasil.*