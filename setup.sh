#!/bin/bash

# 📸 HafiPortrait DSLR Setup Script (Linux/Mac)
# Automated setup untuk gphoto2 + Python dependencies

echo "🎯 HafiPortrait DSLR Setup Starting..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Jangan jalankan script ini sebagai root!"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_status "Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    print_status "Detected: macOS"
else
    print_error "OS tidak didukung: $OSTYPE"
    exit 1
fi

# Step 1: Install gphoto2
echo ""
echo "📷 Step 1: Installing gphoto2..."
echo "================================"

if [[ "$OS" == "linux" ]]; then
    print_status "Installing gphoto2 untuk Linux..."
    
    # Update package list
    sudo apt update
    
    # Install gphoto2 and development libraries
    sudo apt install -y gphoto2 libgphoto2-dev libgphoto2-6
    
    # Install additional dependencies
    sudo apt install -y python3-dev python3-pip python3-venv
    
elif [[ "$OS" == "mac" ]]; then
    print_status "Installing gphoto2 untuk macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew tidak ditemukan. Install Homebrew dulu:"
        print_error "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install gphoto2 via Homebrew
    brew install gphoto2
    
    # Install Python if not available
    if ! command -v python3 &> /dev/null; then
        brew install python3
    fi
fi

# Verify gphoto2 installation
if command -v gphoto2 &> /dev/null; then
    GPHOTO_VERSION=$(gphoto2 --version | head -n1)
    print_success "gphoto2 installed: $GPHOTO_VERSION"
else
    print_error "gphoto2 installation failed!"
    exit 1
fi

# Step 2: Test gphoto2 detection
echo ""
echo "🔍 Step 2: Testing camera detection..."
echo "====================================="

print_status "Scanning untuk cameras..."
CAMERA_DETECT=$(gphoto2 --auto-detect 2>/dev/null)

echo "$CAMERA_DETECT"

if echo "$CAMERA_DETECT" | grep -q "Nikon"; then
    print_success "Nikon camera detected!"
elif echo "$CAMERA_DETECT" | grep -q "usb:"; then
    print_warning "Camera detected, tapi bukan Nikon. Check compatibility."
else
    print_warning "No camera detected. Pastikan:"
    echo "  - Nikon D7100 connected via USB"
    echo "  - Camera dalam mode PTP/MTP"
    echo "  - USB cable working properly"
fi

# Step 3: Python virtual environment
echo ""
echo "🐍 Step 3: Setting up Python environment..."
echo "==========================================="

print_status "Creating Python virtual environment..."
python3 -m venv venv

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install Python dependencies
echo ""
echo "📦 Step 4: Installing Python dependencies..."
echo "============================================"

if [ -f "requirements.txt" ]; then
    print_status "Installing dari requirements.txt..."
    pip install -r requirements.txt
else
    print_status "Installing essential packages..."
    pip install gphoto2 pillow requests watchdog rawpy numpy
fi

# Step 5: Create directories
echo ""
echo "📁 Step 5: Creating directories..."
echo "================================="

mkdir -p presets temp logs

print_success "Directories created:"
print_success "  - presets/ (untuk Adobe Lightroom XMP files)"
print_success "  - temp/ (untuk temporary processing)"
print_success "  - logs/ (untuk log files)"

# Step 6: Set permissions
echo ""
echo "🔐 Step 6: Setting permissions..."
echo "==============================="

# Make scripts executable
chmod +x run.py 2>/dev/null || true
chmod +x setup.sh

# Set proper permissions for camera access (Linux only)
if [[ "$OS" == "linux" ]]; then
    print_status "Setting up camera permissions..."
    
    # Add user to plugdev group (for camera access)
    sudo usermod -a -G plugdev $USER
    
    print_warning "IMPORTANT: Logout dan login kembali untuk apply group permissions!"
fi

# Step 7: Final verification
echo ""
echo "✅ Step 7: Final verification..."
echo "==============================="

print_status "Checking Python packages..."
python -c "
try:
    import gphoto2
    print('✅ gphoto2 Python binding: OK')
except ImportError:
    print('❌ gphoto2 Python binding: FAILED')

try:
    import PIL
    print('✅ Pillow (PIL): OK')
except ImportError:
    print('❌ Pillow (PIL): FAILED')

try:
    import requests
    print('✅ requests: OK')
except ImportError:
    print('❌ requests: FAILED')
"

# Deactivate virtual environment
deactivate

echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_success "gphoto2 dan Python dependencies berhasil diinstall!"

echo ""
echo "📋 Next Steps:"
echo "1. Connect Nikon D7100 via USB"
echo "2. Edit config.json (set web project URL)"
echo "3. Add Adobe presets ke folder presets/"
echo "4. Add watermark.png file"
echo "5. Run: python run.py"

echo ""
print_warning "NOTES:"
if [[ "$OS" == "linux" ]]; then
    echo "- Logout/login untuk apply camera permissions"
fi
echo "- Test camera detection: gphoto2 --auto-detect"
echo "- Activate venv: source venv/bin/activate"

echo ""
print_success "Setup script completed successfully! 🚀"