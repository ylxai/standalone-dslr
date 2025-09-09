# 🚀 Quick Start Guide - gphoto2 Setup

**Step-by-step setup dan testing untuk gphoto2 integration.**

## 📋 Prerequisites

- **Nikon D7100** dengan USB cable
- **Python 3.8+** installed
- **Internet connection** untuk download dependencies

---

## 🔧 Step 1: Setup Dependencies

### Linux/Mac:
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### Windows:
```cmd
# Run setup
setup.bat
```

**Setup script akan:**
- ✅ Install gphoto2
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Create necessary directories
- ✅ Set permissions (Linux)

---

## 📷 Step 2: Connect Camera

1. **Connect Nikon D7100** via USB ke laptop/komputer
2. **Turn ON** camera
3. **Set camera mode** ke **PTP** atau **MTP** (bukan Mass Storage)
   - Menu → Setup → USB → PTP
4. **Allow computer access** jika ada prompt di camera

---

## 🔍 Step 3: Test gphoto2

```bash
# Activate virtual environment
source venv/bin/activate          # Linux/Mac
# atau
venv\Scripts\activate.bat         # Windows

# Test gphoto2 installation
python test_gphoto2.py
```

**Expected output:**
```
🎯 HafiPortrait DSLR gphoto2 Test
================================

🔍 Testing gphoto2 Installation
===============================================
✅ gphoto2 command line: INSTALLED
✅ gphoto2 Python binding: AVAILABLE

🔍 Testing Camera Detection
===============================================
✅ Found 1 camera(s):
   1. Nikon DSC D7100
🎯 Nikon D7100 DETECTED: Nikon DSC D7100

🔍 Testing Nikon D7100 Connection
===============================================
✅ Nikon D7100 connection: SUCCESS
✅ Camera info retrieved:
   Model: Nikon DSC D7100
   Battery: 75%

📊 Results: 4/4 tests passed
🎉 All tests passed! Ready untuk next step.
```

---

## 🛠️ Step 4: Configure

### Edit config.json:
```json
{
    "camera": {
        "watch_directory": "/path/to/your/camera/folder",
        "model": "Nikon D7100"
    },
    "web_project": {
        "base_url": "http://your-vps-ip:3002"
    }
}
```

**Important:** Set `watch_directory` ke folder dimana camera menyimpan foto.

---

## 🔧 Troubleshooting

### ❌ "No cameras detected"
```bash
# Manual test
gphoto2 --auto-detect

# Should show:
# Model                          Port
# Nikon DSC D7100                usb:001,002
```

**Solutions:**
- Check USB cable connection
- Try different USB port
- Restart camera
- Check camera USB mode (PTP/MTP)

### ❌ "gphoto2 command line: NOT FOUND"

**Linux:**
```bash
sudo apt update
sudo apt install gphoto2 libgphoto2-dev
```

**macOS:**
```bash
brew install gphoto2
```

**Windows:**
- Download dari: http://www.gphoto.org/download/
- Extract dan add ke PATH

### ❌ "Permission denied" (Linux)
```bash
# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Logout dan login kembali
```

### ❌ "gphoto2 Python binding: NOT AVAILABLE"
```bash
# Activate venv first
source venv/bin/activate

# Install gphoto2 Python binding
pip install gphoto2
```

---

## ✅ Success Indicators

**Jika semua berhasil, Anda akan melihat:**
- ✅ gphoto2 command line working
- ✅ Python binding available
- ✅ Nikon D7100 detected dan connected
- ✅ Camera info retrieved (battery, settings, etc.)

---

## 📋 Next Steps

**Setelah gphoto2 setup berhasil:**

1. **Adobe Presets** - Add Lightroom .xmp files
2. **Watermark** - Add watermark.png file  
3. **Processing** - Setup image processing pipeline
4. **Upload Integration** - Connect ke web project
5. **Testing** - End-to-end workflow test

---

## 🆘 Need Help?

**Common issues:**
- Camera not detected → Check USB mode (PTP)
- Permission errors → Check user groups (Linux)
- Python errors → Check virtual environment
- Connection timeout → Try different USB port

**Test commands:**
```bash
# Test camera detection
gphoto2 --auto-detect

# Test camera info
gphoto2 --summary

# Test file list
gphoto2 --list-files

# Test capture (optional)
gphoto2 --capture-image-and-download
```