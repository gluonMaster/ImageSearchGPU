@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ======================================================
echo    Image Search Application - Universal Installer
echo ======================================================
echo.
echo Welcome to Image Search Application installer!
echo This script will automatically configure everything needed.
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check operating system
echo [1/8] Checking system...
ver | find "Windows" >nul
if %errorlevel% neq 0 (
    echo ERROR: This script is designed for Windows
    pause
    exit /b 1
)
echo ✅ Windows detected

REM Check Python
echo.
echo [2/8] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip not found!
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)
echo ✅ pip found

REM Installation type selection
echo.
echo [3/8] Choose installation type...
echo.
echo Select installation type:
echo.
echo 1) CPU only (slower, but works on any computer)
echo 2) GPU CUDA (faster, requires NVIDIA GPU with CUDA support)
echo 3) Automatic detection (recommended)
echo.
set /p INSTALL_TYPE="Enter number (1-3): "

if "%INSTALL_TYPE%"=="1" (
    set "INSTALL_MODE=CPU"
    echo Selected: CPU installation
) else if "%INSTALL_TYPE%"=="2" (
    set "INSTALL_MODE=GPU"
    echo Selected: GPU installation
) else if "%INSTALL_TYPE%"=="3" (
    set "INSTALL_MODE=AUTO"
    echo Selected: Automatic detection
) else (
    echo Invalid choice. Using automatic detection.
    set "INSTALL_MODE=AUTO"
)

REM Automatic GPU detection
if "%INSTALL_MODE%"=="AUTO" (
    echo.
    echo Detecting GPU capabilities...
    
    REM Check for NVIDIA GPU via wmic
    wmic path win32_VideoController get name | find /i "nvidia" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ NVIDIA GPU detected
        set "INSTALL_MODE=GPU"
        
        REM Additional compatibility check
        wmic path win32_VideoController get name | find /i "RTX" >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ RTX GPU detected - excellent for acceleration!
        ) else (
            wmic path win32_VideoController get name | find /i "GTX" >nul 2>&1
            if !errorlevel! equ 0 (
                echo ✅ GTX GPU detected - good for acceleration
            )
        )
    ) else (
        echo ℹ️  NVIDIA GPU not detected, using CPU mode
        set "INSTALL_MODE=CPU"
    )
)

echo.
echo Installation mode: !INSTALL_MODE!
echo.

REM Virtual environment setup
echo [4/8] Setting up virtual environment...

set "VENV_PATH="
set "VENV_PYTHON="

REM Check existing environments
if exist ".venv\Scripts\activate.bat" (
    echo ✅ Found existing environment .venv
    set "VENV_PATH=.venv"
    set "VENV_PYTHON=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\activate.bat" (
    echo ✅ Found existing environment venv
    set "VENV_PATH=venv"
    set "VENV_PYTHON=venv\Scripts\python.exe"
) else (
    echo Creating new virtual environment...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo WARNING: Failed to create virtual environment
        echo Continuing with global installation...
        set "VENV_PYTHON=python"
    ) else (
        echo ✅ Virtual environment created: .venv
        set "VENV_PATH=.venv"
        set "VENV_PYTHON=.venv\Scripts\python.exe"
    )
)

REM Activate environment
if not "%VENV_PATH%"=="" (
    echo Activating virtual environment...
    call "%VENV_PATH%\Scripts\activate.bat"
    echo ✅ Virtual environment activated
)

REM Update pip
echo.
echo [5/8] Updating pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
if !errorlevel! neq 0 (
    echo WARNING: Failed to update pip
) else (
    echo ✅ pip updated
)

REM Install base dependencies
echo.
echo [6/8] Installing base dependencies...
echo This may take several minutes...

REM Install core packages
echo Installing core libraries...
"%VENV_PYTHON%" -m pip install --quiet "sentence-transformers>=2.2.2" "Pillow>=9.0.0" "numpy>=1.21.0" "psutil>=5.9.0"
if !errorlevel! neq 0 (
    echo ❌ Error installing core dependencies!
    echo Try installing manually:
    echo pip install sentence-transformers Pillow numpy psutil
    pause
    exit /b 1
)
echo ✅ Core libraries installed

REM Install PyTorch based on mode
echo.
echo [7/8] Installing PyTorch...

if "!INSTALL_MODE!"=="CPU" (
    echo Installing CPU version of PyTorch...
    "%VENV_PYTHON%" -m pip install --quiet "torch>=2.0.0" "torchvision>=0.15.0" --index-url https://download.pytorch.org/whl/cpu
    if !errorlevel! neq 0 (
        echo WARNING: Failed to install CPU version of PyTorch
        echo Trying standard installation...
        "%VENV_PYTHON%" -m pip install --quiet "torch>=2.0.0" "torchvision>=0.15.0"
    )
    echo ✅ PyTorch CPU installed
    
) else if "!INSTALL_MODE!"=="GPU" (
    echo Installing GPU version of PyTorch with CUDA...
    
    REM First remove existing versions
    "%VENV_PYTHON%" -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1
    
    REM Install CUDA version
    "%VENV_PYTHON%" -m pip install --quiet "torch>=2.0.0" "torchvision>=0.15.0" --index-url https://download.pytorch.org/whl/cu118
    if !errorlevel! neq 0 (
        echo WARNING: Failed to install CUDA version of PyTorch
        echo Trying standard installation...
        "%VENV_PYTHON%" -m pip install --quiet "torch>=2.0.0" "torchvision>=0.15.0"
        set "INSTALL_MODE=CPU"
    ) else (
        echo ✅ PyTorch CUDA installed
    )
)

REM Check all requirements from requirements.txt
echo.
echo Checking all requirements...
if exist "requirements.txt" (
    "%VENV_PYTHON%" -m pip install -r requirements.txt --quiet
    if !errorlevel! neq 0 (
        echo WARNING: Some dependencies from requirements.txt may not have installed
    )
)

REM Create necessary directories
echo.
echo [8/8] Final setup...

if not exist "cache" (
    mkdir cache
    echo ✅ Created cache folder
)

REM Final verification
echo.
echo === INSTALLATION VERIFICATION ===
echo.

REM Check Python modules
echo Checking core modules...
"%VENV_PYTHON%" -c "import torch; import torchvision; import sentence_transformers; import PIL; import numpy; import psutil; print('✅ All core modules imported successfully')" 2>nul
if !errorlevel! neq 0 (
    echo ❌ Error importing modules!
    echo.
    echo Try running:
    echo "%VENV_PYTHON%" -c "import torch; print('PyTorch:', torch.__version__)"
    echo.
    pause
    exit /b 1
)

REM Check GPU functionality
if "!INSTALL_MODE!"=="GPU" (
    echo.
    echo Checking GPU functionality...
    "%VENV_PYTHON%" -c "import torch; cuda_available = torch.cuda.is_available(); print(f'CUDA available: {cuda_available}'); print(f'Devices: {torch.cuda.device_count() if cuda_available else 0}'); [print(f'GPU {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())] if cuda_available else None"
    if !errorlevel! neq 0 (
        echo WARNING: Issues with GPU check
        set "INSTALL_MODE=CPU"
    )
)

REM Check memory
echo.
echo Checking system memory...
"%VENV_PYTHON%" -c "import psutil; mem = psutil.virtual_memory(); print(f'Total memory: {mem.total / (1024**3):.1f} GB'); print(f'Available memory: {mem.available / (1024**3):.1f} GB'); print(f'Used: {mem.percent:.1f}%%'); print('✅ Sufficient memory for operation' if mem.available > 2*1024**3 else '⚠️ Low free memory - recommend freeing resources')"

REM Create installation info
echo.
echo Creating installation info...
echo Installation completed on %date% %time% > installation_info.txt
echo Python version: %PYTHON_VERSION% >> installation_info.txt
echo Install mode: !INSTALL_MODE! >> installation_info.txt
echo Virtual environment: %VENV_PATH% >> installation_info.txt
echo Python executable: %VENV_PYTHON% >> installation_info.txt
echo. >> installation_info.txt
"%VENV_PYTHON%" -m pip freeze >> installation_info.txt

REM Create startup script
echo.
echo Creating startup script...
echo @echo off > start_app.bat
echo cd /d "%%~dp0" >> start_app.bat
if not "%VENV_PATH%"=="" (
    echo call "%VENV_PATH%\Scripts\activate.bat" >> start_app.bat
)
echo "%VENV_PYTHON%" main.py >> start_app.bat
echo pause >> start_app.bat

echo ✅ Created start_app.bat for easy launch

REM Final message
echo.
echo ======================================================
echo           ✅ INSTALLATION COMPLETED SUCCESSFULLY!
echo ======================================================
echo.
echo Configuration:
echo   • Mode: !INSTALL_MODE!
if "!INSTALL_MODE!"=="GPU" (
    echo   • GPU acceleration: Enabled
    echo   • Performance: High
) else (
    echo   • GPU acceleration: Disabled
    echo   • Performance: Standard
)
echo   • Virtual environment: %VENV_PATH%
echo   • Memory optimization: Enabled
echo.
echo Application features:
echo   • Search images by description
echo   • Process large collections (up to 70k+ images)
echo   • Automatic memory management
echo   • Recovery from interruptions
echo   • Organize photos by dates
echo.
echo Launch options:
echo   1) Double-click start_app.bat (recommended)
echo   2) Run main.py through Python
echo.
echo Installation files:
echo   • installation_info.txt - installation information
echo   • start_app.bat - quick launch script
echo.

REM Launch offer
echo.
set /p START_NOW="Launch application now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo.
    echo Starting application...
    echo.
    start_app.bat
) else (
    echo.
    echo Application ready to use!
    echo Use start_app.bat to launch
    echo.
    pause
)

endlocal
