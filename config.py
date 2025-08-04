"""
Конфигурационный файл приложения для поиска изображений.
Содержит все основные настройки и константы.
"""

import os
from pathlib import Path

# Основные настройки приложения
APP_NAME = "Image Search Assistant"
APP_VERSION = "1.0.0"

# Поддерживаемые форматы изображений
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']

# Настройки CLIP модели
CLIP_MODEL_NAME = "clip-ViT-B-32"  # Модель для анализа изображений
CLIP_BATCH_SIZE = 32  # Размер батча по умолчанию (уменьшен для экономии памяти)
CLIP_BATCH_SIZE_CPU = 8  # Размер батча для CPU (уменьшен)
CLIP_BATCH_SIZE_GPU = 32  # Размер батча для GPU (уменьшен)

# Настройки кэширования
CACHE_DIR = Path("cache")  # Папка для кэша
CACHE_FILE = CACHE_DIR / "image_embeddings.pkl"  # Файл кэша эмбеддингов
METADATA_CACHE_FILE = CACHE_DIR / "metadata.pkl"  # Файл кэша метаданных

# Настройки интерфейса
THUMBNAIL_SIZE = (150, 150)  # Размер миниатюр в результатах поиска
MAX_RESULTS_DEFAULT = 20  # Количество результатов по умолчанию
MAX_RESULTS_LIMIT = 100  # Максимальное количество результатов

# Настройки окна приложения
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Настройки поиска
SIMILARITY_THRESHOLD = 0.1  # Минимальный порог схожести для результатов
SEARCH_TIMEOUT = 30  # Таймаут поиска в секундах

# Настройки обработки больших объемов изображений
CHUNK_SIZE = 1000  # Размер чанка для обработки изображений (уменьшен для экономии памяти)
MIN_MEMORY_GB = 1.0  # Минимальная память для отмены операции (ГБ)
WARNING_MEMORY_GB = 2.0  # Память для показа предупреждения (ГБ)
AUTO_REDUCE_CHUNK_FACTOR = 0.5  # Коэффициент уменьшения чанка при нехватке памяти

# Настройки множественного выбора папок
MAX_SELECTED_FOLDERS = 50  # Максимальное количество папок для выбора
SAVE_LAST_FOLDERS = True  # Сохранять последние выбранные папки
LAST_FOLDERS_FILE = CACHE_DIR / "last_folders.pkl"  # Файл с последними папками
DEFAULT_RECURSIVE_SEARCH = True  # Рекурсивный поиск по умолчанию

# Создание необходимых директорий
CACHE_DIR.mkdir(exist_ok=True)

# Цвета интерфейса
COLORS = {
    'bg_primary': '#f0f0f0',
    'bg_secondary': '#ffffff',
    'accent': '#007acc',
    'text_primary': '#333333',
    'text_secondary': '#666666',
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545'
}

# Шрифты
FONTS = {
    'default': ('Segoe UI', 9),
    'header': ('Segoe UI', 12, 'bold'),
    'small': ('Segoe UI', 8)
}