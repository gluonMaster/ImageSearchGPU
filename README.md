# ImageSearchGPU

A desktop application for searching local photo collections with natural-language descriptions. It uses CLIP embeddings through Sentence Transformers, a Tkinter interface, and optional NVIDIA GPU acceleration.

The project addresses a practical problem: finding a photo by its contents when filenames and folders are not enough.

## Features

- Index JPEG and PNG images from selected folders.
- Rank images by similarity to a text query and display thumbnails and file details.
- Reuse cached embeddings for subsequent searches.
- Process indexing work in chunks, with progress reporting and memory checks.
- Filter results by recency and limit the number of matches.
- Copy selected photos into date-based folders, adding a suffix when a filename already exists.

## Getting started on Windows

Use Python with pip and Tkinter, in a version supported by your chosen PyTorch and Sentence Transformers releases. Current upstream guidance recommends Python 3.10 or later; consult the [Sentence Transformers installation guide](https://www.sbert.net/docs/installation.html) and [PyTorch installation selector](https://pytorch.org/get-started/locally/) for compatible packages.

From PowerShell in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

The first model load requires an internet connection to download model files. Subsequent indexing and similarity calculations run locally using the downloaded model.

Start with a small folder of non-sensitive sample images before indexing a large archive. Dependencies use minimum versions rather than a fully pinned environment, so compatibility with every newer dependency release is not guaranteed.

### Optional GPU setup

Install a CUDA-enabled PyTorch build compatible with your Python version, GPU, and driver using the [official installation selector](https://pytorch.org/get-started/locally/). Run its installation command with the virtual environment's Python executable.

Check CUDA availability without starting the application:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

The application uses CUDA when available and otherwise falls back to CPU. Throughput and memory requirements depend on hardware, image sizes, and configuration; there is no fixed collection-size or speed guarantee.

### Windows helper scripts

| File | Purpose |
| --- | --- |
| [install.bat](install.bat) | Interactive CPU/GPU installer; creates a `start_app.bat` launcher. |
| [smart_update.bat](smart_update.bat) | Interactive dependency updates for an existing environment. |
| [run.bat](run.bat) | Activates `venv` if present, otherwise uses the current Python environment. For `.venv`, use the explicit command above or the generated launcher. |
| [system_check.py](system_check.py) | Interactive environment diagnostics. |
| [gpu_setup.py](gpu_setup.py) | Interactive GPU helper that can reinstall PyTorch after confirmation. |

The helper scripts contain legacy CUDA 11.8 installation commands. Prefer the upstream selector for a current GPU environment. These scripts are interactive, not unattended installers.

## Basic workflow

1. Choose the folders to search and build an index.
2. Enter a short description, such as `cat on a sofa` or `sunset at the beach`.
3. Inspect the ranked results, adjust the result limit or recency filter, and open matching images.
4. Optionally select photos and copy them to an output folder. Copies are grouped by EXIF date, falling back to file modification time.

Search quality depends on the selected model and query language. Similarity scores are rankings, not calibrated probabilities.

## How it works

`file_scanner.py` discovers images. `image_analyzer.py` encodes images and text with the model selected in `config.py`. `cache_manager.py` stores embeddings and metadata, while `search_engine.py` coordinates indexing and search. The `ui/` modules display results, and `photo_saver.py` copies selected files.

## Configuration

The main settings are in [config.py](config.py):

| Setting | Default / purpose |
| --- | --- |
| `CLIP_MODEL_NAME` | `clip-ViT-B-32` |
| `CHUNK_SIZE` | 1,000 images per indexing chunk |
| `CLIP_BATCH_SIZE_CPU` / `CLIP_BATCH_SIZE_GPU` | 8 / 32 images per model batch |
| `MAX_RESULTS_DEFAULT` | 20 results |
| `SIMILARITY_THRESHOLD` | 0.1 |
| `WARNING_MEMORY_GB` / `MIN_MEMORY_GB` | 2 GB warning / 1 GB cancellation threshold |

Chunk size and model batch size serve different purposes. Reduce batch size when model inference runs out of memory; begin with smaller input folders when diagnosing indexing problems.

## Local data

Keep personal photos and exported results outside the repository. The application stores embeddings, metadata, and selected-folder information under `cache/` and writes `image_search.log`. These can contain local filenames and paths and are excluded from Git.

Use only cache files created by your own trusted installation: the cache format uses Python pickle. Rebuild the cache instead of importing an untrusted cache file.

## Troubleshooting and further reading

- Launch with the same virtual environment used to install dependencies.
- For import errors, check package compatibility before changing the global Python installation.
- For GPU issues, check `torch.cuda.is_available()` and the installed PyTorch build.
- For indexing errors, inspect `image_search.log`, file permissions, and whether the input files are valid JPEG/PNG images.
- The [English user guide](reports/USER_GUIDE_EN.md) and [Russian user guide](reports/USER_GUIDE.md) provide more interface details. Older helper instructions in these guides may differ from the setup instructions above.
