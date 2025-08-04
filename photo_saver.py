"""
Модуль для сохранения выбранных фотографий в организованную структуру папок.
Автоматически создает подпапки по дате создания фотографий в формате ГГГГ-ММ.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)

class PhotoSaver:
    """Класс для сохранения фотографий с автоматической организацией по датам."""
    
    def __init__(self):
        """Инициализация сохранялки фотографий."""
        pass
    
    def save_photos(self, photo_paths: List[str], destination_dir: str, 
                   progress_callback: Optional[callable] = None) -> Dict[str, any]:
        """
        Сохранение списка фотографий в указанную директорию с организацией по датам.
        
        Args:
            photo_paths: Список путей к фотографиям для сохранения
            destination_dir: Целевая директория для сохранения
            progress_callback: Функция обратного вызова для отслеживания прогресса
            
        Returns:
            Dict[str, any]: Результат операции с статистикой
        """
        if not photo_paths:
            return {'success': False, 'error': 'Список фотографий пуст'}
        
        if not os.path.exists(destination_dir):
            try:
                os.makedirs(destination_dir)
            except Exception as e:
                return {'success': False, 'error': f'Не удалось создать целевую директорию: {e}'}
        
        results = {
            'success': True,
            'total_photos': len(photo_paths),
            'saved_photos': 0,
            'failed_photos': 0,
            'created_folders': set(),
            'errors': []
        }
        
        logger.info(f"Начинаем сохранение {len(photo_paths)} фотографий в {destination_dir}")
        
        for i, photo_path in enumerate(photo_paths):
            try:
                # Получаем дату создания фотографии
                creation_date = self._get_photo_creation_date(photo_path)
                
                # Создаем подпапку в формате ГГГГ-ММ
                folder_name = creation_date.strftime('%Y-%m')
                target_folder = os.path.join(destination_dir, folder_name)
                
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                    results['created_folders'].add(folder_name)
                    logger.info(f"Создана папка: {folder_name}")
                
                # Определяем имя файла в целевой папке
                original_name = os.path.basename(photo_path)
                target_path = os.path.join(target_folder, original_name)
                
                # Если файл с таким именем уже существует, добавляем суффикс
                target_path = self._get_unique_filename(target_path)
                
                # Копируем файл
                shutil.copy2(photo_path, target_path)
                results['saved_photos'] += 1
                
                logger.debug(f"Сохранено: {photo_path} -> {target_path}")
                
                # Обновляем прогресс
                if progress_callback:
                    progress_callback(i + 1, len(photo_paths), f"Сохранено: {original_name}")
                
            except Exception as e:
                error_msg = f"Ошибка при сохранении {photo_path}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['failed_photos'] += 1
        
        # Финальная статистика
        results['created_folders'] = list(results['created_folders'])
        logger.info(f"Сохранение завершено. Успешно: {results['saved_photos']}, "
                   f"Ошибок: {results['failed_photos']}, Создано папок: {len(results['created_folders'])}")
        
        return results
    
    def _get_photo_creation_date(self, photo_path: str) -> datetime:
        """
        Получение даты создания фотографии из EXIF данных или файловой системы.
        
        Args:
            photo_path: Путь к фотографии
            
        Returns:
            datetime: Дата создания фотографии
        """
        try:
            # Сначала пытаемся получить дату из EXIF
            exif_date = self._get_exif_date(photo_path)
            if exif_date:
                return exif_date
        except Exception as e:
            logger.debug(f"Не удалось получить EXIF дату для {photo_path}: {e}")
        
        try:
            # Если EXIF недоступен, используем дату модификации файла
            timestamp = os.path.getmtime(photo_path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.warning(f"Не удалось получить дату файла для {photo_path}: {e}")
            # В крайнем случае используем текущую дату
            return datetime.now()
    
    def _get_exif_date(self, photo_path: str) -> Optional[datetime]:
        """
        Извлечение даты создания из EXIF данных изображения.
        
        Args:
            photo_path: Путь к изображению
            
        Returns:
            Optional[datetime]: Дата создания из EXIF или None
        """
        try:
            with Image.open(photo_path) as image:
                exif_data = image._getexif()
                
                if exif_data is not None:
                    # Ищем дату создания в различных EXIF тегах
                    date_tags = [
                        'DateTimeOriginal',  # Дата съемки
                        'DateTime',          # Дата изменения
                        'DateTimeDigitized'  # Дата оцифровки
                    ]
                    
                    for tag_name in date_tags:
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == tag_name and value:
                                # Парсим дату в формате EXIF: "YYYY:MM:DD HH:MM:SS"
                                try:
                                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                except ValueError:
                                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Ошибка при чтении EXIF из {photo_path}: {e}")
            return None
    
    def _get_unique_filename(self, file_path: str) -> str:
        """
        Получение уникального имени файла, добавляя суффикс если файл уже существует.
        
        Args:
            file_path: Исходный путь к файлу
            
        Returns:
            str: Уникальный путь к файлу
        """
        if not os.path.exists(file_path):
            return file_path
        
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, extension = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name}_({counter}){extension}"
            new_path = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_path):
                return new_path
            
            counter += 1
            
            # Защита от бесконечного цикла
            if counter > 1000:
                raise RuntimeError(f"Не удалось создать уникальное имя для файла {file_path}")
    
    def preview_organization(self, photo_paths: List[str]) -> Dict[str, List[str]]:
        """
        Предварительный просмотр организации фотографий по папкам.
        
        Args:
            photo_paths: Список путей к фотографиям
            
        Returns:
            Dict[str, List[str]]: Словарь {папка: [список_файлов]}
        """
        organization = {}
        
        for photo_path in photo_paths:
            try:
                creation_date = self._get_photo_creation_date(photo_path)
                folder_name = creation_date.strftime('%Y-%m')
                
                if folder_name not in organization:
                    organization[folder_name] = []
                
                organization[folder_name].append(os.path.basename(photo_path))
                
            except Exception as e:
                logger.warning(f"Не удалось обработать {photo_path}: {e}")
                # Добавляем в папку "unknown"
                if 'unknown' not in organization:
                    organization['unknown'] = []
                organization['unknown'].append(os.path.basename(photo_path))
        
        return organization
