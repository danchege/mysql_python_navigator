#!/bin/bash
# MySQL Navigator - Linux Build Script
# Creates a standalone executable using PyInstaller

echo "========================================"
echo "MySQL Navigator - Linux Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "[1/5] Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi

echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi

echo ""
echo "[3/5] Installing/Updating dependencies..."
if [ -f "requirements.txt" ]; then
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install requirements"
        exit 1
    fi
else
    echo "[WARNING] requirements.txt not found, skipping dependency installation"
fi

echo ""
echo "[4/5] Installing PyInstaller..."
pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install PyInstaller"
    exit 1
fi

echo ""
echo "[5/5] Building executable..."

# Check for icon file
ICON_PARAM=""
if [ -f "icon.ico" ] || [ -f "icon.png" ]; then
    if [ -f "icon.png" ]; then
        echo "Using icon: icon.png"
        # Convert PNG to ICO if it doesn't exist
        if [ ! -f "icon.ico" ]; then
            echo "Converting icon.png to icon.ico..."
            if command -v convert &> /dev/null; then
                convert icon.png -define icon:auto-resize=16,32,48,64,128,256 icon.ico
            else
                echo "[WARNING] ImageMagick not found, using PNG icon directly"
                ICON_PARAM="--icon=icon.png"
            fi
        fi
        if [ -f "icon.ico" ]; then
            ICON_PARAM="--icon=icon.ico"
        fi
    else
        echo "[WARNING] No icon file (icon.png) found in repo directory"
        echo "Building without custom icon"
    fi
else
    echo "[WARNING] No icon file (icon.ico or icon.png) found in repo directory"
    echo "Building without custom icon"
fi

# Create a hook file for MySQL Connector
echo "Creating PyInstaller hook for MySQL Connector..."
cat > hook-mysql_connector.py << 'EOL'
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('mysql.connector')

hiddenimports = collect_submodules('mysql.connector')
hiddenimports.extend([
    'mysql.connector.plugins.mysql_native_password',
    'mysql.connector.plugins.caching_sha2_password',
    'mysql.connector.plugins.mysql_clear_password',
])
EOL

# Build with PyInstaller
echo "[5/5] Building executable with PyInstaller..."
pyinstaller --name="MySQL_Navigator" \
    --onefile \
    --windowed \
    --add-data="app.py:." \
    --add-data="db.py:." \
    --add-data="backup.py:." \
    --add-data="operations.py:." \
    --add-data="config.py:." \
    --hidden-import="PIL._tkinter_finder" \
    --hidden-import="PIL.ImageTk" \
    --hidden-import="PIL.Image" \
    --hidden-import="ttkbootstrap" \
    --hidden-import="ttkthemes" \
    --hidden-import="mysql.connector" \
    --hidden-import="mysql.connector.plugins.mysql_native_password" \
    --hidden-import="mysql.connector.plugins.caching_sha2_password" \
    --hidden-import="cryptography" \
    --hidden-import="tkinterdnd2" \
    --additional-hooks-dir=. \
    --additional-hooks-dir=$(pwd) \
    $ICON_PARAM \
    --clean \
    --noconfirm \
    app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "Executable location: dist/MySQL_Navigator"
echo ""
echo "Note: Make sure MySQL and mysqldump are installed"
echo "and accessible in your system PATH for full functionality."
echo ""

# Make the executable... executable
chmod +x dist/MySQL_Navigator

echo "Permissions set. You can run: ./dist/MySQL_Navigator"
echo ""