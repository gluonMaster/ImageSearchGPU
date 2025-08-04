# 🚀 Complete User Guide - Image Search by Description

## 📖 About the Application

This application uses modern CLIP technology to search for images using text descriptions in Russian language. You can find photos in your archive by simply describing what's depicted in them.

### 🆕 Latest Updates

- **Modern Results Interface**: New tabular interface based on Treeview
- **Eliminated Scrolling Limitations**: No more element count limits
- **Column Sorting**: Click headers to sort results
- **Keyboard Control**: Space to select, Enter to open
- **Optimized Performance**: Thumbnail caching and batch loading

## 🏗️ Detailed Application Installation

### Method 1: Automatic Installation (Recommended)

#### 1️⃣ System Preparation

1. **Download Python 3.8+** from [python.org](https://python.org/downloads/)

   - ✅ During installation, make sure to check **"Add Python to PATH"**
   - ✅ Choose **"Install for all users"** (recommended)
   - ✅ Restart computer after installation

2. **Download all application files** to a separate folder

   - Create a folder, for example: `C:\ImageSearch`
   - Place all project files there

3. **Check Python** (open command prompt):
   ```
   python --version
   ```
   Should show version 3.8 or higher

#### 2️⃣ Application Installation

1. **Run installer**:

   - Double-click **`install.bat`** file
   - Or open command prompt in application folder and run: `install.bat`

2. **Choose installation type**:

   - **Automatic detection** (recommended) - system will detect GPU automatically
   - **CPU only** - for computers without NVIDIA GPU
   - **GPU CUDA** - for computers with NVIDIA graphics cards

3. **Wait for completion**:
   - Installation may take 5-15 minutes
   - CLIP model will be downloaded (~500 MB)
   - All necessary dependencies will be installed

#### 3️⃣ First Launch

1. **Use launch file**: `start_app.bat` or `run.bat`
2. **Or run manually**: `python main.py` in command prompt

### Method 2: Manual Installation

If automatic installation doesn't work, follow instructions in `reports/manual_install_EN.md`

### Method 3: Update Existing Installation

If application is already installed:

1. **Smart update** (preserves settings):

   ```
   smart_update.bat
   ```

2. **Full update** (resets settings):
   ```
   install.bat
   ```

### 🔍 System Readiness Check

Run diagnostics to verify correct installation:

```batch
python system_check.py
```

Script will check:

- ✅ Python version
- ✅ GPU availability
- ✅ Free memory amount
- ✅ Installed dependencies
- ✅ Configuration correctness

## 🎯 First Use - Step-by-Step Instructions

### Step 1: Launch Application

1. **Start application**:

   - Double-click `start_app.bat` or `run.bat`
   - Or via command prompt: `python main.py`

2. **First launch**:
   - On first launch, CLIP model may be downloaded (~500 MB)
   - This happens only once

### Step 2: Select Photo Folder

1. **Click "Select Folder" button** in main window

   - Or use menu: `File → Select Folder`
   - Or hotkey: `Ctrl+O`

2. **Choose folder** with your photos

   - Supported formats: JPG, JPEG, PNG
   - Application will scan all subfolders

3. **Wait for scan completion**
   - Information about found images will appear
   - File count will be displayed in interface

### Step 3: Build Index

1. **Click "Build Index"**

   - This process analyzes all images
   - Creates search index for fast searching

2. **Monitor progress**:

   - Indicator shows number of processed images
   - For large collections, process runs in chunks
   - Can be safely interrupted and continued later

3. **Wait for completion**:
   - All data is saved to `cache/` folder
   - When reusing same folder, indexing is not needed

### Step 4: Search for Images

1. **Enter description** in search field:

   - Examples: "cat on sofa", "sunset at sea", "children playing"
   - Describe in natural language in Russian

2. **Configure search parameters** (optional):

   - **Max results**: how many images to show (1-100)
   - **Photos from last days**: limit search by time (0 = all photos)

3. **Click "Find"** or press Enter in search field

### Step 5: Working with Results

**New modern results interface**:

1. **Tabular display**:

   - **"Photo" column**: image thumbnails
   - **"Similarity" column**: match coefficient to query
   - **"Size" column**: file size
   - **"Modified Date" column**: when file was modified
   - **"Path" column**: file location

2. **Sort results**:

   - Click any column header to sort
   - Repeated click changes sort direction
   - By default, results sorted by similarity

3. **Select images**:

   - Click row to select/deselect
   - Press `Space` on keyboard to toggle selection
   - Use "Select All" / "Clear Selection" buttons

4. **Image actions**:

   - **Double-click** or **Enter**: open image in default program
   - **"Open" button**: same action
   - **"Open folder" button**: open file folder in explorer

5. **Keyboard control**:
   - **Arrow keys ↑↓**: navigate through results
   - **Space**: select/deselect current item
   - **Enter**: open current image
   - **Ctrl+A**: select all results

### Step 6: Save Selected Photos

1. **Select photos** (check boxes or use Space key)

2. **Click "Save Selected..."**

3. **Choose destination folder** where to save photos

4. **Preview organization**:

   - Photos will be organized into subfolders by dates
   - Folder format: `YYYY-MM` (e.g., `2020-03`, `2021-12`)
   - Date taken from EXIF data or file modification date

5. **Confirm saving**:
   - Progress bar will appear for operation
   - After completion - statistics and option to open result folder

## ⚡ Performance and Optimization

### 📊 Collection Sizes and Processing Time

| Photo Count  | Approx. Time (CPU) | Approx. Time (GPU) | Recommended Memory |
| ------------ | ------------------ | ------------------ | ------------------ |
| Up to 1,000  | 2-5 minutes        | 30-60 seconds      | 2+ GB free         |
| Up to 5,000  | 10-15 minutes      | 2-3 minutes        | 3+ GB free         |
| Up to 25,000 | 30-60 minutes      | 8-12 minutes       | 4+ GB free         |
| Up to 70,000 | 2-4 hours          | 20-30 minutes      | 6+ GB free         |

### 🚀 Tips for Maximum Speed

1. **Use NVIDIA GPU**:

   - RTX/GTX series provide 5-10x acceleration
   - Run `python gpu_setup.py` for setup
   - Or use `smart_update.bat` → "Switch to GPU"

2. **Optimize system**:

   - Close browser and other programs during indexing
   - Use SSD for photo folder and cache
   - Ensure minimum 2 GB RAM is free

3. **Configure application**:
   - `config.py` file contains performance settings
   - `CLIP_BATCH_SIZE` - batch size (reduce if low memory)
   - `THUMBNAIL_SIZE` - thumbnail size (reduce to save memory)

### 💾 Memory Conservation

1. **Automatic management**:

   - Application automatically monitors memory
   - Reduces chunk size when memory is low
   - Shows warnings at critically low memory

2. **Manual optimization**:

   - Close unnecessary programs
   - Clear browser cache
   - Use "Photos from last days" parameter to limit search

3. **Large collection processing**:
   - Large collections processed in chunks (5000 images each)
   - Can safely interrupt process and continue later
   - All processed data saved automatically

### 🔄 Interruption and Recovery

- **Safe interruption**: Can close application during indexing
- **Automatic recovery**: Next launch continues from where stopped
- **Progress saving**: Results of each chunk saved immediately
- **Progress information**: "Chunk 3 of 14 (15000/70000 images)"

## 🔧 Frequently Asked Questions and Solutions

### ❓ Installation Problems

**Application won't start after installation**

1. Check Python: `python --version` (should be 3.8+)
2. Run diagnostics: `python system_check.py`
3. Reinstall: `install.bat`
4. Check logs in `image_search.log` file

**"Module not found" error**

1. Make sure you're using correct launch method:
   - `start_app.bat` or `run.bat` (recommended)
   - Or `python main.py` from application folder
2. Run `smart_update.bat` to fix dependencies
3. As last resort, reinstall: `install.bat`

**GPU not detected**

1. Ensure you have NVIDIA GPU (RTX/GTX series)
2. Install latest NVIDIA drivers
3. Run `smart_update.bat` → "Switch to GPU"
4. Check: `python -c "import torch; print(torch.cuda.is_available())"`

### ❓ Performance Problems

**Application works slowly**

1. Check available memory: should be 2+ GB free
2. Check GPU: `python system_check.py`
3. Close other programs (especially browser)
4. Use SSD instead of HDD
5. Reduce `CLIP_BATCH_SIZE` in `config.py` file

**Memory runs out during indexing**

Application automatically:

- Shows warning when memory is low
- Reduces size of processed chunks
- Saves progress for recovery
- Suggests interruption at critical shortage

**First launch takes long**

- This is normal: CLIP model is being downloaded (~500 MB)
- Happens only on first launch
- Ensure stable internet connection

### ❓ Interface Problems

**Search results display incorrectly**

1. Ensure you're using current version with Treeview interface
2. Try resizing window
3. Check correct tkinter version is installed
4. Restart application

**Result scrolling doesn't work**

1. Use mouse wheel for scrolling
2. Click on results for focus
3. Use arrow keys on keyboard
4. Try column sorting

**Thumbnails don't load**

1. Check file formats (supported: JPG, PNG)
2. Ensure files are not corrupted
3. Check access rights to image folder
4. Clear cache and recreate index

### ❓ Search Problems

**Can't find photos**

1. Check supported formats: only JPG and PNG
2. Ensure index is built for selected folder
3. Try more specific queries:
   - Instead of "car" → "red car"
   - Instead of "animal" → "cat" or "dog"
4. Check "Photos from last days" setting

**Search results are inaccurate**

1. Use more descriptive queries
2. Specify details: color, size, action
3. Try synonyms: "cat" / "kitten", "children" / "child"
4. CLIP model understands objects better than abstract concepts

### ❓ Saving Problems

**Error when saving selected photos**

1. Check access rights to destination folder
2. Ensure sufficient disk space
3. Check that source files are not locked by other programs
4. Try different destination folder

**Files saved to wrong folder**

- Date organization creates subfolders in YYYY-MM format
- Check image EXIF data
- File modification date used when EXIF is missing

## 💻 Useful Commands and Tools

### 🔍 System Diagnostics

```batch
# Full system readiness diagnostics
python system_check.py

# Check Python version
python --version

# Check available memory
python -c "import psutil; print(f'Available: {psutil.virtual_memory().available/1024**3:.1f} GB')"

# Check GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check CLIP model
python -c "import sentence_transformers; print('CLIP model OK')"
```

### 🚀 Launch and Management

```batch
# Recommended launch methods
start_app.bat
run.bat

# Alternative methods
python main.py

# Installation and updates
install.bat                    # New installation
smart_update.bat              # Smart update (preserves settings)
```

### 🛠️ Configuration and Maintenance

```batch
# Configure GPU acceleration
python gpu_setup.py

# Clear cache
rmdir /s cache
mkdir cache

# Check application file integrity
dir /b *.py | find /c /v ""   # Count Python files
```

### 📂 Application Hotkeys

| Key      | Action                         |
| -------- | ------------------------------ |
| `Ctrl+O` | Select image folder            |
| `Ctrl+F` | Go to search field             |
| `Enter`  | Start search (in search field) |
| `F5`     | Rebuild index                  |
| `Space`  | Select/deselect item           |
| `Enter`  | Open selected image            |
| `↑↓`     | Navigate through results       |
| `Ctrl+A` | Select all results             |

## 📁 File Structure After Installation

```
📁 Your application folder/
├── 📄 start_app.bat          # Quick launch ⭐
├── 📄 run.bat               # Alternative launch
├── 📄 install.bat           # Installer ⭐
├── 📄 smart_update.bat      # Smart update ⭐
├── 📄 system_check.py       # System diagnostics ⭐
├── 📄 main.py              # Main application
├── 📄 config.py            # Application settings
├── 📄 requirements.txt     # Dependencies list
├── 📁 ui/                  # Interface modules
│   ├── results_panel.py    # Modern results interface
│   ├── dialogs.py         # Application dialogs
│   ├── search_options.py  # Search settings panel
│   └── ...                # Other UI components
├── 📁 .venv/              # Python virtual environment
├── 📁 cache/              # Index and embedding cache
│   ├── image_embeddings.pkl
│   └── metadata.pkl
├── 📁 reports/            # Documentation
│   ├── USER_GUIDE.md      # This guide
│   ├── manual_install.md  # Manual installation
│   └── ...               # Other guides
├── 📄 image_search.log    # Application logs
├── 📄 installation_info.txt # Installation info
└── 📄 update_info.txt     # Update information
```

## 🎯 Usage Examples

### Family Photo Search

```
"family photo"         → Find group family shots
"children playing"     → Photos of playing children
"birthday"            → Holiday photos with cake
"new year"            → New Year and Christmas photos
"vacation at sea"     → Beach photographs
"pets"                → Pet photos
```

### Object Search

```
"cat"                 → Images with cats
"dog outdoors"        → Dogs on walks
"red car"             → Red colored automobiles
"flowers in garden"   → Garden and field flowers
"sunset"              → Sunset/sunrise photos
"food on table"       → Culinary photos
```

### Activity Search

```
"sports"              → Sports events
"dancing"             → Dance photos
"swimming"            → Water activities
"picnic"              → Outdoor dining
"fishing"             → Fishing photos
"cooking"             → Food preparation process
```

## 🆘 Contacts and Support

### When problems occur:

1. **Try first**:

   - Run diagnostics: `python system_check.py`
   - Restart application
   - Check logs in `image_search.log` file

2. **If that doesn't help**:

   - Run smart update: `smart_update.bat`
   - Or full reinstallation: `install.bat`

3. **For specific problems**:
   - Study documentation in `reports/` folder
   - Check `REFACTORING_SUMMARY.md` file for change information

### 📊 System Requirements

**Minimum requirements:**

- Windows 10/11
- Python 3.8+
- 4 GB RAM (2+ GB free)
- 2 GB free disk space
- Internet for initial model download

**Recommended requirements:**

- Windows 10/11
- Python 3.9+
- 8+ GB RAM (4+ GB free)
- SSD drive
- NVIDIA GPU (RTX/GTX series)
- Stable internet connection

---

_Application developed for convenient search in family photo archives. All data is processed locally on your computer and is not transmitted anywhere._

**Guide version**: August 2025 | **Compatibility**: Windows 10/11, Python 3.8+
