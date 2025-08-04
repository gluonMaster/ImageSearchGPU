"""
Диалог прогресса для длительных операций.
"""

import tkinter as tk
from tkinter import ttk
from config import FONTS


class ProgressDialog:
    """Диалоговое окно для отображения прогресса выполнения операций."""
    
    def __init__(self, parent, title: str = "Выполнение операции"):
        """
        Инициализация диалога прогресса.
        
        Args:
            parent: Родительское окно
            title: Заголовок диалога
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрирование окна
        self.window.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.cancelled = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога."""
        # Основная рамка
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Метка статуса
        self.status_label = ttk.Label(
            main_frame, 
            text="Инициализация...",
            font=FONTS['default']
        )
        self.status_label.pack(pady=(0, 10))
        
        # Прогресс-бар
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Метка процентов
        self.percent_label = ttk.Label(
            main_frame,
            text="0%",
            font=FONTS['small']
        )
        self.percent_label.pack(pady=(0, 10))
        
        # Кнопка отмены
        self.cancel_button = ttk.Button(
            main_frame,
            text="Отмена",
            command=self._on_cancel
        )
        self.cancel_button.pack()
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """
        Обновление прогресса выполнения.
        
        Args:
            current: Текущее значение
            total: Максимальное значение
            message: Сообщение о состоянии
        """
        if total > 0:
            progress = int((current / total) * 100)
        else:
            progress = 0
        
        # Обновление в главном потоке
        self.window.after(0, self._update_ui, progress, message)
    
    def _update_ui(self, progress: int, message: str):
        """Обновление UI в главном потоке."""
        self.progress_var.set(progress)
        self.percent_label.config(text=f"{progress}%")
        if message:
            self.status_label.config(text=message)
    
    def _on_cancel(self):
        """Обработка отмены операции."""
        self.cancelled = True
        self.window.destroy()
    
    def close(self):
        """Закрытие диалога."""
        self.window.destroy()
    
    def is_cancelled(self) -> bool:
        """Проверка, была ли операция отменена."""
        return self.cancelled
