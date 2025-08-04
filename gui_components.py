"""
Модуль с вспомогательными GUI компонентами для приложения поиска изображений.
Теперь служит как слой совместимости, импортирующий компоненты из модульной структуры ui/.
"""

# Импортируем все компоненты из новой модульной структуры
from ui import (
    ProgressDialog,
    ResultsPanel,
    SearchOptionsFrame,
    PhotoPreviewDialog,
    MultipleFolderSelector
)

# Обеспечиваем обратную совместимость
__all__ = [
    'ProgressDialog',
    'ResultsPanel',
    'SearchOptionsFrame', 
    'PhotoPreviewDialog',
    'MultipleFolderSelector'
]