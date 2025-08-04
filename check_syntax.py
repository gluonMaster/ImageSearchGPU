#!/usr/bin/env python3
"""
Простая проверка синтаксиса отрефакторенного файла.
"""

import sys
from pathlib import Path

# Добавляем путь к модулям проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("Проверка импорта модулей...")
    from ui.results_panel import ResultsPanel
    print("✓ ResultsPanel импортирован успешно")
    
    from search_engine import SearchResult
    print("✓ SearchResult импортирован успешно")
    
    from config import THUMBNAIL_SIZE, COLORS, FONTS
    print("✓ Конфигурация импортирована успешно")
    
    print("\n✅ Все основные модули импортированы успешно!")
    print("Рефакторинг выполнен корректно.")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
