# ImageSearchGPU

Find photos in a local archive by describing them: "cat on a sofa", "sunset at the beach", "children at a birthday party". ImageSearchGPU indexes your folders with the CLIP model and ranks every picture by how well it matches the text. It runs entirely on your own computer; an NVIDIA GPU makes indexing much faster but is not required.

I wrote it for a large family photo archive where file names and folders were no help in finding a particular picture.

## Features

- Indexes JPEG and PNG files in the folders you choose and caches the embeddings, so later searches are instant.
- Ranks images by similarity to a text query and shows thumbnails with file details.
- Filters by recency and limits the number of results.
- Processes big collections in chunks with a progress bar and memory checks.
- Copies selected photos into folders by date (from EXIF, or the file date as a fallback) without overwriting existing files.

## Getting started on Windows

Use a Python version that your PyTorch and Sentence Transformers releases support (3.10 or newer at the time of writing). In PowerShell, from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

The first start downloads the CLIP model; after that, indexing and search work offline. Try a small folder of pictures first before indexing a whole archive. The requirements set minimum versions only, so a very new release of a dependency may need an adjustment.

### GPU

Install a CUDA build of PyTorch that fits your GPU and driver with the [official selector](https://pytorch.org/get-started/locally/), using the virtual environment's Python. To check that it works:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

The app uses CUDA when it is available and falls back to the CPU otherwise.

### Helper scripts

| File | Purpose |
| --- | --- |
| [install.bat](install.bat) | Interactive CPU or GPU install; creates a `start_app.bat` launcher |
| [smart_update.bat](smart_update.bat) | Interactive dependency update |
| [run.bat](run.bat) | Starts the app from `venv` if present, otherwise from the current Python |
| [system_check.py](system_check.py) | Environment diagnostics |
| [gpu_setup.py](gpu_setup.py) | GPU helper that can reinstall PyTorch after asking |

The batch scripts still install the older CUDA 11.8 builds. For a current GPU setup, the PyTorch selector above is the better choice.

## How to use it

1. Choose the folders to search and build the index.
2. Type a short description of the picture you are looking for.
3. Go through the ranked results, change the number of results or the date filter, and open the pictures you want.
4. Optionally select photos and copy them to an output folder, sorted by date.

How well a query works depends on the model and the language of the query; the default model understands English best. The scores rank the results, they are not probabilities.

## How it works

`file_scanner.py` finds the images, `image_analyzer.py` turns images and text into embeddings with the model set in `config.py`, `cache_manager.py` stores the embeddings and metadata, and `search_engine.py` ties indexing and search together. The `ui/` package is the Tkinter interface, and `photo_saver.py` copies the selected files.

The main settings are in [config.py](config.py):

| Setting | Default |
| --- | --- |
| `CLIP_MODEL_NAME` | `clip-ViT-B-32` |
| `CHUNK_SIZE` | 1,000 images per indexing chunk |
| `CLIP_BATCH_SIZE_CPU` / `CLIP_BATCH_SIZE_GPU` | 8 / 32 images per model batch |
| `MAX_RESULTS_DEFAULT` | 20 results |
| `SIMILARITY_THRESHOLD` | 0.1 |
| `WARNING_MEMORY_GB` / `MIN_MEMORY_GB` | warn at 2 GB, stop at 1 GB of free memory |

If the model runs out of memory, lower the batch size; if indexing fails, try a smaller folder first.

## Your photos stay local

Nothing is uploaded. The index lives in `cache/` and the log in `image_search.log`; both contain local file names and paths and are excluded from Git. The cache uses Python pickle, so only load caches created by your own installation and rebuild instead of importing someone else's.

## Troubleshooting

- Start the app with the same virtual environment you installed into.
- For import errors, check package versions before touching the global Python installation.
- For GPU problems, check `torch.cuda.is_available()` and which PyTorch build is installed.
- For indexing errors, look at `image_search.log`, file permissions and whether the files are valid JPEG or PNG images.

The [English user guide](reports/USER_GUIDE_EN.md) and the [Russian user guide](reports/USER_GUIDE.md) describe the interface in more detail; their installation notes are older than this README.

## License

[MIT](LICENSE). Developed by Dr. Konstantin S. Shakun with the help of AI coding agents.
