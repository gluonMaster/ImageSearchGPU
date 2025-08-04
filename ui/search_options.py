"""
Панель настроек поиска изображений.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from config import FONTS, MAX_RESULTS_LIMIT


class SearchOptionsFrame:
    """Рамка с настройками поиска."""
    
    def __init__(self, parent):
        """
        Инициализация рамки настроек.
        
        Args:
            parent: Родительский виджет
        """
        self.parent = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса рамки настроек."""
        # Основная рамка
        self.main_frame = ttk.LabelFrame(self.parent, text="Настройки поиска", padding="10")
        self.main_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Настройки количества результатов
        results_frame = ttk.Frame(self.main_frame)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(results_frame, text="Макс. результатов:", font=FONTS['default']).pack(side=tk.LEFT)
        
        self.max_results_var = tk.StringVar(value="20")
        max_results_spinbox = ttk.Spinbox(
            results_frame,
            from_=1,
            to=MAX_RESULTS_LIMIT,
            textvariable=self.max_results_var,
            width=10
        )
        max_results_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Настройки фильтрации по дате
        date_frame = ttk.Frame(self.main_frame)
        date_frame.pack(fill=tk.X)
        
        self.date_filter_var = tk.BooleanVar()
        date_checkbox = ttk.Checkbutton(
            date_frame,
            text="Фильтр по дате (дней назад):",
            variable=self.date_filter_var
        )
        date_checkbox.pack(side=tk.LEFT)
        
        self.date_days_var = tk.StringVar(value="30")
        date_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=3650,
            textvariable=self.date_days_var,
            width=10
        )
        date_spinbox.pack(side=tk.LEFT, padx=(5, 0))
    
    def get_max_results(self) -> int:
        """
        Получение максимального количества результатов.
        
        Returns:
            int: Максимальное количество результатов
        """
        try:
            return int(self.max_results_var.get())
        except ValueError:
            return 20
    
    def get_date_filter(self) -> Optional[dict]:
        """
        Получение настроек фильтра по дате.
        
        Returns:
            Optional[dict]: Настройки фильтра или None если отключен
        """
        if not self.date_filter_var.get():
            return None
        
        try:
            days = int(self.date_days_var.get())
            return {'days': days}
        except ValueError:
            return None
