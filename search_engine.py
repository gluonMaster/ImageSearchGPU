"""
Основной поисковый движок для поиска изображений по текстовому описанию.
Объединяет функциональность анализа изображений, кэширования и сканирования файлов.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
import logging
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import psutil
import time
import os
from datetime import datetime

from image_analyzer import ImageAnalyzer
from cache_manager import CacheManager
from file_scanner import FileScanner
from config import (SIMILARITY_THRESHOLD, MAX_RESULTS_DEFAULT, CHUNK_SIZE, 
                   MIN_MEMORY_GB, WARNING_MEMORY_GB, AUTO_REDUCE_CHUNK_FACTOR)

logger = logging.getLogger(__name__)

class SearchResult:
    """Класс для представления результата поиска."""
    
    def __init__(self, file_path: str, similarity_score: float, file_info: dict):
        """
        Инициализация результата поиска.
        
        Args:
            file_path: Путь к файлу изображения
            similarity_score: Коэффициент схожести с запросом (0.0 - 1.0)
            file_info: Информация о файле
        """
        self.file_path = file_path
        self.similarity_score = similarity_score
        self.file_info = file_info
    
    def __repr__(self):
        return f"SearchResult(path='{self.file_path}', score={self.similarity_score:.3f})"

class SearchEngine:
    """
    Основной класс поискового движка.
    Управляет процессом поиска изображений по текстовому описанию.
    """
    
    def __init__(self):
        """Инициализация поискового движка."""
        self.image_analyzer = ImageAnalyzer()
        self.cache_manager = CacheManager()
        self.file_scanner = FileScanner()
        
        # Текущие данные для поиска
        self.current_embeddings: Dict[str, np.ndarray] = {}
        self.current_file_paths: List[str] = []
        self.is_index_built = False
        
        # Блокировка для thread-safe операций
        self._lock = threading.Lock()
    
    def _check_memory_status(self) -> Tuple[float, bool, str]:
        """
        Проверка состояния доступной памяти.
        
        Returns:
            Tuple[float, bool, str]: (доступная_память_ГБ, можно_продолжать, сообщение)
        """
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < MIN_MEMORY_GB:
                return available_gb, False, f"Критически мало памяти: {available_gb:.1f} ГБ. Операция отменена."
            elif available_gb < WARNING_MEMORY_GB:
                return available_gb, True, f"Предупреждение: мало памяти ({available_gb:.1f} ГБ). Рекомендуется освободить память."
            else:
                return available_gb, True, f"Доступная память: {available_gb:.1f} ГБ"
        except Exception as e:
            logger.warning(f"Не удалось проверить память: {e}")
            return 0.0, True, "Не удалось проверить память"
    
    def _calculate_optimal_chunk_size(self, total_files: int, available_memory_gb: float) -> int:
        """
        Расчет оптимального размера чанка на основе доступной памяти.
        
        Args:
            total_files: Общее количество файлов
            available_memory_gb: Доступная память в ГБ
            
        Returns:
            int: Оптимальный размер чанка
        """
        base_chunk_size = CHUNK_SIZE
        
        if available_memory_gb < WARNING_MEMORY_GB:
            # Уменьшаем размер чанка при нехватке памяти
            reduction_factor = available_memory_gb / WARNING_MEMORY_GB
            base_chunk_size = int(base_chunk_size * reduction_factor)
        
        # Минимальный размер чанка - 500 файлов
        return max(500, min(base_chunk_size, total_files))
    
    def _force_garbage_collection(self) -> None:
        """Принудительная сборка мусора для освобождения памяти."""
        try:
            gc.collect()
            time.sleep(0.1)  # Небольшая пауза для завершения сборки мусора
        except Exception as e:
            logger.warning(f"Ошибка при сборке мусора: {e}")
    
    def build_index_multiple_folders(self, folder_paths: List[str], 
                                   recursive: bool = True,
                                   date_filter: Optional[dict] = None,
                                   progress_callback: Optional[Callable] = None,
                                   force_rebuild: bool = False) -> bool:
        """
        Построение индекса изображений для множественных директорий.
        
        Args:
            folder_paths: Список путей к директориям с изображениями
            recursive: Рекурсивный поиск в подпапках
            date_filter: Фильтр по дате модификации файлов
            progress_callback: Функция для отслеживания прогресса
            force_rebuild: Принудительная перестройка индекса
            
        Returns:
            bool: True если индекс успешно построен
        """
        try:
            with self._lock:
                logger.info(f"Начало построения индекса для {len(folder_paths)} папок")
                
                # Этап 1: Проверка памяти
                available_memory, can_continue, memory_message = self._check_memory_status()
                logger.info(memory_message)
                
                if not can_continue:
                    if progress_callback:
                        progress_callback(0, 100, memory_message)
                    logger.error(memory_message)
                    return False
                
                if available_memory < WARNING_MEMORY_GB and progress_callback:
                    progress_callback(0, 100, memory_message)
                
                # Этап 2: Сканирование всех папок
                if progress_callback:
                    progress_callback(0, 100, "Сканирование папок...")
                
                all_file_paths = []
                folder_file_mapping = {}  # Маппинг файл -> папка источник
                
                for i, folder_path in enumerate(folder_paths):
                    if not os.path.exists(folder_path):
                        logger.warning(f"Папка не существует: {folder_path}")
                        continue
                    
                    if progress_callback:
                        progress_callback(
                            int((i / len(folder_paths)) * 10), 100, 
                            f"Сканирование папки {i+1}/{len(folder_paths)}: {os.path.basename(folder_path)}"
                        )
                    
                    folder_files = self.file_scanner.scan_directory(
                        folder_path, 
                        recursive=recursive,
                        date_filter=date_filter
                    )
                    
                    # Добавляем файлы и запоминаем их источник
                    for file_path in folder_files:
                        all_file_paths.append(file_path)
                        folder_file_mapping[file_path] = folder_path
                
                if not all_file_paths:
                    logger.warning("Изображения не найдены ни в одной папке")
                    return False
                
                self.current_file_paths = all_file_paths
                # Сохраняем маппинг для использования в результатах поиска
                self.folder_file_mapping = folder_file_mapping
                
                total_files = len(all_file_paths)
                logger.info(f"Найдено {total_files} изображений в {len(folder_paths)} папках")
                
                # Этап 3: Проверка возможности восстановления прогресса
                # Для множественных папок используем объединенный ключ кэша
                cache_key = "|".join(sorted(folder_paths))
                resume_data = None
                if not force_rebuild:
                    resume_data = self.cache_manager.load_chunk_progress(cache_key)
                
                # Этап 4: Расчет размера чанков
                chunk_size = self._calculate_optimal_chunk_size(total_files, available_memory)
                total_chunks = (total_files + chunk_size - 1) // chunk_size
                
                logger.info(f"Обработка {total_files} файлов по {chunk_size} в чанке ({total_chunks} чанков)")
                
                # Этап 5: Загрузка кэшированных эмбеддингов
                if progress_callback:
                    progress_callback(10, 100, "Проверка кэша...")
                
                if not force_rebuild:
                    cached_embeddings, uncached_paths = self.cache_manager.get_cached_embeddings_for_paths(
                        self.current_file_paths
                    )
                    
                    # Очистка недействительных записей кэша
                    self.cache_manager.remove_invalid_cache_entries(self.current_file_paths)
                else:
                    cached_embeddings = {}
                    uncached_paths = self.current_file_paths.copy()
                
                self.current_embeddings = cached_embeddings.copy()
                
                # Этап 6: Определение файлов для обработки с учетом восстановления
                files_to_process = uncached_paths
                start_chunk = 0
                processed_files = []
                
                if resume_data and not force_rebuild:
                    processed_files = resume_data.get('processed_files', [])
                    start_chunk = resume_data.get('last_chunk', 0)
                    
                    # Исключаем уже обработанные файлы
                    files_to_process = [f for f in uncached_paths if f not in processed_files]
                    logger.info(f"Восстановление с чанка {start_chunk}, осталось {len(files_to_process)} файлов")
                
                if not files_to_process:
                    logger.info("Все файлы уже обработаны")
                    self.is_index_built = True
                    return True
                
                # Этап 7: Обработка файлов по чанкам
                progress_offset = 15  # 15% уже прошли на сканирование и кэш
                progress_range = 80   # 80% на обработку файлов
                
                for chunk_idx in range(start_chunk, total_chunks):
                    start_idx = chunk_idx * chunk_size
                    end_idx = min(start_idx + chunk_size, len(files_to_process))
                    chunk_files = files_to_process[start_idx:end_idx]
                    
                    if not chunk_files:
                        break
                    
                    # Проверка памяти перед каждым чанком
                    available_memory, can_continue, memory_message = self._check_memory_status()
                    
                    if not can_continue:
                        logger.error(f"Недостаточно памяти на чанке {chunk_idx}: {memory_message}")
                        # Сохраняем прогресс
                        self.cache_manager.save_chunk_progress(
                            cache_key, 
                            chunk_idx, 
                            total_chunks,
                            processed_files
                        )
                        return False
                    
                    chunk_progress = int((chunk_idx / total_chunks) * progress_range) + progress_offset
                    
                    if progress_callback:
                        progress_callback(
                            chunk_progress, 100,
                            f"Обработка чанка {chunk_idx + 1}/{total_chunks} ({len(chunk_files)} файлов)"
                        )
                    
                    # Обработка чанка
                    try:
                        chunk_embeddings_array = self.image_analyzer.encode_images(
                            chunk_files,
                            progress_callback=lambda current, total, msg: progress_callback(
                                chunk_progress + int((current / total) * (progress_range / total_chunks)),
                                100,
                                f"Чанк {chunk_idx + 1}/{total_chunks}: {msg}"
                            ) if progress_callback else None
                        )
                        
                        # Преобразуем в словарь для совместимости
                        chunk_embeddings = {}
                        for i, file_path in enumerate(chunk_files):
                            if i < len(chunk_embeddings_array):
                                chunk_embeddings[file_path] = chunk_embeddings_array[i]
                        
                        # Добавляем эмбеддинги в общий словарь
                        self.current_embeddings.update(chunk_embeddings)
                        
                        # Сохраняем эмбеддинги в кэш
                        self.cache_manager.cache_batch_embeddings(chunk_embeddings)
                        
                        # Обновляем список обработанных файлов
                        processed_files.extend(chunk_files)
                        
                        # Сохраняем прогресс
                        self.cache_manager.save_chunk_progress(
                            cache_key, 
                            chunk_idx, 
                            total_chunks,
                            processed_files
                        )
                        
                        # Принудительная сборка мусора после каждого чанка
                        self._force_garbage_collection()
                        
                    except Exception as e:
                        logger.error(f"Ошибка при обработке чанка {chunk_idx}: {e}")
                        # Сохраняем прогресс до ошибки
                        self.cache_manager.save_chunk_progress(
                            cache_key, 
                            chunk_idx, 
                            total_chunks,
                            processed_files
                        )
                        return False
                
                # Финальное сохранение кэша
                if progress_callback:
                    progress_callback(95, 100, "Сохранение кэша...")
                
                self.cache_manager.save_cache()
                
                # Очистка временных данных прогресса
                self.cache_manager.clear_chunk_progress(cache_key)
                
                self.is_index_built = True
                
                if progress_callback:
                    progress_callback(100, 100, f"Индекс построен! Обработано {len(self.current_embeddings)} изображений")
                
                logger.info(f"Индекс успешно построен для {len(self.current_embeddings)} изображений")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при построении индекса: {e}")
            return False
    
    def build_index(self, directory_path: str, 
                   recursive: bool = True,
                   date_filter: Optional[dict] = None,
                   progress_callback: Optional[Callable] = None,
                   force_rebuild: bool = False) -> bool:
        """
        Построение индекса изображений для указанной директории с обработкой по чанкам.
        
        Args:
            directory_path: Путь к директории с изображениями
            recursive: Рекурсивный поиск в подпапках
            date_filter: Фильтр по дате модификации файлов
            progress_callback: Функция для отслеживания прогресса
            force_rebuild: Принудительная перестройка индекса
            
        Returns:
            bool: True если индекс успешно построен
        """
        try:
            with self._lock:
                logger.info(f"Начало построения индекса для директории: {directory_path}")
                
                # Этап 1: Проверка памяти
                available_memory, can_continue, memory_message = self._check_memory_status()
                logger.info(memory_message)
                
                if not can_continue:
                    if progress_callback:
                        progress_callback(0, 100, memory_message)
                    logger.error(memory_message)
                    return False
                
                if available_memory < WARNING_MEMORY_GB and progress_callback:
                    progress_callback(0, 100, memory_message)
                
                # Этап 2: Сканирование файлов
                if progress_callback:
                    progress_callback(0, 100, "Сканирование директории...")
                
                self.current_file_paths = self.file_scanner.scan_directory(
                    directory_path, 
                    recursive=recursive,
                    date_filter=date_filter,
                    progress_callback=lambda current, total, msg: progress_callback(
                        int(current / total * 10), 100, f"Сканирование: {msg}"
                    ) if progress_callback else None
                )
                
                if not self.current_file_paths:
                    logger.warning("Изображения не найдены")
                    return False
                
                total_files = len(self.current_file_paths)
                logger.info(f"Найдено {total_files} изображений")
                
                # Этап 3: Проверка возможности восстановления прогресса
                resume_data = None
                if not force_rebuild:
                    resume_data = self.cache_manager.load_chunk_progress(directory_path)
                
                # Этап 4: Расчет размера чанков
                chunk_size = self._calculate_optimal_chunk_size(total_files, available_memory)
                total_chunks = (total_files + chunk_size - 1) // chunk_size
                
                logger.info(f"Обработка {total_files} файлов по {chunk_size} в чанке ({total_chunks} чанков)")
                
                # Этап 5: Загрузка кэшированных эмбеддингов
                if progress_callback:
                    progress_callback(10, 100, "Проверка кэша...")
                
                if not force_rebuild:
                    cached_embeddings, uncached_paths = self.cache_manager.get_cached_embeddings_for_paths(
                        self.current_file_paths
                    )
                    
                    # Очистка недействительных записей кэша
                    self.cache_manager.remove_invalid_cache_entries(self.current_file_paths)
                else:
                    cached_embeddings = {}
                    uncached_paths = self.current_file_paths.copy()
                
                self.current_embeddings = cached_embeddings.copy()
                
                # Этап 6: Определение файлов для обработки с учетом восстановления
                files_to_process = uncached_paths
                start_chunk = 0
                processed_files = []
                
                if resume_data and not force_rebuild:
                    # Восстановление после прерывания
                    processed_files = resume_data.get('processed_files', [])
                    start_chunk = resume_data.get('processed_chunks', 0)
                    
                    # Исключаем уже обработанные файлы
                    processed_set = set(processed_files)
                    files_to_process = [f for f in uncached_paths if f not in processed_set]
                    
                    logger.info(f"Восстановление с чанка {start_chunk}, осталось файлов: {len(files_to_process)}")
                
                # Этап 7: Обработка по чанкам
                if files_to_process:
                    success = self._process_files_in_chunks(
                        files_to_process, 
                        chunk_size, 
                        start_chunk,
                        total_chunks,
                        processed_files,
                        directory_path,
                        progress_callback
                    )
                    
                    if not success:
                        return False
                else:
                    logger.info("Все файлы уже обработаны")
                
                # Этап 8: Финализация
                self.is_index_built = True
                
                # Очистка прогресса после успешного завершения
                self.cache_manager.clear_chunk_progress(directory_path)
                
                if progress_callback:
                    progress_callback(100, 100, "Индекс построен успешно!")
                
                logger.info(f"Индекс построен успешно. Всего изображений: {len(self.current_embeddings)}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при построении индекса: {e}")
            if progress_callback:
                progress_callback(0, 100, f"Ошибка: {str(e)}")
            return False
    
    def _process_files_in_chunks(self, files_to_process: List[str], 
                                chunk_size: int, 
                                start_chunk: int,
                                total_chunks: int,
                                processed_files: List[str],
                                directory_path: str,
                                progress_callback: Optional[Callable] = None) -> bool:
        """
        Обработка файлов по чанкам с мониторингом памяти.
        
        Args:
            files_to_process: Список файлов для обработки
            chunk_size: Размер чанка
            start_chunk: Номер чанка для начала (для восстановления)
            total_chunks: Общее количество чанков
            processed_files: Список уже обработанных файлов
            directory_path: Путь к директории (для сохранения прогресса)
            progress_callback: Функция для отслеживания прогресса
            
        Returns:
            bool: True если обработка успешна
        """
        current_chunk_size = chunk_size
        
        # Разбиваем файлы на чанки
        chunks = []
        for i in range(0, len(files_to_process), current_chunk_size):
            chunk_files = files_to_process[i:i + current_chunk_size]
            chunks.append(chunk_files)
        
        processed_count = len(processed_files)
        
        for chunk_idx, chunk_files in enumerate(chunks):
            actual_chunk_idx = start_chunk + chunk_idx
            
            try:
                # Проверка памяти перед обработкой чанка
                available_memory, can_continue, memory_message = self._check_memory_status()
                
                if not can_continue:
                    logger.error(f"Остановка на чанке {actual_chunk_idx + 1}: {memory_message}")
                    if progress_callback:
                        progress_callback(0, 100, memory_message)
                    return False
                
                # Автоматическое уменьшение размера чанка при нехватке памяти
                if available_memory < WARNING_MEMORY_GB and current_chunk_size > 500:
                    new_chunk_size = int(current_chunk_size * AUTO_REDUCE_CHUNK_FACTOR)
                    logger.warning(f"Уменьшение размера чанка с {current_chunk_size} до {new_chunk_size}")
                    current_chunk_size = max(500, new_chunk_size)
                    
                    # Пересчитываем чанки с новым размером
                    remaining_files = files_to_process[chunk_idx * chunk_size:]
                    chunks = []
                    for i in range(0, len(remaining_files), current_chunk_size):
                        chunk_files = remaining_files[i:i + current_chunk_size]
                        chunks.append(chunk_files)
                    
                    chunk_files = chunks[0] if chunks else []
                    chunks = chunks[1:] if len(chunks) > 1 else []
                
                # Обновление прогресса
                progress_msg = f"Чанк {actual_chunk_idx + 1} из {total_chunks} ({processed_count + len(chunk_files)}/{len(self.current_file_paths)} изображений)"
                base_progress = 20 + int((actual_chunk_idx / total_chunks) * 70)
                
                if progress_callback:
                    progress_callback(base_progress, 100, progress_msg)
                
                logger.info(f"Обработка {progress_msg}, доступно памяти: {available_memory:.1f} ГБ")
                
                # Обработка чанка
                chunk_embeddings = self._create_embeddings_batch(
                    chunk_files,
                    lambda current, total, msg: progress_callback(
                        base_progress + int((current / total) * (70 / total_chunks)), 100, 
                        f"{progress_msg} - {msg}"
                    ) if progress_callback else None
                )
                
                # Добавление эмбеддингов
                if chunk_embeddings is not None and len(chunk_embeddings) > 0:
                    for i, file_path in enumerate(chunk_files):
                        if i < len(chunk_embeddings):
                            self.current_embeddings[file_path] = chunk_embeddings[i]
                            processed_files.append(file_path)
                            processed_count += 1
                    
                    # Сохранение в кэш после каждого чанка
                    chunk_embeddings_dict = {
                        path: self.current_embeddings[path] 
                        for path in chunk_files 
                        if path in self.current_embeddings
                    }
                    
                    self.cache_manager.cache_batch_embeddings(chunk_embeddings_dict)
                    self.cache_manager.save_cache()
                    
                    # Сохранение прогресса
                    self.cache_manager.save_chunk_progress(
                        directory_path, 
                        actual_chunk_idx + 1, 
                        total_chunks, 
                        processed_files
                    )
                else:
                    logger.warning(f"Не удалось обработать чанк {actual_chunk_idx + 1}")
                
                # Принудительная сборка мусора после каждого чанка
                self._force_garbage_collection()
                
            except MemoryError as e:
                logger.error(f"Ошибка памяти на чанке {actual_chunk_idx + 1}: {e}")
                if current_chunk_size > 500:
                    # Попытка уменьшить размер чанка и повторить
                    current_chunk_size = max(500, int(current_chunk_size * AUTO_REDUCE_CHUNK_FACTOR))
                    logger.info(f"Повторная попытка с размером чанка {current_chunk_size}")
                    continue
                else:
                    if progress_callback:
                        progress_callback(0, 100, f"Критическая ошибка памяти на чанке {actual_chunk_idx + 1}")
                    return False
                    
            except Exception as e:
                logger.error(f"Ошибка при обработке чанка {actual_chunk_idx + 1}: {e}")
                # Продолжаем с следующим чанком, логируя проблемные изображения
                continue
        
        return True
    
    def _create_embeddings_batch(self, file_paths: List[str], 
                               progress_callback: Optional[Callable] = None) -> np.ndarray:
        """
        Создание эмбеддингов для батча изображений с многопоточностью.
        
        Args:
            file_paths: Список путей к файлам
            progress_callback: Функция для отслеживания прогресса
            
        Returns:
            np.ndarray: Массив эмбеддингов
        """
        if not file_paths:
            return np.array([])
        
        try:
            # Используем анализатор изображений для создания эмбеддингов
            embeddings = self.image_analyzer.encode_images(
                file_paths, 
                progress_callback=progress_callback
            )
            return embeddings
            
        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддингов: {e}")
            return np.array([])
    
    def search(self, query: str, 
              max_results: int = MAX_RESULTS_DEFAULT,
              similarity_threshold: float = SIMILARITY_THRESHOLD) -> List[SearchResult]:
        """
        Поиск изображений по текстовому запросу.
        
        Args:
            query: Текстовый запрос для поиска
            max_results: Максимальное количество результатов
            similarity_threshold: Минимальный порог схожести
            
        Returns:
            List[SearchResult]: Список результатов поиска, отсортированных по релевантности
        """
        if not self.is_index_built:
            raise RuntimeError("Индекс не построен. Выполните build_index() перед поиском.")
        
        if not query.strip():
            raise ValueError("Поисковый запрос не может быть пустым")
        
        try:
            logger.info(f"Поиск по запросу: '{query}'")
            
            # Создание эмбеддинга для текстового запроса
            query_embedding = self.image_analyzer.encode_text(query)
            
            # Подготовка данных для поиска
            file_paths = list(self.current_embeddings.keys())
            embeddings_matrix = np.array([self.current_embeddings[path] for path in file_paths])
            
            if len(embeddings_matrix) == 0:
                return []
            
            # Вычисление схожести
            similarities = self.image_analyzer.calculate_similarity(query_embedding, embeddings_matrix)
            
            # Создание результатов
            results = []
            for i, (file_path, similarity) in enumerate(zip(file_paths, similarities)):
                if similarity >= similarity_threshold:
                    # Используем новый метод для создания результата с информацией о папке
                    result = self.get_search_result_with_folder_info(file_path, float(similarity))
                    results.append(result)
            
            # Сортировка по релевантности (по убыванию схожести)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Ограничение количества результатов
            results = results[:max_results]
            
            logger.info(f"Найдено {len(results)} результатов")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, any]:
        """
        Получение статистики построенного индекса.
        
        Returns:
            Dict[str, any]: Статистика индекса
        """
        cache_stats = self.cache_manager.get_cache_stats()
        available_memory, can_continue, memory_message = self._check_memory_status()
        
        return {
            'is_built': self.is_index_built,
            'total_images': len(self.current_embeddings),
            'indexed_paths': len(self.current_file_paths),
            'cache_stats': cache_stats,
            'model_ready': self.image_analyzer.is_model_ready(),
            'memory_status': {
                'available_gb': available_memory,
                'can_continue': can_continue,
                'message': memory_message
            }
        }
    
    def clear_index(self) -> None:
        """Очистка текущего индекса."""
        with self._lock:
            self.current_embeddings.clear()
            self.current_file_paths.clear()
            self.is_index_built = False
            self._force_garbage_collection()
            logger.info("Индекс очищен")
    
    def clear_cache(self) -> None:
        """Полная очистка кэша."""
        self.cache_manager.clear_cache()
        logger.info("Кэш очищен")
    
    def is_ready(self) -> bool:
        """
        Проверка готовности поискового движка.
        
        Returns:
            bool: True если движок готов к работе
        """
        return (self.image_analyzer.is_model_ready() and 
                self.is_index_built and 
                len(self.current_embeddings) > 0)
    
    def can_resume_indexing(self, directory_path: str) -> Tuple[bool, Optional[dict]]:
        """
        Проверка возможности восстановления прерванной индексации.
        
        Args:
            directory_path: Путь к директории
            
        Returns:
            Tuple[bool, Optional[dict]]: (можно_восстановить, данные_прогресса)
        """
        progress_data = self.cache_manager.load_chunk_progress(directory_path)
        
        if progress_data is None:
            return False, None
        
        # Проверяем, что прогресс не завершен
        processed_chunks = progress_data.get('processed_chunks', 0)
        total_chunks = progress_data.get('total_chunks', 0)
        
        if processed_chunks >= total_chunks:
            # Прогресс завершен, очищаем его
            self.cache_manager.clear_chunk_progress(directory_path)
            return False, None
        
        return True, progress_data
    
    def get_memory_usage_info(self) -> dict:
        """
        Получение подробной информации об использовании памяти.
        
        Returns:
            dict: Информация о памяти
        """
        try:
            memory = psutil.virtual_memory()
            
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent_used': memory.percent,
                'can_continue': memory.available >= MIN_MEMORY_GB * (1024**3),
                'warning_threshold': memory.available < WARNING_MEMORY_GB * (1024**3)
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о памяти: {e}")
            return {
                'error': str(e),
                'can_continue': True,
                'warning_threshold': False
            }
    
    def get_index_stats_multiple_folders(self) -> dict:
        """
        Получение статистики индекса для множественных папок.
        
        Returns:
            dict: Статистика индекса с разбивкой по папкам
        """
        if not self.is_index_built:
            return {'total_images': 0, 'folders': {}}
        
        folder_stats = {}
        total_images = len(self.current_file_paths)
        
        # Подсчет изображений по папкам
        if hasattr(self, 'folder_file_mapping'):
            for file_path, folder_path in self.folder_file_mapping.items():
                if folder_path not in folder_stats:
                    folder_stats[folder_path] = 0
                folder_stats[folder_path] += 1
        
        return {
            'total_images': total_images,
            'folders': folder_stats,
            'total_folders': len(folder_stats),
            'is_ready': self.is_ready()
        }
    
    def get_search_result_with_folder_info(self, file_path: str, similarity_score: float) -> SearchResult:
        """
        Создание результата поиска с информацией о папке-источнике.
        
        Args:
            file_path: Путь к файлу
            similarity_score: Коэффициент схожести
            
        Returns:
            SearchResult: Результат поиска с дополнительной информацией
        """
        # Получаем базовую информацию о файле
        file_info = {'file_size': 0, 'modified_date': ''}
        
        try:
            stat = os.stat(file_path)
            file_info['file_size'] = stat.st_size
            file_info['modified_date'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        except OSError:
            pass
        
        # Добавляем информацию о папке-источнике
        if hasattr(self, 'folder_file_mapping') and file_path in self.folder_file_mapping:
            file_info['source_folder'] = self.folder_file_mapping[file_path]
            file_info['folder_name'] = os.path.basename(self.folder_file_mapping[file_path])
        else:
            file_info['source_folder'] = os.path.dirname(file_path)
            file_info['folder_name'] = os.path.basename(os.path.dirname(file_path))
        
        return SearchResult(file_path, similarity_score, file_info)