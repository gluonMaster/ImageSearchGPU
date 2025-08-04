"""
Модуль для управления кэшированием эмбеддингов изображений.
Обеспечивает сохранение и загрузку результатов анализа для ускорения повторных поисков.
"""

import pickle
import numpy as np
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import hashlib

from config import CACHE_FILE, METADATA_CACHE_FILE

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Класс для управления кэшем эмбеддингов изображений и метаданных.
    Обеспечивает быстрый доступ к ранее обработанным данным.
    """
    
    def __init__(self):
        """Инициализация менеджера кэша."""
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.metadata_cache: Dict[str, dict] = {}
        self._load_cache()
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        Создание хэша файла для отслеживания изменений.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: MD5 хэш файла
        """
        try:
            stat = os.stat(file_path)
            # Используем размер и время модификации для создания хэша
            hash_string = f"{file_path}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(hash_string.encode()).hexdigest()
        except OSError:
            return ""
    
    def _load_cache(self) -> None:
        """Загрузка кэша из файлов."""
        try:
            # Загрузка эмбеддингов
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(f"Загружено {len(self.embeddings_cache)} эмбеддингов из кэша")
            
            # Загрузка метаданных
            if METADATA_CACHE_FILE.exists():
                with open(METADATA_CACHE_FILE, 'rb') as f:
                    self.metadata_cache = pickle.load(f)
                logger.info(f"Загружено {len(self.metadata_cache)} записей метаданных")
                
        except Exception as e:
            logger.warning(f"Ошибка при загрузке кэша: {e}")
            self.embeddings_cache = {}
            self.metadata_cache = {}
    
    def save_cache(self) -> None:
        """Сохранение кэша в файлы."""
        try:
            # Создание директории если не существует
            CACHE_FILE.parent.mkdir(exist_ok=True)
            
            # Сохранение эмбеддингов
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            
            # Сохранение метаданных
            with open(METADATA_CACHE_FILE, 'wb') as f:
                pickle.dump(self.metadata_cache, f)
            
            logger.info("Кэш успешно сохранен")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении кэша: {e}")
    
    def get_cached_embedding(self, file_path: str) -> Optional[np.ndarray]:
        """
        Получение эмбеддинга из кэша.
        
        Args:
            file_path: Путь к файлу изображения
            
        Returns:
            Optional[np.ndarray]: Эмбеддинг если найден в кэше, None иначе
        """
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return None
        
        # Проверяем актуальность кэша
        if file_path in self.metadata_cache:
            cached_hash = self.metadata_cache[file_path].get('file_hash', '')
            if cached_hash == file_hash and file_path in self.embeddings_cache:
                return self.embeddings_cache[file_path]
        
        return None
    
    def cache_embedding(self, file_path: str, embedding: np.ndarray) -> None:
        """
        Сохранение эмбеддинга в кэш.
        
        Args:
            file_path: Путь к файлу изображения
            embedding: Эмбеддинг изображения
        """
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return
        
        self.embeddings_cache[file_path] = embedding
        self.metadata_cache[file_path] = {
            'file_hash': file_hash,
            'cached_at': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
    
    def get_cached_embeddings_for_paths(self, file_paths: List[str]) -> Tuple[Dict[str, np.ndarray], List[str]]:
        """
        Получение кэшированных эмбеддингов для списка путей.
        
        Args:
            file_paths: Список путей к файлам
            
        Returns:
            Tuple[Dict[str, np.ndarray], List[str]]: 
                Словарь с кэшированными эмбеддингами и список некэшированных путей
        """
        cached_embeddings = {}
        uncached_paths = []
        
        for path in file_paths:
            embedding = self.get_cached_embedding(path)
            if embedding is not None:
                cached_embeddings[path] = embedding
            else:
                uncached_paths.append(path)
        
        logger.info(f"Найдено в кэше: {len(cached_embeddings)}, требует обработки: {len(uncached_paths)}")
        return cached_embeddings, uncached_paths
    
    def cache_batch_embeddings(self, embeddings_dict: Dict[str, np.ndarray]) -> None:
        """
        Сохранение множественных эмбеддингов в кэш.
        
        Args:
            embeddings_dict: Словарь с эмбеддингами {путь_к_файлу: эмбеддинг}
        """
        for file_path, embedding in embeddings_dict.items():
            self.cache_embedding(file_path, embedding)
    
    def remove_invalid_cache_entries(self, valid_paths: List[str]) -> None:
        """
        Удаление недействительных записей из кэша.
        
        Args:
            valid_paths: Список действительных путей к файлам
        """
        valid_paths_set = set(valid_paths)
        
        # Удаление недействительных эмбеддингов
        invalid_embeddings = [path for path in self.embeddings_cache.keys() 
                            if path not in valid_paths_set or not os.path.exists(path)]
        
        for path in invalid_embeddings:
            self.embeddings_cache.pop(path, None)
            self.metadata_cache.pop(path, None)
        
        if invalid_embeddings:
            logger.info(f"Удалено {len(invalid_embeddings)} недействительных записей из кэша")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        Получение статистики кэша.
        
        Returns:
            Dict[str, any]: Статистика кэша
        """
        total_size = 0
        oldest_entry = None
        newest_entry = None
        
        for metadata in self.metadata_cache.values():
            if 'file_size' in metadata:
                total_size += metadata['file_size']
            
            if 'cached_at' in metadata:
                cached_at = metadata['cached_at']
                if oldest_entry is None or cached_at < oldest_entry:
                    oldest_entry = cached_at
                if newest_entry is None or cached_at > newest_entry:
                    newest_entry = cached_at
        
        return {
            'total_entries': len(self.embeddings_cache),
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_entry': oldest_entry,
            'newest_entry': newest_entry,
            'cache_file_exists': CACHE_FILE.exists(),
            'metadata_file_exists': METADATA_CACHE_FILE.exists()
        }
    
    def clear_cache(self) -> None:
        """Полная очистка кэша."""
        self.embeddings_cache.clear()
        self.metadata_cache.clear()
        
        # Удаление файлов кэша
        for cache_file in [CACHE_FILE, METADATA_CACHE_FILE]:
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    logger.info(f"Удален файл кэша: {cache_file}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении файла кэша {cache_file}: {e}")
        
        logger.info("Кэш полностью очищен")
    
    def save_chunk_progress(self, directory_path: str, processed_chunks: int, total_chunks: int, 
                           processed_files: List[str]) -> None:
        """
        Сохранение прогресса обработки чанков.
        
        Args:
            directory_path: Путь к обрабатываемой директории
            processed_chunks: Количество обработанных чанков
            total_chunks: Общее количество чанков
            processed_files: Список уже обработанных файлов
        """
        progress_file = CACHE_FILE.parent / f"progress_{hashlib.md5(directory_path.encode()).hexdigest()}.pkl"
        
        progress_data = {
            'directory_path': directory_path,
            'processed_chunks': processed_chunks,
            'total_chunks': total_chunks,
            'processed_files': processed_files,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(progress_file, 'wb') as f:
                pickle.dump(progress_data, f)
            logger.info(f"Сохранен прогресс: {processed_chunks}/{total_chunks} чанков")
        except Exception as e:
            logger.error(f"Ошибка при сохранении прогресса: {e}")
    
    def load_chunk_progress(self, directory_path: str) -> Optional[dict]:
        """
        Загрузка сохраненного прогресса обработки чанков.
        
        Args:
            directory_path: Путь к обрабатываемой директории
            
        Returns:
            Optional[dict]: Данные о прогрессе или None
        """
        progress_file = CACHE_FILE.parent / f"progress_{hashlib.md5(directory_path.encode()).hexdigest()}.pkl"
        
        if not progress_file.exists():
            return None
        
        try:
            with open(progress_file, 'rb') as f:
                progress_data = pickle.load(f)
            logger.info(f"Загружен прогресс: {progress_data['processed_chunks']}/{progress_data['total_chunks']} чанков")
            return progress_data
        except Exception as e:
            logger.error(f"Ошибка при загрузке прогресса: {e}")
            return None
    
    def clear_chunk_progress(self, directory_path: str) -> None:
        """
        Очистка сохраненного прогресса для директории.
        
        Args:
            directory_path: Путь к директории
        """
        progress_file = CACHE_FILE.parent / f"progress_{hashlib.md5(directory_path.encode()).hexdigest()}.pkl"
        
        if progress_file.exists():
            try:
                progress_file.unlink()
                logger.info("Прогресс чанков очищен")
            except Exception as e:
                logger.error(f"Ошибка при очистке прогресса: {e}")
    
    def get_processed_files_from_chunks(self, processed_files: List[str]) -> set:
        """
        Получение множества уже обработанных файлов.
        
        Args:
            processed_files: Список обработанных файлов
            
        Returns:
            set: Множество обработанных файлов
        """
        return set(processed_files)
    
    def save_multiple_folders_config(self, folder_paths: List[str], recursive: bool = True) -> None:
        """
        Сохранение конфигурации множественных папок.
        
        Args:
            folder_paths: Список путей к папкам
            recursive: Рекурсивный поиск
        """
        from config import LAST_FOLDERS_FILE, SAVE_LAST_FOLDERS
        
        if not SAVE_LAST_FOLDERS:
            return
        
        try:
            config_data = {
                'folder_paths': folder_paths,
                'recursive': recursive,
                'saved_at': datetime.now().isoformat()
            }
            
            LAST_FOLDERS_FILE.parent.mkdir(exist_ok=True)
            with open(LAST_FOLDERS_FILE, 'wb') as f:
                pickle.dump(config_data, f)
            
            logger.info(f"Сохранена конфигурация для {len(folder_paths)} папок")
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации папок: {e}")
    
    def load_multiple_folders_config(self) -> Optional[dict]:
        """
        Загрузка сохраненной конфигурации множественных папок.
        
        Returns:
            Optional[dict]: Конфигурация папок или None
        """
        from config import LAST_FOLDERS_FILE, SAVE_LAST_FOLDERS
        
        if not SAVE_LAST_FOLDERS or not LAST_FOLDERS_FILE.exists():
            return None
        
        try:
            with open(LAST_FOLDERS_FILE, 'rb') as f:
                config_data = pickle.load(f)
            
            # Проверяем существование папок
            existing_folders = []
            for folder_path in config_data.get('folder_paths', []):
                if os.path.exists(folder_path):
                    existing_folders.append(folder_path)
            
            if existing_folders:
                config_data['folder_paths'] = existing_folders
                logger.info(f"Загружена конфигурация для {len(existing_folders)} папок")
                return config_data
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации папок: {e}")
        
        return None
    
    def get_folders_cache_key(self, folder_paths: List[str]) -> str:
        """
        Создание ключа кэша для множественных папок.
        
        Args:
            folder_paths: Список путей к папкам
            
        Returns:
            str: Ключ кэша
        """
        sorted_paths = sorted(folder_paths)
        combined_path = "|".join(sorted_paths)
        return hashlib.md5(combined_path.encode()).hexdigest()
    
    def clean_old_progress_files(self, max_age_days: int = 7) -> None:
        """
        Очистка старых файлов прогресса.
        
        Args:
            max_age_days: Максимальный возраст файлов в днях
        """
        try:
            cache_dir = CACHE_FILE.parent
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            
            for file_path in cache_dir.glob("progress_*.pkl"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Удален старый файл прогресса: {file_path.name}")
        
        except Exception as e:
            logger.error(f"Ошибка при очистке старых файлов прогресса: {e}")