@echo off
REM MySQL Navigator - Windows Build Script
REM Creates a standalone executable using PyInstaller

echo ========================================
echo MySQL Navigator - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo [1/5] Checking for virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

echo.
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [3/5] Installing/Updating dependencies...
if exist "requirements.txt" (
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo [WARNING] requirements.txt not found, skipping dependency installation
)

echo.
echo [4/5] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [5/5] Building executable...

REM Check for icon file and convert if needed
set ICON_PARAM=
if exist "icon.png" (
    echo Using icon: icon.png
    REM Convert PNG to ICO if it doesn't exist
    if not exist "icon.ico" (
        echo Converting icon.png to icon.ico...
        python -c "from PIL import Image; img = Image.open('icon.png'); img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])" 2>nul
        if errorlevel 1 (
            echo [WARNING] Failed to convert icon.png to .ico format, using PNG directly
            set ICON_PARAM=--icon=icon.png
        ) else (
            set ICON_PARAM=--icon=icon.ico
        )
    else (
        set ICON_PARAM=--icon=icon.ico
    )
) else (
    if exist "icon.ico" (
        echo Using icon: icon.ico
        set ICON_PARAM=--icon=icon.ico
    ) else (
        echo [WARNING] No icon file (icon.png or icon.ico) found in repo directory
        echo Building without custom icon
    )
)

echo.
echo [5/5] Creating PyInstaller hook for MySQL Connector...
echo from PyInstaller.utils.hooks import collect_data_files, collect_submodules > hook-mysql_connector.py
echo. >> hook-mysql_connector.py
echo datas = collect_data_files('mysql.connector') >> hook-mysql_connector.py
echo. >> hook-mysql_connector.py
echo hiddenimports = collect_submodules('mysql.connector') >> hook-mysql_connector.py
echo hiddenimports.extend([ >> hook-mysql_connector.py
echo     'mysql.connector.plugins.mysql_native_password', >> hook-mysql_connector.py
echo     'mysql.connector.plugins.caching_sha2_password', >> hook-mysql_connector.py
echo     'mysql.connector.plugins.mysql_clear_password', >> hook-mysql_connector.py
echo ]) >> hook-mysql_connector.py

echo.
echo [6/6] Building executable with PyInstaller...

REM Build with PyInstaller
pyinstaller --name="MySQL_Navigator" ^
    --onefile ^
    --windowed ^
    --add-data="app.py;." ^
    --add-data="db.py;." ^
    --add-data="backup.py;." ^
    --add-data="operations.py;." ^
    --add-data="config.py;." ^
    --hidden-import="PIL._tkinter_finder" ^
    --hidden-import="PIL.ImageTk" ^
    --hidden-import="PIL.Image" ^
    --hidden-import="ttkbootstrap" ^
    --hidden-import="ttkthemes" ^
    --hidden-import="mysql.connector" ^
    --hidden-import="mysql.connector.plugins.mysql_native_password" ^
    --hidden-import="mysql.connector.plugins.caching_sha2_password" ^
    --hidden-import="cryptography" ^
    --hidden-import="tkinterdnd2" ^
    --additional-hooks-dir=. ^
    --additional-hooks-dir=%~dp0 ^
    %ICON_PARAM% ^
    --clean ^
    --noconfirm ^
    app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\MySQL_Navigator.exe
echo.
echo Note: Make sure MySQL and mysqldump are installed
echo and accessible in your system PATH for full functionality.
echo.
pause