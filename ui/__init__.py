"""
UI модули для приложения поиска изображений.
"""

# Импорты всех UI компонентов для удобства
from .progress_dialog import ProgressDialog
from .results_panel import ResultsPanel
from .search_options import SearchOptionsFrame
from .dialogs import PhotoPreviewDialog, MultipleFolderSelector

__all__ = [
    'ProgressDialog',
    'ResultsPanel', 
    'SearchOptionsFrame',
    'PhotoPreviewDialog',
    'MultipleFolderSelector'
]
