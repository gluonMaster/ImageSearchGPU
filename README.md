# Image Search Application by Description

GUI application for searching images in family archives using natural language descriptions powered by CLIP technology.

## Features

- 🔍 **Smart Search**: Find images using natural language descriptions in Russian
- 🚀 **Fast Performance**: Cache analysis results for instant repeated searches
- 📁 **Mass Processing**: Analyze up to 70,000+ images without memory crashes
- 🧠 **Smart Memory Management**: Automatic chunking and resource monitoring
- 🔄 **Crash Recovery**: Resume interrupted indexing from the last chunk
- 🎯 **Accurate Results**: Relevance sorting with similarity coefficients display
- 📅 **Filtering**: Search among photos from specific time periods
- 🖼️ **Convenient Viewing**: Image thumbnails in modern tabular interface
- 📊 **Enhanced Navigation**: New Treeview-based interface with column sorting
- ⚙️ **Flexible Settings**: Configure result count and other parameters
- 💾 **Organized Saving**: Save selected photos with automatic date-based organization
- 🔧 **Optimized Scrolling**: Eliminated Canvas limitations for large collections

## New Feature: Photo Saving

🆕 **Automatic Date Organization**: You can now select found photos and save them to a specified folder. The application automatically:

- ✅ Creates subfolders in `YYYY-MM` format (e.g., `2020-03`, `2020-07`)
- ✅ Organizes photos by creation date from EXIF data
- ✅ Shows preview of file organization
- ✅ Provides progress bar for large collections
- ✅ Prevents overwriting existing files

### Organization Example:

```
Selected_folder/
├── 2020-03/
│   ├── IMG_1234.jpg (11.03.2020)
│   └── IMG_1235.jpg (16.03.2020)
└── 2020-07/
    └── IMG_1236.jpg (21.07.2020)
```

## 🚀 New Features: Modern Interface and Optimization

🆕 **Completely updated search results interface**:

### ⚡ Key Improvements:

- ✅ **New Tabular Interface**: Replaced Canvas with modern Treeview
- ✅ **Eliminated Scrolling Limitations**: No more element count limits
- ✅ **Result Sorting**: Click column headers to sort
- ✅ **Enhanced Navigation**: Columns with similarity, size, date information
- ✅ **Keyboard Control**: Space to select, Enter to open
- ✅ **Optimized Performance**: Thumbnail caching and batch loading

## 🚀 New Feature: Large Collection Optimization

🆕 **Processing huge archives without crashes**: The application can now stably process collections up to **70,000+ images** without memory errors!

### ⚡ Key Capabilities:

- ✅ **Smart Memory Management**: Automatic monitoring and overflow prevention
- ✅ **Chunk Processing**: Break large tasks into manageable parts (5000 images each)
- ✅ **Crash Recovery**: Continue from last processed chunk on interruption
- ✅ **Adaptive Chunk Size**: Automatic reduction when memory is low
- ✅ **Detailed Progress**: "Chunk 3 of 14 (15000/70000 images)"
- ✅ **Intermediate Saving**: Results saved after each chunk

### 📊 Performance After Optimization:

| Image Count | Processing Time | Memory Requirements | Status    |
| ----------- | --------------- | ------------------- | --------- |
| 8,000       | ~15 minutes     | 2+ GB free          | ✅ Stable |
| 25,000      | ~45 minutes     | 4+ GB free          | ✅ Stable |
| 70,000      | ~2.5 hours      | 6+ GB free          | ✅ Stable |

### 🔧 Automatic Crash Protection:

- **Warning** when < 2 GB free memory
- **Automatic cancellation** when < 1 GB memory
- **Smart chunk reduction** when resources are low
- **Forced memory cleanup** between chunks

### 🔄 Updating Existing Installations:

If you already have the system deployed, update it to get new features:

```bash
# Automatic update (recommended)
update_dependencies.bat

# Or through existing GPU script
setup_gpu.bat
```

## Supported Formats

- JPG/JPEG
- PNG

## GPU Support (RTX 2060 and others)

The application automatically uses GPU when available, providing **significant acceleration**:

### 🚀 GPU Benefits:

- **Image Analysis**: 3-10 times faster
- **Large Archive Indexing**: minutes instead of hours
- **Batch Processing**: optimized for GPU memory

### ⚙️ RTX 2060 Setup:

1. **Automatic Setup**:

   ```bash
   # Run GPU setup script
   setup_gpu.bat
   ```

2. **Manual Setup**:

   ```bash
   # Reinstall PyTorch with CUDA
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Check Operation**:
   ```bash
   python gpu_setup.py
   ```

### 📊 Expected Performance:

- **CPU (Intel/AMD)**: ~1000 images in 10-15 minutes
- **RTX 2060**: ~1000 images in 2-3 minutes
- **Large archives (10k+ photos)**: 5-8x acceleration

The application automatically detects GPU availability and selects optimal settings.

## Quick Installation and Launch

### 🚀 Universal Installation (Recommended)

**New unified installer** - the simplest setup method:

1. **Download all files** to a separate folder
2. **Run `install.bat`** by double-clicking
3. **Choose installation type**:
   - CPU only (works everywhere)
   - GPU CUDA (for NVIDIA cards)
   - Automatic detection (recommended)
4. **Wait for completion** - everything will be configured automatically!

The installer will:

- ✅ Check system and Python
- ✅ Create virtual environment
- ✅ Detect NVIDIA GPU presence
- ✅ Install correct PyTorch versions
- ✅ Configure memory optimization
- ✅ Create quick launch script
- ✅ Perform full diagnostics

### 🔄 Updating Existing Installations

If the application is already installed, use:

```batch
# Smart update preserving settings
smart_update.bat

# Or old method
update_dependencies.bat
```

### 🔍 System Diagnostics

To check system readiness:

```batch
python system_check.py
```

### 📊 Installation Method Comparison

| Method              | Simplicity | Flexibility | Automation |
| ------------------- | ---------- | ----------- | ---------- |
| `install.bat`       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐    | ⭐⭐⭐⭐⭐ |
| `smart_update.bat`  | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐   |
| Manual installation | ⭐⭐       | ⭐⭐⭐⭐⭐  | ⭐         |

### Automatic Installation (Legacy Method)

For backward compatibility, the old method is preserved:

1. **Download all files** to a separate folder
2. **Run `install_and_run.bat`** by double-clicking
3. **Wait** for dependency installation completion (may take 5-10 minutes)
4. **Application will start automatically**

### Manual Installation

If automatic installation doesn't work:

1. **Install Python 3.8+** from [python.org](https://python.org)

   - Make sure to check "Add Python to PATH" during installation

2. **Open command prompt** in the application folder

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Usage Instructions

### First Launch

1. **Select folder** with images via "Browse..." button or "File → Select Folder" menu

2. **Build index** by clicking "Build Index" button

   - On first launch, CLIP model will be downloaded (~500 MB)
   - Image analysis will take time depending on their quantity
   - Results are cached for fast reuse

3. **Start searching!** Enter description in search field and click "Find"

### Search Query Examples

- `cat` - find images with cats
- `dog outdoors` - dogs outside
- `sunset` - sunset photos
- `family photo` - family photographs
- `birthday` - birthday photos
- `beach` - beach photos
- `children playing` - playing children
- `new year` - New Year photos

### Search Settings

- **Max results** - limit number of found images (1-100)
- **Photos from last days** - search only among recent photos (0 = all photos)

### Working with Results

- **Tabular interface** with columns: Photo, Similarity, Size, Modified Date, Path
- **Column sorting** - click headers to sort data
- **Image thumbnails** displayed directly in main column
- **Relevance sorting** - most suitable images shown first
- **Similarity coefficient** displayed for each result
- **Image selection** - click to select/deselect, Space key on keyboard
- **"Open" button** - opens image in default program (or Enter)
- **"Open folder" button** - opens file folder in explorer
- **Keyboard navigation** - arrows to move, Space/Enter for actions

### 🆕 Saving Selected Photos

1. **Select photos**: Check boxes next to desired images in search results

2. **Use control buttons**:

   - `Select All` - select all found photos
   - `Clear Selection` - deselect all photos

3. **Save selected photos**:

   - Click `Save Selected...` button
   - Choose destination folder
   - Preview file organization
   - Confirm saving

4. **Automatic organization**:

   - Photos will be organized into subfolders by creation date
   - Folder format: `YYYY-MM` (e.g., `2020-03`, `2021-12`)
   - Date taken from photo EXIF data or file modification date
   - If file with same name exists, suffix `_(<number>)` is added

5. **Progress tracking**:
   - Progress bar displayed during saving
   - Detailed statistics shown on completion
   - Option to immediately open folder with saved photos

### Photo Saving Usage Example

Suppose you found photos by query "birthday" and selected 5 photos:

- `IMG_1234.jpg` (created 21.07.2020)
- `IMG_1235.jpg` (created 11.03.2020)
- `IMG_1236.jpg` (created 16.03.2020)
- `IMG_1237.jpg` (created 05.12.2021)
- `IMG_1238.jpg` (created 15.12.2021)

After saving to folder `D:\My_Photos\Birthday`, this structure will be created:

```
D:\My_Photos\Birthday\
├── 2020-03\
│   ├── IMG_1235.jpg
│   └── IMG_1236.jpg
├── 2020-07\
│   └── IMG_1234.jpg
└── 2021-12\
    ├── IMG_1237.jpg
    └── IMG_1238.jpg
```

## Application File Structure

```
image-search-app/
├── main.py                 # Main application file
├── config.py              # Application settings
├── image_analyzer.py      # CLIP image analysis
├── cache_manager.py       # Cache management
├── file_scanner.py        # File scanning
├── search_engine.py       # Search engine
├── photo_saver.py         # Photo saving with date organization
├── gpu_setup.py           # GPU support setup
├── debug_scanner.py       # Scanning debugging
├── system_check.py        # System diagnostics
├── gui_components.py      # Base GUI components (legacy)
├── requirements.txt       # Python dependencies
├── install.bat           # New universal installer
├── smart_update.bat      # Smart update
├── run.bat               # Quick launch (Windows)
├── REFACTORING_SUMMARY.md # Interface changes description
├── ui/                   # 🆕 Modular UI architecture
│   ├── __init__.py       # UI component exports
│   ├── results_panel.py  # Modern results interface (Treeview)
│   ├── dialogs.py        # Dialogs: photo preview, folder selection
│   ├── search_options.py # Search settings panel
│   ├── progress_dialog.py# Operation progress dialog
│   └── alternative_results_panel.py # Alternative implementation
├── cache/                # Embeddings cache folder
│   ├── image_embeddings.pkl
│   └── metadata.pkl
└── reports/              # Documentation and guides
    ├── USER_GUIDE.md
    ├── QUICK_GUIDE.md
    └── (other guides...)
```

## Hotkeys

- **Ctrl+O** - select folder
- **Ctrl+F** - focus on search field
- **Enter** in search field - start search
- **F5** - rebuild index

## Application Menu

### File

- **Select Folder** - choose folder with images
- **Clear Cache** - delete all cached data
- **Exit** - close application

### View

- **Update Index** - force index rebuild
- **Statistics** - index and cache information

### Help

- **About** - application information

## Troubleshooting

### Application Won't Start

1. **Check Python**: open command prompt and run `python --version`
2. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
3. **Check logs** in `image_search.log` file

### Slow Performance

1. **Use SSD** for cache and images
2. **Increase RAM** - application uses memory for caching
3. **With NVIDIA GPU** uncomment torch-audio in requirements.txt
4. **New results interface** automatically optimizes large list display

### Result Scrolling Issues

1. **Update to new version** - old versions had Canvas limitations
2. **Use mouse wheel** - new Treeview interface supports smooth scrolling
3. **Try sorting** - click column headers to change order

### Image Analysis Errors

1. **Check file formats** - only JPG and PNG supported
2. **Ensure image integrity** - corrupted files are skipped
3. **Check access rights** to image folder

### Running Out of Memory

1. **Reduce CLIP_BATCH_SIZE** in config.py (e.g., to 16)
2. **Analyze images in parts** - select subfolders separately
3. **Clear cache** when switching to new folder

## Technical Details

### Used Libraries

- **sentence-transformers** - CLIP model for image analysis
- **torch/torchvision** - machine learning
- **Pillow** - image processing
- **tkinter** - graphical interface (base elements)
- **ttk.Treeview** - modern tabular interface for results
- **numpy** - computations

### How It Works

1. **Image Analysis**: CLIP model creates vector representations (embeddings) of images
2. **Caching**: embeddings are saved to disk for fast access
3. **Search**: text query is converted to embedding and compared with image embeddings
4. **Ranking**: results are sorted by cosine similarity
5. **Display**: modern Treeview interface provides fast scrolling and sorting

### Configuration

Main settings can be changed in `config.py` file:

- **CLIP_MODEL_NAME** - CLIP model used
- **THUMBNAIL_SIZE** - thumbnail size
- **MAX_RESULTS_DEFAULT** - default result count
- **SIMILARITY_THRESHOLD** - minimum similarity threshold

## Updates and Support

The application logs its operation to `image_search.log` file. When issues occur, check this file for detailed error information.

**New Results Interface**: The application uses modern Treeview instead of Canvas, eliminating element count limitations and improving scrolling performance.

The application is developed for Windows and tested with family archives up to 70,000+ images with the new optimized architecture.

---

**Enjoy using! 🎉**
