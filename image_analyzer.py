"""
Модуль для анализа изображений с использованием CLIP модели.
Обеспечивает создание эмбеддингов изображений и текстовых запросов.
"""

import torch
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
import warnings
from typing import List, Union, Optional
import logging

from config import CLIP_MODEL_NAME, CLIP_BATCH_SIZE_CPU, CLIP_BATCH_SIZE_GPU

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """
    Класс для анализа изображений с использованием CLIP модели.
    Предоставляет методы для создания эмбеддингов изображений и текста.
    """
    
    def __init__(self):
        """Инициализация анализатора изображений."""
        self.model = None
        self.device = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """
        Инициализация CLIP модели.
        Автоматически определяет доступное устройство (GPU/CPU).
        """
        try:
            # Определение устройства с приоритетом GPU
            if torch.cuda.is_available():
                self.device = 'cuda'
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"Используется GPU: {gpu_name} ({gpu_memory:.1f} ГБ)")
            else:
                self.device = 'cpu'
                logger.info("GPU недоступен, используется CPU")
            
            logger.info(f"Используется устройство: {self.device}")
            
            # Подавление предупреждений
            warnings.filterwarnings("ignore", category=FutureWarning)
            
            # Загрузка модели
            logger.info(f"Загрузка модели {CLIP_MODEL_NAME}...")
            self.model = SentenceTransformer(CLIP_MODEL_NAME, device=self.device)
            
            # Дополнительная оптимизация для GPU
            if self.device == 'cuda':
                torch.backends.cudnn.benchmark = True  # Оптимизация для фиксированных размеров
                logger.info("Включена оптимизация cuDNN")
            
            logger.info("Модель успешно загружена")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации модели: {e}")
            # Fallback на CPU если GPU не работает
            if self.device == 'cuda':
                logger.warning("Падение назад на CPU из-за ошибки GPU")
                self.device = 'cpu'
                try:
                    self.model = SentenceTransformer(CLIP_MODEL_NAME, device=self.device)
                    logger.info("Модель успешно загружена на CPU")
                except Exception as e2:
                    raise RuntimeError(f"Не удалось загрузить модель даже на CPU: {e2}")
            else:
                raise RuntimeError(f"Не удалось загрузить модель CLIP: {e}")
    
    def encode_images(self, image_paths: List[str], 
                     progress_callback: Optional[callable] = None) -> np.ndarray:
        """
        Создание эмбеддингов для списка изображений с оптимизацией памяти.
        
        Args:
            image_paths: Список путей к изображениям
            progress_callback: Функция обратного вызова для отслеживания прогресса
            
        Returns:
            numpy.ndarray: Массив эмбеддингов изображений
        """
        if not self.model:
            raise RuntimeError("Модель не инициализирована")
        
        if not image_paths:
            return np.array([])
        
        # Определяем размер батча в зависимости от доступной памяти
        import psutil
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Уменьшаем размер батча при нехватке памяти
        if available_memory_gb < 2.0:
            batch_size = 8  # Очень маленький батч для слабых систем
        elif available_memory_gb < 4.0:
            batch_size = 16  # Средний батч
        else:
            batch_size = CLIP_BATCH_SIZE_GPU if self.device == 'cuda' else CLIP_BATCH_SIZE_CPU
        
        # Дополнительно уменьшаем батч для GPU при больших изображениях
        if self.device == 'cuda' and len(image_paths) > 1000:
            batch_size = min(batch_size, 32)
        
        logger.info(f"Обработка {len(image_paths)} изображений батчами по {batch_size} (устройство: {self.device}, память: {available_memory_gb:.1f} ГБ)")
        
        embeddings = []
        processed_count = 0
        total_batches = (len(image_paths) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[batch_idx:batch_idx + batch_size]
            
            # Загружаем и обрабатываем только текущий батч
            batch_images = []
            valid_batch_paths = []
            
            for path in batch_paths:
                try:
                    image = self._load_and_preprocess_image(path)
                    batch_images.append(image)
                    valid_batch_paths.append(path)
                    
                except Exception as e:
                    logger.warning(f"Не удалось загрузить изображение {path}: {e}")
                    continue
            
            if not batch_images:
                continue
            
            try:
                # Обрабатываем батч изображений
                batch_embeddings = self.model.encode(
                    batch_images,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                
                embeddings.append(batch_embeddings)
                processed_count += len(valid_batch_paths)
                
                # Принудительная очистка памяти после каждого батча
                del batch_images
                del batch_embeddings
                import gc
                gc.collect()
                
                if progress_callback:
                    current_batch = (batch_idx // batch_size) + 1
                    progress_callback(
                        current_batch, 
                        total_batches, 
                        f"Обработка батча {current_batch}/{total_batches} на {self.device.upper()} ({processed_count}/{len(image_paths)})"
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка при создании эмбеддингов для батча {batch_idx}: {e}")
                # Принудительная очистка памяти при ошибке
                if 'batch_images' in locals():
                    del batch_images
                import gc
                gc.collect()
                
                # При ошибке памяти пытаемся уменьшить размер батча
                if "allocate" in str(e).lower() or "memory" in str(e).lower():
                    logger.warning(f"Ошибка памяти в батче {batch_idx}, попытка уменьшить размер батча")
                    
                    # Рекурсивно обрабатываем оставшуеся изображения с меньшим батчем
                    if batch_size > 4:
                        remaining_paths = image_paths[batch_idx:]
                        if remaining_paths:
                            # Создаем новый экземпляр анализатора с меньшим батчем
                            smaller_batch_embeddings = self._encode_images_smaller_batch(
                                remaining_paths, 
                                max(4, batch_size // 2),
                                progress_callback,
                                current_batch=batch_idx // batch_size,
                                total_batches=total_batches
                            )
                            if len(smaller_batch_embeddings) > 0:
                                embeddings.append(smaller_batch_embeddings)
                        break
                continue
        
        if embeddings:
            try:
                result = np.vstack(embeddings)
                logger.info(f"Успешно создано {len(result)} эмбеддингов")
                return result
            except Exception as e:
                logger.error(f"Ошибка при объединении эмбеддингов: {e}")
                return np.array([])
        else:
            logger.warning("Не удалось создать ни одного эмбеддинга")
            return np.array([])
    
    def _encode_images_smaller_batch(self, image_paths: List[str], small_batch_size: int, 
                                   progress_callback: Optional[callable] = None,
                                   current_batch: int = 0, total_batches: int = 1) -> np.ndarray:
        """
        Вспомогательный метод для обработки изображений с уменьшенным размером батча.
        """
        embeddings = []
        
        for batch_idx in range(0, len(image_paths), small_batch_size):
            batch_paths = image_paths[batch_idx:batch_idx + small_batch_size]
            batch_images = []
            
            for path in batch_paths:
                try:
                    image = self._load_and_preprocess_image(path)
                    batch_images.append(image)
                except Exception as e:
                    logger.warning(f"Не удалось загрузить изображение {path}: {e}")
                    continue
            
            if not batch_images:
                continue
            
            try:
                batch_embeddings = self.model.encode(
                    batch_images,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                
                embeddings.append(batch_embeddings)
                
                # Очистка памяти
                del batch_images
                del batch_embeddings
                import gc
                gc.collect()
                
                if progress_callback:
                    current_batch += 1
                    progress_callback(
                        current_batch, 
                        total_batches, 
                        f"Восстановление: батч {current_batch}/{total_batches} (размер: {small_batch_size})"
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка в уменьшенном батче {batch_idx}: {e}")
                if 'batch_images' in locals():
                    del batch_images
                import gc
                gc.collect()
                continue
        
        if embeddings:
            return np.vstack(embeddings)
        else:
            return np.array([])
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Создание эмбеддинга для текстового запроса.
        
        Args:
            text: Текстовый запрос
            
        Returns:
            numpy.ndarray: Эмбеддинг текста
        """
        if not self.model:
            raise RuntimeError("Модель не инициализирована")
        
        try:
            embedding = self.model.encode(
                [text],
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding[0]
            
        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддинга для текста '{text}': {e}")
            raise
    
    def _load_and_preprocess_image(self, image_path: str) -> Image.Image:
        """
        Загрузка и предобработка изображения с оптимизацией памяти.
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            PIL.Image.Image: Предобработанное изображение
        """
        try:
            image = Image.open(image_path)
            
            # Конвертация в RGB если необходимо
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Ограничиваем размер изображения для экономии памяти
            # CLIP модели работают эффективно с изображениями до 1024x1024
            max_size = 1024
            width, height = image.size
            
            if width > max_size or height > max_size:
                # Сохраняем пропорции при изменении размера
                if width > height:
                    new_width = max_size
                    new_height = int((height * max_size) / width)
                else:
                    new_height = max_size
                    new_width = int((width * max_size) / height)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Изображение {image_path} изменено с {width}x{height} на {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            raise IOError(f"Не удалось загрузить изображение {image_path}: {e}")
    
    def calculate_similarity(self, text_embedding: np.ndarray, 
                           image_embeddings: np.ndarray) -> np.ndarray:
        """
        Вычисление схожести между текстовым запросом и изображениями.
        
        Args:
            text_embedding: Эмбеддинг текстового запроса
            image_embeddings: Эмбеддинги изображений
            
        Returns:
            numpy.ndarray: Массив коэффициентов схожести
        """
        if len(image_embeddings) == 0:
            return np.array([])
        
        # Вычисление косинусного сходства
        similarities = np.dot(image_embeddings, text_embedding)
        return similarities
    
    def is_model_ready(self) -> bool:
        """
        Проверка готовности модели к работе.
        
        Returns:
            bool: True если модель готова, False иначе
        """
        return self.model is not None