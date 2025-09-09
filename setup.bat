@echo off
REM 📸 HafiPortrait DSLR Setup Script (Windows)
REM Automated setup untuk gphoto2 + Python dependencies

echo 🎯 HafiPortrait DSLR Setup Starting...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan!
    echo Download dan install Python dari: https://python.org
    echo Pastikan "Add Python to PATH" dicentang saat install
    pause
    exit /b 1
)

echo ✅ Python detected
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip tidak ditemukan!
    echo Install pip atau reinstall Python dengan pip
    pause
    exit /b 1
)

echo ✅ pip detected

echo.
echo 📷 Step 1: gphoto2 untuk Windows
echo ================================
echo.
echo MANUAL STEP REQUIRED:
echo 1. Download gphoto2 untuk Windows dari:
echo    https://github.com/gphoto/gphoto2/releases
echo 2. Extract dan add ke PATH, atau
echo 3. Install via MSYS2/MinGW
echo.
echo Alternative: Gunakan libgphoto2 Python binding
echo (akan diinstall otomatis via pip)
echo.

REM Create virtual environment
echo 🐍 Step 2: Creating Python virtual environment...
echo ===============================================
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo.
echo 📦 Step 3: Installing Python dependencies...
echo ==========================================

if exist requirements.txt (
    echo Installing dari requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing essential packages...
    pip install pillow requests watchdog rawpy numpy
    
    REM Try to install gphoto2 Python binding
    echo Installing gphoto2 Python binding...
    pip install gphoto2 || (
        echo ⚠️  gphoto2 Python binding gagal install
        echo Akan menggunakan alternative method
    )
)

REM Create directories
echo.
echo 📁 Step 4: Creating directories...
echo ===============================

if not exist "presets" mkdir presets
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs

echo ✅ Directories created:
echo   - presets\ (untuk Adobe Lightroom XMP files)
echo   - temp\ (untuk temporary processing)
echo   - logs\ (untuk log files)

REM Final verification
echo.
echo ✅ Step 5: Final verification...
echo =============================

python -c "
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

try:
    import rawpy
    print('✅ rawpy: OK')
except ImportError:
    print('❌ rawpy: FAILED')

try:
    import gphoto2
    print('✅ gphoto2 Python binding: OK')
except ImportError:
    print('⚠️  gphoto2 Python binding: Not available')
    print('   Will use alternative camera detection')
"

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo.
echo 🎉 Setup Complete!
echo ================
echo ✅ Python dependencies berhasil diinstall!

echo.
echo 📋 Next Steps:
echo 1. Install gphoto2 untuk Windows (manual)
echo 2. Connect Nikon D7100 via USB
echo 3. Edit config.json (set web project URL)
echo 4. Add Adobe presets ke folder presets\
echo 5. Add watermark.png file
echo 6. Run: python run.py

echo.
echo 📝 NOTES:
echo - Untuk activate venv: venv\Scripts\activate.bat
echo - Test camera: gphoto2 --auto-detect (jika installed)
echo - Alternative: Script akan auto-detect via USB monitoring

echo.
echo ✅ Setup script completed successfully! 🚀
pause