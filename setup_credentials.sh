#!/bin/bash
# 🔧 Setup Credentials for Standalone DSLR System
# Copies environment variables from main project and validates setup

echo "🔧 HafiPortrait DSLR Credentials Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if main project .env exists
MAIN_ENV="../.env.local"
if [ ! -f "$MAIN_ENV" ]; then
    MAIN_ENV="../.env"
fi

if [ ! -f "$MAIN_ENV" ]; then
    print_error "Main project .env file not found!"
    print_info "Please ensure main project has .env.local or .env file"
    exit 1
fi

print_status "Found main project environment file: $MAIN_ENV"

# Create .env file for standalone DSLR
DSLR_ENV=".env"

print_info "Creating standalone DSLR .env file..."

# Copy essential variables from main project
echo "# 🔧 Standalone DSLR Environment Configuration" > $DSLR_ENV
echo "# Auto-generated from main project on $(date)" >> $DSLR_ENV
echo "" >> $DSLR_ENV

# Extract and copy Supabase variables
echo "# ===== SUPABASE CONFIGURATION =====" >> $DSLR_ENV
grep "NEXT_PUBLIC_SUPABASE_URL" $MAIN_ENV >> $DSLR_ENV 2>/dev/null || echo "NEXT_PUBLIC_SUPABASE_URL=" >> $DSLR_ENV
grep "NEXT_PUBLIC_SUPABASE_ANON_KEY" $MAIN_ENV >> $DSLR_ENV 2>/dev/null || echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=" >> $DSLR_ENV
grep "SUPABASE_SERVICE_ROLE_KEY" $MAIN_ENV >> $DSLR_ENV 2>/dev/null || echo "SUPABASE_SERVICE_ROLE_KEY=" >> $DSLR_ENV
echo "" >> $DSLR_ENV

# Extract and copy App URL
echo "# ===== WEB PROJECT URL =====" >> $DSLR_ENV
grep "NEXT_PUBLIC_APP_URL" $MAIN_ENV >> $DSLR_ENV 2>/dev/null || echo "NEXT_PUBLIC_APP_URL=http://localhost:3002" >> $DSLR_ENV
echo "" >> $DSLR_ENV

# Extract and copy Storage variables
echo "# ===== STORAGE CONFIGURATION =====" >> $DSLR_ENV
grep "R2_" $MAIN_ENV >> $DSLR_ENV 2>/dev/null
grep "GOOGLE_DRIVE_" $MAIN_ENV >> $DSLR_ENV 2>/dev/null
echo "" >> $DSLR_ENV

# Add DSLR-specific configuration
echo "# ===== DSLR SYSTEM CONFIGURATION =====" >> $DSLR_ENV
cat << 'EOF' >> $DSLR_ENV
DSLR_CAMERA_MODEL=Nikon D7100
DSLR_WATCH_DIRECTORY=./test_photos/
DSLR_TEMP_DIRECTORY=./temp/
DSLR_DEFAULT_PRESET=wedding_warm
DSLR_AUTO_WATERMARK=true
DSLR_BACKUP_ORIGINALS=true
DSLR_JPEG_QUALITY=95
DSLR_DEFAULT_ALBUM=Official
DSLR_UPLOADER_NAME=DSLR Auto
DSLR_MAX_RETRIES=3
DSLR_RETRY_DELAY=5

# ===== MONITORING & LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=./logs/dslr_system.log
STATUS_FILE=./dslr_status.json
CONFIG_FILE=./dslr_active_config.json
COMMANDS_FILE=./dslr_commands.json

# ===== DEVELOPMENT SETTINGS =====
DSLR_SIMULATION_MODE=false
DEBUG_API_CALLS=false
DEBUG_FILE_PROCESSING=false
DEBUG_UPLOAD_PROCESS=false
EOF

print_status "Created .env file with configuration"

# Validate environment variables
print_info "Validating environment variables..."

# Source the new .env file
set -a
source $DSLR_ENV
set +a

# Check required variables
REQUIRED_VARS=(
    "NEXT_PUBLIC_SUPABASE_URL"
    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    "SUPABASE_SERVICE_ROLE_KEY"
    "NEXT_PUBLIC_APP_URL"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    else
        print_status "$var: Set"
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    print_warning "Please add these variables to your main project .env file"
    exit 1
fi

# Create necessary directories
print_info "Creating necessary directories..."

mkdir -p test_photos
mkdir -p temp
mkdir -p logs
mkdir -p presets

print_status "Created directories: test_photos, temp, logs, presets"

# Copy test photo if available
if [ -f "../test-photo.jpg" ]; then
    cp "../test-photo.jpg" "./test_photos/"
    print_status "Copied test photo to test_photos/"
fi

# Create watermark if not exists
if [ ! -f "watermark.png" ]; then
    print_info "Creating test watermark..."
    # This would require ImageMagick or similar
    # For now, just create a placeholder
    touch watermark.png
    print_warning "Created placeholder watermark.png - replace with actual watermark"
fi

# Test connection to web project
print_info "Testing connection to web project..."

if command -v curl &> /dev/null; then
    if curl -s -f "${NEXT_PUBLIC_APP_URL}/api/health" > /dev/null; then
        print_status "Web project connection successful"
    else
        print_warning "Could not connect to web project at ${NEXT_PUBLIC_APP_URL}"
        print_info "Make sure web project is running"
    fi
else
    print_warning "curl not available - skipping connection test"
fi

# Final summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_status "Environment file created: .env"
print_status "Directories created: test_photos, temp, logs, presets"
print_status "Configuration validated"

echo ""
echo "📋 Next Steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Add your Adobe Lightroom presets (.xmp) to presets/ folder"
echo "3. Replace watermark.png with your actual watermark"
echo "4. Test the system: python3 lib/uploader_robust.py"
echo "5. Run full system: python3 run.py"

echo ""
print_info "For manual testing, copy photos to test_photos/ directory"