"""
Модуль для сканирования папок и поиска изображений.
Обеспечивает рекурсивный поиск файлов изображений с фильтрацией по дате.
"""

import os
from pathlib import Path
from typing import List, Optional, Callable
import logging
from datetime import datetime, timedelta

from config import SUPPORTED_FORMATS

logger = logging.getLogger(__name__)

class FileScanner:
    """
    Класс для сканирования файловой системы и поиска изображений.
    Поддерживает рекурсивный поиск и фильтрацию по различным критериям.
    """
    
    def __init__(self):
        """Инициализация сканера файлов."""
        self.supported_formats = [fmt.lower() for fmt in SUPPORTED_FORMATS]
    
    def scan_directory(self, directory_path: str, 
                      recursive: bool = True,
                      date_filter: Optional[dict] = None,
                      progress_callback: Optional[Callable] = None) -> List[str]:
        """
        Сканирование директории для поиска изображений.
        
        Args:
            directory_path: Путь к директории для сканирования
            recursive: Рекурсивный поиск в подпапках
            date_filter: Фильтр по дате в формате {'days': количество_дней_назад}
            progress_callback: Функция обратного вызова для отслеживания прогресса
            
        Returns:
            List[str]: Список путей к найденным изображениям
        """
        # Нормализация пути для Windows
        directory_path = os.path.normpath(directory_path)
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Директория не найдена: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise ValueError(f"Указанный путь не является директорией: {directory_path}")
        
        logger.info(f"Начало сканирования директории: {directory_path}")
        logger.info(f"Поддерживаемые форматы: {self.supported_formats}")
        
        image_files = []
        processed_files = 0
        
        # Определяем временной фильтр
        date_threshold = None
        if date_filter and 'days' in date_filter:
            date_threshold = datetime.now() - timedelta(days=date_filter['days'])
        
        try:
            if recursive:
                total_files = self._count_files(directory_path)
                logger.info(f"Всего файлов для проверки: {total_files}")
                
                for root, dirs, files in os.walk(directory_path):
                    logger.debug(f"Проверка папки: {root}, файлов: {len(files)}")
                    for file in files:
                        processed_files += 1
                        
                        if progress_callback and processed_files % 100 == 0:
                            progress_callback(
                                processed_files, 
                                total_files, 
                                f"Сканирование: {processed_files}/{total_files} файлов"
                            )
                        
                        file_path = os.path.join(root, file)
                        
                        # Отладочная информация для первых файлов
                        if len(image_files) < 5:
                            logger.debug(f"Проверка файла: {file}")
                            logger.debug(f"Расширение: {Path(file).suffix.lower()}")
                            logger.debug(f"Является изображением: {self._is_image_file(file_path)}")
                        
                        if self._is_image_file(file_path) and self._passes_date_filter(file_path, date_threshold):
                            image_files.append(file_path)
                            logger.debug(f"Добавлен файл: {file_path}")
            else:
                files = os.listdir(directory_path)
                total_files = len(files)
                logger.info(f"Файлов в директории: {total_files}")
                
                for i, file in enumerate(files):
                    if progress_callback and i % 50 == 0:
                        progress_callback(
                            i, 
                            total_files, 
                            f"Сканирование: {i}/{total_files} файлов"
                        )
                    
                    file_path = os.path.join(directory_path, file)
                    
                    # Отладочная информация для первых файлов
                    if i < 5:
                        logger.info(f"Проверка файла: {file}")
                        logger.info(f"Полный путь: {file_path}")
                        logger.info(f"Существует файл: {os.path.isfile(file_path)}")
                        logger.info(f"Расширение: {Path(file).suffix.lower()}")
                        logger.info(f"Является изображением: {self._is_image_file(file_path)}")
                    
                    if (os.path.isfile(file_path) and 
                        self._is_image_file(file_path) and 
                        self._passes_date_filter(file_path, date_threshold)):
                        image_files.append(file_path)
        
        except Exception as e:
            logger.error(f"Ошибка при сканировании директории: {e}")
            raise
        
        logger.info(f"Найдено {len(image_files)} изображений")
        return image_files
    
    def _count_files(self, directory_path: str) -> int:
        """
        Подсчет общего количества файлов для отслеживания прогресса.
        
        Args:
            directory_path: Путь к директории
            
        Returns:
            int: Общее количество файлов
        """
        total = 0
        try:
            for root, dirs, files in os.walk(directory_path):
                total += len(files)
        except Exception:
            return 0
        return total
    
    def _is_image_file(self, file_path: str) -> bool:
        """
        Проверка, является ли файл изображением поддерживаемого формата.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True если файл является поддерживаемым изображением
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            return file_extension in self.supported_formats
        except Exception:
            return False
    
    def _passes_date_filter(self, file_path: str, date_threshold: Optional[datetime]) -> bool:
        """
        Проверка соответствия файла фильтру по дате.
        
        Args:
            file_path: Путь к файлу
            date_threshold: Пороговая дата для фильтрации
            
        Returns:
            bool: True если файл проходит фильтр по дате
        """
        if date_threshold is None:
            return True
        
        try:
            # Получаем дату модификации файла
            modification_time = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(modification_time)
            return file_date >= date_threshold
        except Exception:
            # Если не можем получить дату, включаем файл
            return True
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Получение информации о файле.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            dict: Словарь с информацией о файле
        """
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modification_time': datetime.fromtimestamp(stat.st_mtime),
                'creation_time': datetime.fromtimestamp(stat.st_ctime),
                'extension': Path(file_path).suffix.lower()
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о файле {file_path}: {e}")
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': 0,
                'modification_time': datetime.now(),
                'creation_time': datetime.now(),
                'extension': Path(file_path).suffix.lower() if file_path else ''
            }
    
    def validate_directory(self, directory_path: str) -> tuple:
        """
        Валидация директории перед сканированием.
        
        Args:
            directory_path: Путь к директории
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not directory_path:
            return False, "Путь к директории не указан"
        
        if not os.path.exists(directory_path):
            return False, f"Директория не существует: {directory_path}"
        
        if not os.path.isdir(directory_path):
            return False, f"Указанный путь не является директорией: {directory_path}"
        
        try:
            # Проверяем права доступа
            os.listdir(directory_path)
        except PermissionError:
            return False, f"Нет прав доступа к директории: {directory_path}"
        except Exception as e:
            return False, f"Ошибка при доступе к директории: {e}"
        
        return True, ""
    
    def estimate_scan_time(self, directory_path: str, recursive: bool = True) -> dict:
        """
        Оценка времени сканирования директории.
        
        Args:
            directory_path: Путь к директории
            recursive: Рекурсивный поиск
            
        Returns:
            dict: Оценочная информация о сканировании
        """
        try:
            file_count = self._count_files(directory_path) if recursive else len(os.listdir(directory_path))
            
            # Примерная оценка: 1000 файлов в секунду
            estimated_seconds = max(1, file_count / 1000)
            
            return {
                'estimated_files': file_count,
                'estimated_time_seconds': estimated_seconds,
                'estimated_time_formatted': self._format_time(estimated_seconds)
            }
        except Exception:
            return {
                'estimated_files': 0,
                'estimated_time_seconds': 0,
                'estimated_time_formatted': "Неизвестно"
            }
    
    def _format_time(self, seconds: float) -> str:
        """
        Форматирование времени в читаемый вид.
        
        Args:
            seconds: Количество секунд
            
        Returns:
            str: Отформатированное время
        """
        if seconds < 60:
            return f"{int(seconds)} сек"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} мин"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours} ч {minutes} мин"