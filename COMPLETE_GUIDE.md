# 🎯 HafiPortrait DSLR Complete System Guide

**Complete standalone system untuk auto-upload foto DSLR ke HafiPortrait web project.**

---

## 📋 System Overview

### **What This System Does:**
1. **Monitor** Nikon D7100 untuk new photos (real-time)
2. **Apply** Adobe Lightroom presets (.xmp files)
3. **Add** transparent watermark (bottom-center positioning)
4. **Upload** processed photos ke HafiPortrait web project
5. **Backup** original files untuk quality preservation

### **Target Workflow:**
```
Shutter → Auto-detect → Apply Preset → Add Watermark → Upload → Appear in Gallery
```

**Performance Target:** 30-60 seconds per photo

---

## 🚀 Quick Start (5 Minutes)

### **1. Setup Dependencies**
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

### **2. Test System**
```bash
# Activate environment
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate.bat   # Windows

# Test all components
python test_complete_system.py
```

### **3. Configure**
```bash
# Edit configuration
nano config.json

# Set:
# - watch_directory: path ke camera folder
# - base_url: your web project URL
```

### **4. Add Assets**
```bash
# Add Adobe presets
cp your_presets/*.xmp presets/

# Add watermark
cp your_watermark.png watermark.png
```

### **5. Run**
```bash
python run.py
```

---

## 📁 Complete File Structure

```
standalone-dslr/
├── 📄 run.py                    # Main script - START HERE
├── ⚙️ config.json              # Configuration file
├── 🖼️ watermark.png            # Your watermark file
├── 📋 requirements.txt         # Python dependencies
├── 🔧 setup.sh / setup.bat     # Setup scripts
├── 🧪 test_*.py               # Test scripts
├── 📚 *.md                     # Documentation
├── 📁 presets/                 # Adobe Lightroom XMP files
│   ├── wedding_warm.xmp
│   ├── wedding_classic.xmp
│   └── portrait_soft.xmp
├── 📁 lib/                     # Core modules
│   ├── camera.py              # gphoto2 integration
│   ├── preset_processor.py    # Adobe preset system
│   ├── watermark_manager.py   # Watermark application
│   ├── uploader.py            # Upload to web project
│   └── utils.py               # Helper functions
├── 📁 temp/                    # Temporary processing
├── 📁 logs/                    # Log files
└── 📁 venv/                    # Python virtual environment
```

---

## 🔧 Configuration Guide

### **config.json Sections:**

#### **Camera Settings**
```json
{
    "camera": {
        "model": "Nikon D7100",
        "watch_directory": "/path/to/camera/photos",
        "file_extensions": [".NEF", ".JPG", ".JPEG"],
        "auto_detect": true
    }
}
```

#### **Web Project Integration**
```json
{
    "web_project": {
        "base_url": "http://your-vps:3002",
        "upload_endpoint": "/api/dslr/upload",
        "timeout": 30
    }
}
```

#### **Processing Settings**
```json
{
    "processing": {
        "default_preset": "wedding_warm",
        "auto_watermark": true,
        "backup_originals": true,
        "quality": 95
    }
}
```

#### **Watermark Configuration**
```json
{
    "watermark": {
        "file": "./watermark.png",
        "position": "bottom_center",
        "size_percentage": 15,
        "margin_bottom": 10
    }
}
```

---

## 🎨 Adobe Preset System

### **Supported Formats:**
- ✅ **Adobe Lightroom** .xmp files
- ✅ **Adobe Camera Raw** presets
- ✅ **Custom** preset parameters

### **Adding Your Presets:**

#### **From Lightroom:**
1. **Develop Module** → **Presets Panel**
2. **Right-click** preset → **Export**
3. **Save as** .xmp file
4. **Copy** ke folder `presets/`

#### **Preset Settings Supported:**
- Exposure, Contrast, Highlights, Shadows
- Whites, Blacks, Vibrance, Saturation
- Temperature, Tint, Clarity
- Sharpening, Noise Reduction

### **Sample Presets Included:**
- **wedding_warm.xmp** - Warm tones untuk wedding
- **wedding_classic.xmp** - Classic wedding look
- **portrait_soft.xmp** - Soft portrait style

---

## 🏷️ Watermark System

### **Watermark Requirements:**
- **Format:** PNG dengan transparency
- **Recommended Size:** 300x80 pixels
- **Position:** Bottom-center, 10% from bottom
- **Size:** 15% of image width (configurable)

### **Creating Watermark:**
```python
# Sample watermark creation
from PIL import Image, ImageDraw, ImageFont

watermark = Image.new('RGBA', (300, 80), (0, 0, 0, 0))
draw = ImageDraw.Draw(watermark)
font = ImageFont.truetype("arial.ttf", 36)

# Add shadow effect
draw.text((2, 2), "HafiPortrait", font=font, fill=(0, 0, 0, 128))
draw.text((0, 0), "HafiPortrait", font=font, fill=(255, 255, 255, 200))

watermark.save("watermark.png")
```

---

## 🔗 Web Project Integration

### **API Endpoints Required:**

#### **Upload Endpoint** (`/api/dslr/upload`)
```javascript
// Expected request
POST /api/dslr/upload
Content-Type: multipart/form-data

{
    photo: File,
    eventId: string,
    albumName: string,
    originalFileName: string,
    presetApplied: string,
    watermarkApplied: boolean
}
```

#### **Status Endpoint** (`/api/dslr/status`)
```javascript
// Expected response
{
    status: "ready" | "busy" | "error",
    currentEvent: {
        id: string,
        name: string,
        albumName: string
    }
}
```

### **Event Context:**
System akan auto-detect current active event dari web project atau bisa di-set manual via admin dashboard.

---

## 📊 Monitoring & Status

### **Real-time Status:**
```bash
# Check system status
cat dslr_status.json

# View logs
tail -f logs/dslr_system.log
```

### **Status File Format:**
```json
{
    "system_status": "running",
    "stats": {
        "photos_processed": 15,
        "photos_uploaded": 14,
        "errors": 1
    },
    "camera_status": {
        "connected": true,
        "model": "Nikon D7100"
    }
}
```

---

## 🧪 Testing Guide

### **Test Scripts Available:**

#### **1. gphoto2 Setup Test**
```bash
python test_gphoto2.py
```
Tests camera detection dan gphoto2 installation.

#### **2. Complete System Test**
```bash
python test_complete_system.py
```
Tests all components: presets, watermark, upload, integration.

#### **3. Individual Component Tests**
```bash
# Test preset parsing
python lib/preset_processor.py

# Test watermark application
python lib/watermark_manager.py

# Test upload client
python lib/uploader.py
```

---

## 🔧 Troubleshooting

### **Common Issues:**

#### **❌ "No cameras detected"**
```bash
# Check USB connection
gphoto2 --auto-detect

# Check camera mode (should be PTP/MTP)
# Check USB cable
# Try different USB port
```

#### **❌ "gphoto2 not found"**
```bash
# Linux
sudo apt install gphoto2 libgphoto2-dev

# macOS
brew install gphoto2

# Windows
# Download dari gphoto.org
```

#### **❌ "Permission denied" (Linux)**
```bash
# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Logout dan login kembali
```

#### **❌ "Upload failed"**
```bash
# Check web project running
curl http://your-vps:3002/api/health

# Check network connection
# Check API endpoints
```

#### **❌ "Preset parsing failed"**
```bash
# Check XMP file format
# Validate XML syntax
# Check file permissions
```

---

## 🚀 Production Deployment

### **Laptop/Computer Setup:**
1. **Install** dependencies via setup script
2. **Configure** camera folder path
3. **Add** your presets dan watermark
4. **Test** dengan test scripts
5. **Run** main script

### **VPS Web Project:**
1. **Add** DSLR API endpoints
2. **Configure** event management
3. **Test** upload functionality
4. **Monitor** via admin dashboard

### **Workflow Integration:**
1. **Set active event** di admin dashboard
2. **Connect** Nikon D7100 ke laptop
3. **Start** DSLR script
4. **Take photos** - auto-upload ke gallery
5. **Monitor** progress via status file

---

## 📈 Performance Optimization

### **Target Performance:**
- **File Detection:** < 5 seconds
- **Preset Application:** 10-15 seconds
- **Watermark:** 2-3 seconds
- **Upload:** 10-20 seconds
- **Total:** 30-60 seconds per photo

### **Optimization Tips:**
- Use **SSD** untuk faster file processing
- **Stable internet** untuk reliable uploads
- **USB 3.0** untuk faster camera communication
- **Adequate RAM** untuk image processing

---

## 🎯 Success Criteria

### **System Ready When:**
- ✅ All tests pass (`test_complete_system.py`)
- ✅ Camera detected dan connected
- ✅ Presets loaded successfully
- ✅ Watermark applied correctly
- ✅ Web project connection working
- ✅ Upload successful

### **Production Ready When:**
- ✅ Real photos processed successfully
- ✅ Performance within target (30-60s)
- ✅ Error handling working
- ✅ Monitoring dan logging active
- ✅ Backup system functional

---

## 🆘 Support & Resources

### **Documentation:**
- `README.md` - Basic overview
- `QUICK_START.md` - Setup instructions
- `COMPLETE_GUIDE.md` - This comprehensive guide

### **Test Scripts:**
- `test_gphoto2.py` - Camera setup validation
- `test_complete_system.py` - Full system test

### **Log Files:**
- `logs/dslr_system.log` - System operations
- `dslr_status.json` - Real-time status

### **Configuration:**
- `config.json` - Main configuration
- `presets/` - Adobe Lightroom presets
- `watermark.png` - Watermark file

---

**🎉 Ready untuk professional photography workflow!**