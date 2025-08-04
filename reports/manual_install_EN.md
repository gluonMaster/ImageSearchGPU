# Manual Installation of Image Search Application

Use this guide if automatic installation via `install.bat` doesn't work.

## ⭐ New Features

This version includes:

- **Modern Results Interface**: Replaced Canvas with Treeview for improved scrolling
- **Eliminated Limitations**: No more element count limits in results
- **Modular UI Architecture**: Separate components in `ui/` folder
- **System Diagnostics**: New `system_check.py` file for readiness verification
- **Smart Updates**: `smart_update.bat` script to preserve settings

See details in files: `USER_GUIDE.md`, `REFACTORING_SUMMARY.md` and main `README.md`

## Step 1: Check Python

Open command prompt (Win+R → cmd → Enter) and run:

```
python --version
```

Should display Python version 3.8 or higher. If command not found:

1. Download Python from https://python.org/downloads/
2. During installation, make sure to check "Add Python to PATH"
3. Restart computer after installation

## Step 2: Navigate to Application Folder

In command prompt, navigate to the folder with application files:

```
cd C:\path\to\application\folder
```

For example:

```
cd C:\ImageSearch
```

## Step 3: Create Virtual Environment (Recommended)

```
python -m venv venv
```

If command executed successfully, activate the environment:

```
venv\Scripts\activate
```

Command prompt should show `(venv)`.

## Step 4: Update pip

```
python -m pip install --upgrade pip
```

## Step 5: Install Dependencies

### Option A: Install from requirements.txt

```
pip install -r requirements.txt
```

### Option B: Step-by-step installation (if Option A doesn't work)

```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
pip install Pillow
pip install numpy
pip install psutil
```

## Step 6: Verify Installation

```
python -c "import torch; print('PyTorch OK')"
python -c "import sentence_transformers; print('sentence-transformers OK')"
python -c "from PIL import Image; print('Pillow OK')"
python -c "import numpy; print('numpy OK')"
python -c "import psutil; print('psutil OK')"
```

All commands should execute without errors.

## Step 7: System Diagnostics (Recommended)

Run system readiness check:

```
python system_check.py
```

This script will check:

- Python version
- GPU availability
- Free memory amount
- Installed dependencies
- Configuration correctness

## Step 8: Create Cache Folder

```
mkdir cache
```

## Step 9: Run Application

```
python main.py
```

## Possible Issues and Solutions

### Error "Microsoft Visual C++ 14.0 is required"

Download and install "Microsoft C++ Build Tools" from the official Microsoft website.

### Error installing torch

Try installing CPU version:

```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

For GPU support (NVIDIA):

```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Results interface issues

If search results display incorrectly, ensure that:

1. Current tkinter version is installed
2. New Treeview-based interface is being used
3. No conflicts with other GUI libraries

### Modular structure errors

If module import errors from `ui/` folder occur:

1. Ensure `ui/` folder contains `__init__.py` file
2. Check that you're running application from project root folder

### Error "No module named '\_tkinter'"

Tkinter should be included in standard Python installation. If missing, reinstall Python from the official website.

### Application starts but cannot load model

Ensure you have stable internet connection. On first launch, the model is downloaded (~500 MB).

## Create Shortcut

After successful installation, create `start.bat` file in application folder:

```batch
@echo off
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python main.py
pause
```

Or use existing `run.bat` file if available.

## Verify Operation

1. Run diagnostics: `python system_check.py`
2. Run application: `python main.py`
3. Select folder with several images
4. Click "Build Index"
5. After completion, try searching
6. Check new tabular results interface with sorting

## Additional Features

### GPU Acceleration

To configure GPU support use:

```
python gpu_setup.py
```

### Update Dependencies

To update dependencies without losing settings:

```
python -m pip install --upgrade -r requirements.txt
```

### Clear Cache

To clear cache and free space:

```
# Delete all cache files
rmdir /s cache
mkdir cache
```

If everything works correctly, the application is ready to use with the new improved interface!
