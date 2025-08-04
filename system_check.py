#!/usr/bin/env python3
"""
Скрипт диагностики системы для Image Search Application.
Проверяет все компоненты и дает рекомендации по оптимизации.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def print_header(title):
    """Печать заголовка раздела."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_section(title):
    """Печать подзаголовка."""
    print(f"\n--- {title} ---")

def check_system_info():
    """Проверка информации о системе."""
    print_header("ИНФОРМАЦИЯ О СИСТЕМЕ")
    
    print(f"Операционная система: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.machine()}")
    print(f"Процессор: {platform.processor()}")
    print(f"Python версия: {sys.version}")
    print(f"Python путь: {sys.executable}")

def check_python_environment():
    """Проверка Python окружения."""
    print_header("PYTHON ОКРУЖЕНИЕ")
    
    # Проверка виртуального окружения
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Виртуальное окружение: Активно")
        print(f"   Путь: {sys.prefix}")
    else:
        print("⚠️  Виртуальное окружение: Не активно (используется глобальное)")
    
    # Проверка pip
    try:
        import pip
        print(f"✅ pip версия: {pip.__version__}")
    except ImportError:
        print("❌ pip не найден")

def check_memory():
    """Проверка памяти системы."""
    print_header("ПАМЯТЬ СИСТЕМЫ")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        print(f"Общая память: {memory.total / (1024**3):.1f} ГБ")
        print(f"Доступная память: {memory.available / (1024**3):.1f} ГБ")
        print(f"Использовано: {memory.percent:.1f}%")
        print(f"Свободно: {memory.free / (1024**3):.1f} ГБ")
        
        # Оценка достаточности памяти
        available_gb = memory.available / (1024**3)
        if available_gb >= 6:
            print("✅ Отлично! Достаточно памяти для больших коллекций (70k+ изображений)")
        elif available_gb >= 4:
            print("✅ Хорошо! Подходит для средних коллекций (до 25k изображений)")
        elif available_gb >= 2:
            print("⚠️  Ограниченно. Подходит для небольших коллекций (до 8k изображений)")
        else:
            print("❌ Недостаточно памяти. Рекомендуется освободить ресурсы")
            
    except ImportError:
        print("❌ psutil не установлен - невозможно проверить память")

def check_gpu():
    """Проверка GPU возможностей."""
    print_header("GPU ВОЗМОЖНОСТИ")
    
    try:
        import torch
        print(f"PyTorch версия: {torch.__version__}")
        
        # Проверка CUDA
        cuda_available = torch.cuda.is_available()
        print(f"CUDA доступна: {'✅ Да' if cuda_available else '❌ Нет'}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"Количество GPU устройств: {device_count}")
            
            # Информация о каждом GPU
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / (1024**3)
                compute_capability = f"{props.major}.{props.minor}"
                
                print(f"\nGPU {i}: {gpu_name}")
                print(f"   Память: {memory_gb:.1f} ГБ")
                print(f"   Compute Capability: {compute_capability}")
                
                # Специальные рекомендации для популярных карт
                if "2060" in gpu_name:
                    print("   🎯 RTX 2060 - отлично подходит для ускорения!")
                elif "3060" in gpu_name or "3070" in gpu_name or "3080" in gpu_name or "3090" in gpu_name:
                    print("   🚀 RTX 30xx - великолепная производительность!")
                elif "4060" in gpu_name or "4070" in gpu_name or "4080" in gpu_name or "4090" in gpu_name:
                    print("   🔥 RTX 40xx - максимальная производительность!")
                elif "GTX" in gpu_name:
                    print("   ✅ GTX карта - хорошее ускорение")
                    
            print(f"\nCUDA версия PyTorch: {torch.version.cuda}")
            
            # Тест GPU
            try:
                test_tensor = torch.randn(100, 100).cuda()
                print("✅ GPU тест прошел успешно")
            except Exception as e:
                print(f"⚠️  Проблема с GPU тестом: {e}")
                
        else:
            print("\nГPU не обнаружен или CUDA недоступна.")
            print("Приложение будет работать в CPU режиме (медленнее).")
            
    except ImportError:
        print("❌ PyTorch не установлен")

def check_required_packages():
    """Проверка необходимых пакетов."""
    print_header("ПРОВЕРКА ПАКЕТОВ")
    
    required_packages = {
        'torch': 'PyTorch - основа для нейронных сетей',
        'torchvision': 'Torchvision - обработка изображений',
        'sentence_transformers': 'Sentence Transformers - CLIP модели',
        'PIL': 'Pillow - работа с изображениями',
        'numpy': 'NumPy - численные вычисления',
        'psutil': 'PSUtil - мониторинг системы',
        'tkinter': 'Tkinter - графический интерфейс'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'PIL':
                import PIL
                version = PIL.__version__
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'неизвестно')
            
            print(f"✅ {package} ({version}) - {description}")
            
        except ImportError:
            print(f"❌ {package} - ОТСУТСТВУЕТ - {description}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Отсутствующие пакеты: {', '.join(missing_packages)}")
        print("Запустите install.bat для установки всех зависимостей")
    else:
        print("\n✅ Все необходимые пакеты установлены!")

def check_application_files():
    """Проверка файлов приложения."""
    print_header("ФАЙЛЫ ПРИЛОЖЕНИЯ")
    
    required_files = {
        'main.py': 'Главный файл приложения',
        'search_engine.py': 'Поисковый движок',
        'image_analyzer.py': 'Анализатор изображений',
        'cache_manager.py': 'Менеджер кэша',
        'file_scanner.py': 'Сканер файлов',
        'gui_components.py': 'Компоненты интерфейса',
        'config.py': 'Конфигурация',
        'requirements.txt': 'Список зависимостей'
    }
    
    missing_files = []
    
    for filename, description in required_files.items():
        if Path(filename).exists():
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} - ОТСУТСТВУЕТ - {description}")
            missing_files.append(filename)
    
    # Проверка папки cache
    if Path('cache').exists():
        print("✅ cache/ - папка для кэша")
        
        # Статистика кэша
        cache_files = list(Path('cache').glob('*.pkl'))
        if cache_files:
            total_size = sum(f.stat().st_size for f in cache_files)
            print(f"   Файлов кэша: {len(cache_files)}")
            print(f"   Размер кэша: {total_size / (1024*1024):.1f} МБ")
        else:
            print("   Кэш пуст (первый запуск)")
    else:
        print("⚠️  cache/ - папка будет создана при первом запуске")
    
    if missing_files:
        print(f"\n❌ Отсутствующие файлы: {', '.join(missing_files)}")
        print("Убедитесь, что все файлы приложения скопированы")
    else:
        print("\n✅ Все файлы приложения на месте!")

def check_performance_settings():
    """Проверка настроек производительности."""
    print_header("НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ")
    
    try:
        # Импортируем конфиг для проверки настроек
        sys.path.insert(0, '.')
        import config
        
        print(f"Размер чанка: {getattr(config, 'CHUNK_SIZE', 'не задан')}")
        print(f"Минимальная память: {getattr(config, 'MIN_MEMORY_GB', 'не задана')} ГБ")
        print(f"Порог предупреждения: {getattr(config, 'WARNING_MEMORY_GB', 'не задан')} ГБ")
        print(f"Размер батча CLIP: {getattr(config, 'CLIP_BATCH_SIZE', 'не задан')}")
        
        # Рекомендации
        try:
            import psutil
            available_gb = psutil.virtual_memory().available / (1024**3)
            chunk_size = getattr(config, 'CHUNK_SIZE', 5000)
            
            if available_gb < 4 and chunk_size > 3000:
                print("\n⚠️  РЕКОМЕНДАЦИЯ: Уменьшите CHUNK_SIZE до 2000-3000 для вашей системы")
            elif available_gb >= 8 and chunk_size < 5000:
                print("\n✅ РЕКОМЕНДАЦИЯ: Можно увеличить CHUNK_SIZE до 7000-8000 для лучшей производительности")
            else:
                print("\n✅ Настройки оптимальны для вашей системы")
                
        except:
            pass
            
    except ImportError:
        print("❌ Не удалось загрузить config.py")

def performance_recommendations():
    """Рекомендации по производительности."""
    print_header("РЕКОМЕНДАЦИИ ПО ПРОИЗВОДИТЕЛЬНОСТИ")
    
    try:
        import psutil
        import torch
        
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        total_gb = memory.total / (1024**3)
        
        print("📊 Анализ системы:")
        print(f"   Общая память: {total_gb:.1f} ГБ")
        print(f"   Доступная память: {available_gb:.1f} ГБ")
        print(f"   GPU: {'Да' if torch.cuda.is_available() else 'Нет'}")
        
        print("\n🎯 Рекомендации:")
        
        if available_gb >= 8:
            print("   ✅ У вас достаточно памяти для больших коллекций")
            print("   ✅ Можете обрабатывать 50k+ изображений одновременно")
            print("   💡 Рекомендуется увеличить CHUNK_SIZE до 7000")
            
        elif available_gb >= 4:
            print("   ✅ Подходит для средних коллекций (до 25k изображений)")
            print("   💡 Стандартные настройки оптимальны")
            
        elif available_gb >= 2:
            print("   ⚠️  Ограниченная память - подходит для небольших коллекций")
            print("   💡 Рекомендуется уменьшить CHUNK_SIZE до 2000-3000")
            print("   💡 Закройте другие приложения перед индексацией")
            
        else:
            print("   ❌ Недостаточно памяти для комфортной работы")
            print("   💡 Критично: освободите память или добавьте ОЗУ")
            print("   💡 Уменьшите CHUNK_SIZE до 1000")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"\n🚀 GPU ускорение:")
            print(f"   GPU: {gpu_name}")
            print(f"   Память GPU: {gpu_memory:.1f} ГБ")
            
            if "RTX" in gpu_name:
                print("   ✅ Отличная производительность! Ожидайте 5-10x ускорение")
            elif "GTX" in gpu_name:
                print("   ✅ Хорошее ускорение! Ожидайте 3-5x ускорение")
            else:
                print("   ✅ GPU ускорение доступно")
                
        else:
            print(f"\n💻 CPU режим:")
            print("   ⚠️  Обработка будет медленнее")
            print("   💡 Рассмотрите возможность использования NVIDIA GPU")
        
        print(f"\n📁 Рекомендуемые размеры коллекций:")
        if torch.cuda.is_available() and available_gb >= 6:
            print("   • До 10k изображений: ~10-15 минут")
            print("   • До 25k изображений: ~30-45 минут") 
            print("   • До 70k изображений: ~2-3 часа")
        elif available_gb >= 4:
            print("   • До 5k изображений: ~15-20 минут")
            print("   • До 15k изображений: ~1-1.5 часа")
            print("   • До 30k изображений: ~3-4 часа")
        else:
            print("   • До 3k изображений: ~20-30 минут")
            print("   • До 8k изображений: ~1-2 часа")
            print("   • Больше 8k: разбейте на части")
            
    except ImportError:
        print("Установите psutil и torch для получения рекомендаций")

def main():
    """Основная функция диагностики."""
    print("🔍 Диагностика системы Image Search Application")
    print("Эта утилита проверит готовность системы к работе\n")
    
    # Выполнение всех проверок
    check_system_info()
    check_python_environment()
    check_memory()
    check_gpu()
    check_required_packages()
    check_application_files()
    check_performance_settings()
    performance_recommendations()
    
    # Итоговое заключение
    print_header("ИТОГОВОЕ ЗАКЛЮЧЕНИЕ")
    
    # Простая оценка готовности
    issues = []
    
    try:
        import torch, torchvision, sentence_transformers, PIL, numpy, psutil
        print("✅ Все основные пакеты установлены")
    except ImportError as e:
        issues.append(f"Отсутствуют пакеты: {e}")
    
    if not Path('main.py').exists():
        issues.append("Отсутствует main.py")
    
    try:
        import psutil
        if psutil.virtual_memory().available < 1024**3:  # < 1GB
            issues.append("Критически мало памяти")
    except:
        pass
    
    if not issues:
        print("🎉 СИСТЕМА ГОТОВА К РАБОТЕ!")
        print("\nДля запуска используйте:")
        print("   • start_app.bat (если создан установщиком)")
        print("   • python main.py")
        
        try:
            import torch
            if torch.cuda.is_available():
                print("\n🚀 GPU ускорение доступно - ожидайте высокую производительность!")
            else:
                print("\n💻 Работа в CPU режиме - производительность стандартная")
        except:
            pass
            
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ:")
        for issue in issues:
            print(f"   • {issue}")
        print("\nРекомендуется запустить install.bat для исправления")
    
    print(f"\n{'='*60}")
    input("Нажмите Enter для завершения...")

if __name__ == "__main__":
    main()
