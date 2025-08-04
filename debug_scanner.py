"""
Отладочный скрипт для проверки сканирования файлов.
Запустите его для диагностики проблем со сканированием изображений.
"""

import os
from pathlib import Path

def debug_directory_scan(directory_path: str):
    """Отладочное сканирование директории."""
    print(f"=== Отладка сканирования директории ===")
    print(f"Путь: {directory_path}")
    print(f"Существует: {os.path.exists(directory_path)}")
    print(f"Является директорией: {os.path.isdir(directory_path)}")
    print()
    
    if not os.path.exists(directory_path):
        print("ОШИБКА: Директория не существует!")
        return
    
    if not os.path.isdir(directory_path):
        print("ОШИБКА: Путь не является директорией!")
        return
    
    # Поддерживаемые форматы
    supported_formats = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    print(f"Поддерживаемые форматы: {supported_formats}")
    print()
    
    try:
        files = os.listdir(directory_path)
        print(f"Всего файлов в директории: {len(files)}")
        print()
        
        image_files = []
        other_files = []
        
        for i, file in enumerate(files):
            file_path = os.path.join(directory_path, file)
            
            # Показываем первые 10 файлов для отладки
            if i < 10:
                print(f"Файл {i+1}: {file}")
                print(f"  Полный путь: {file_path}")
                print(f"  Существует: {os.path.exists(file_path)}")
                print(f"  Является файлом: {os.path.isfile(file_path)}")
                
                if os.path.isfile(file_path):
                    extension = Path(file).suffix
                    extension_lower = extension.lower()
                    print(f"  Расширение: '{extension}'")
                    print(f"  Расширение (lower): '{extension_lower}'")
                    print(f"  В поддерживаемых форматах: {extension_lower in [fmt.lower() for fmt in supported_formats]}")
                    
                    if extension_lower in ['.jpg', '.jpeg', '.png']:
                        image_files.append(file_path)
                        print(f"  -> ДОБАВЛЕН как изображение")
                    else:
                        other_files.append(file_path)
                        print(f"  -> НЕ изображение")
                else:
                    print(f"  -> НЕ файл (возможно, папка)")
                print()
            else:
                # Для остальных файлов только быстрая проверка
                if os.path.isfile(file_path):
                    extension_lower = Path(file).suffix.lower()
                    if extension_lower in ['.jpg', '.jpeg', '.png']:
                        image_files.append(file_path)
                    else:
                        other_files.append(file_path)
        
        print(f"=== РЕЗУЛЬТАТЫ ===")
        print(f"Найдено изображений: {len(image_files)}")
        print(f"Других файлов: {len(other_files)}")
        
        if image_files:
            print(f"\nПервые 5 найденных изображений:")
            for i, img_path in enumerate(image_files[:5]):
                print(f"  {i+1}. {os.path.basename(img_path)}")
        
        if other_files:
            print(f"\nПримеры других файлов:")
            for i, other_path in enumerate(other_files[:5]):
                print(f"  {i+1}. {os.path.basename(other_path)} (расширение: {Path(other_path).suffix})")
        
    except Exception as e:
        print(f"ОШИБКА при сканировании: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция отладочного скрипта."""
    print("=== ОТЛАДОЧНЫЙ СКРИПТ СКАНИРОВАНИЯ ИЗОБРАЖЕНИЙ ===")
    print()
    
    # Можете изменить путь здесь для тестирования
    test_directories = [
        r"D:\Work\My Pictures\20130921",
        r"D:/Work/My Pictures/20130921",
        r"D:\Work\My Pictures\20221116_Dresden\Photos"
    ]
    
    for directory in test_directories:
        if os.path.exists(directory):
            debug_directory_scan(directory)
            break
    else:
        print("Ни одна из тестовых директорий не найдена.")
        print("Введите путь к директории для проверки:")
        user_path = input().strip()
        if user_path:
            debug_directory_scan(user_path)

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
