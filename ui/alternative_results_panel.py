"""
Альтернативная реализация панели результатов с использованием Treeview
для обхода проблем с прокруткой Canvas при большом количестве элементов.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
from typing import List
import os
import logging
from pathlib import Path

from config import THUMBNAIL_SIZE, COLORS, FONTS
from search_engine import SearchResult
from photo_saver import PhotoSaver

logger = logging.getLogger(__name__)


class AlternativeResultsPanel(ttk.Frame):
    """Альтернативная панель результатов с использованием Treeview для надежной прокрутки."""
    
    def __init__(self, parent):
        """Инициализация панели результатов."""
        super().__init__(parent)
        self.parent = parent
        self.results: List[SearchResult] = []
        self.selected_results: List[SearchResult] = []
        self.photo_saver = PhotoSaver()
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса панели результатов."""
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Панель управления выбором
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления выбором
        ttk.Button(
            self.control_frame, 
            text="Выбрать все", 
            command=self._select_all
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            self.control_frame, 
            text="Снять выбор", 
            command=self._deselect_all
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка сохранения выбранных
        self.save_selected_button = ttk.Button(
            self.control_frame,
            text="Сохранить выбранные...",
            command=self._save_selected_photos,
            state='disabled'
        )
        self.save_selected_button.pack(side=tk.RIGHT)
        
        # Метка с количеством выбранных
        self.selected_count_label = ttk.Label(
            self.control_frame,
            text="Выбрано: 0",
            font=FONTS['small']
        )
        self.selected_count_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Treeview для отображения результатов
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Настройка колонок Treeview
        columns = ('selection', 'similarity', 'name', 'path', 'size', 'modified')
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show='tree headings',
            height=20
        )
        
        # Настройка заголовков
        self.tree.heading('#0', text='#')
        self.tree.heading('selection', text='Выбрать')
        self.tree.heading('similarity', text='Схожесть')
        self.tree.heading('name', text='Имя файла')
        self.tree.heading('path', text='Путь')
        self.tree.heading('size', text='Размер')
        self.tree.heading('modified', text='Изменен')
        
        # Настройка ширины колонок
        self.tree.column('#0', width=50, minwidth=30)
        self.tree.column('selection', width=70, minwidth=50)
        self.tree.column('similarity', width=80, minwidth=60)
        self.tree.column('name', width=200, minwidth=150)
        self.tree.column('path', width=300, minwidth=200)
        self.tree.column('size', width=80, minwidth=60)
        self.tree.column('modified', width=120, minwidth=100)
        
        # Scrollbar для Treeview
        tree_scrollbar = ttk.Scrollbar(
            self.tree_frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Размещение элементов
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Привязка событий
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_click)
        self.tree.bind('<space>', self._on_space_key)
        
        # Привязка прокрутки колесом мыши
        self.tree.bind("<MouseWheel>", self._on_mousewheel)
        
        # Контекстное меню
        self._setup_context_menu()
        
        # Начальное состояние
        self._update_control_panel()
        self.show_no_results_message()
    
    def _setup_context_menu(self):
        """Настройка контекстного меню."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Открыть файл", command=self._open_selected_file)
        self.context_menu.add_command(label="Открыть папку", command=self._open_selected_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выбрать", command=self._toggle_selected_item)
        self.context_menu.add_command(label="Выбрать все", command=self._select_all)
        self.context_menu.add_command(label="Снять выбор", command=self._deselect_all)
        
        self.tree.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Показ контекстного меню."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _on_mousewheel(self, event):
        """Обработка прокрутки колесом мыши."""
        # Treeview автоматически обрабатывает прокрутку, но можем добавить кастомную логику
        pass
    
    def _on_double_click(self, event):
        """Обработка двойного клика - открытие файла."""
        selected_item = self.tree.selection()
        if selected_item:
            self._open_selected_file()
    
    def _on_click(self, event):
        """Обработка клика для выбора элементов."""
        # Определяем элемент и колонку
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)
        
        if item and column == '#1':  # Колонка выбора
            self._toggle_item_selection(item)
    
    def _on_space_key(self, event):
        """Обработка нажатия пробела для переключения выбора."""
        selected_item = self.tree.selection()
        if selected_item:
            self._toggle_item_selection(selected_item[0])
    
    def show_results(self, results: List[SearchResult]):
        """Отображение результатов поиска."""
        self.results = results
        self.selected_results = []
        self._clear_results()
        
        if not results:
            self.show_no_results_message()
            self._update_control_panel()
            return
        
        print(f"Loading {len(results)} results into Treeview...")
        
        # Добавляем результаты в Treeview
        for i, result in enumerate(results):
            # Форматируем данные для отображения
            file_size = result.file_info.get('size', result.file_info.get('file_size', 0))
            size_text = self._format_file_size(file_size)
            
            mod_time = result.file_info.get('modification_time', result.file_info.get('modified_date', ''))
            if isinstance(mod_time, str):
                mod_time_text = mod_time if mod_time else 'Неизвестно'
            else:
                mod_time_text = mod_time.strftime('%d.%m.%Y %H:%M') if mod_time else 'Неизвестно'
            
            # Добавляем элемент в дерево
            item_id = self.tree.insert(
                '', 'end',
                text=str(i + 1),
                values=(
                    '☐',  # Чекбокс (не выбран)
                    f"{result.similarity_score:.1%}",
                    Path(result.file_path).name,
                    result.file_path,
                    size_text,
                    mod_time_text
                ),
                tags=('unselected',)
            )
            
            # Промежуточное обновление для больших наборов
            if (i + 1) % 100 == 0:
                self.tree.update_idletasks()
                print(f"Loaded {i + 1} results...")
        
        print(f"All {len(results)} results loaded into Treeview")
        self._update_control_panel()
    
    def _clear_results(self):
        """Очистка текущих результатов."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def _toggle_item_selection(self, item_id):
        """Переключение выбора элемента."""
        if not item_id:
            return
        
        # Получаем текущие значения
        values = list(self.tree.item(item_id, 'values'))
        if not values:
            return
        
        # Переключаем состояние чекбокса
        if values[0] == '☐':  # Не выбран
            values[0] = '☑'  # Выбран
            self.tree.item(item_id, values=values, tags=('selected',))
        else:  # Выбран
            values[0] = '☐'  # Не выбран
            self.tree.item(item_id, values=values, tags=('unselected',))
        
        self._update_selected_results()
        self._update_control_panel()
    
    def _toggle_selected_item(self):
        """Переключение выбора текущего выделенного элемента."""
        selected_items = self.tree.selection()
        if selected_items:
            self._toggle_item_selection(selected_items[0])
    
    def _select_all(self):
        """Выбор всех результатов."""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            if values and values[0] == '☐':
                values[0] = '☑'
                self.tree.item(item, values=values, tags=('selected',))
        
        self._update_selected_results()
        self._update_control_panel()
    
    def _deselect_all(self):
        """Снятие выбора со всех результатов."""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            if values and values[0] == '☑':
                values[0] = '☐'
                self.tree.item(item, values=values, tags=('unselected',))
        
        self._update_selected_results()
        self._update_control_panel()
    
    def _update_selected_results(self):
        """Обновление списка выбранных результатов."""
        self.selected_results = []
        
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, 'values')
            if values and values[0] == '☑' and i < len(self.results):
                self.selected_results.append(self.results[i])
    
    def _update_control_panel(self):
        """Обновление панели управления."""
        selected_count = len(self.selected_results)
        self.selected_count_label.config(text=f"Выбрано: {selected_count}")
        
        # Активация/деактивация кнопки сохранения
        if selected_count > 0:
            self.save_selected_button.config(state='normal')
        else:
            self.save_selected_button.config(state='disabled')
    
    def _open_selected_file(self):
        """Открытие выбранного файла."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.tree.item(item, 'values')
        if values and len(values) > 3:
            file_path = values[3]  # Путь к файлу
            self._open_file(file_path)
    
    def _open_selected_folder(self):
        """Открытие папки выбранного файла."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.tree.item(item, 'values')
        if values and len(values) > 3:
            file_path = values[3]  # Путь к файлу
            self._open_folder(file_path)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Форматирование размера файла в читаемый вид."""
        if size_bytes < 1024:
            return f"{size_bytes} Б"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} КБ"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} МБ"
    
    def _open_file(self, file_path: str):
        """Открытие файла в приложении по умолчанию."""
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
    
    def _open_folder(self, file_path: str):
        """Открытие папки с файлом в проводнике."""
        try:
            folder_path = os.path.dirname(file_path)
            os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{e}")
    
    def show_no_results_message(self):
        """Отображение сообщения об отсутствии результатов."""
        self._clear_results()
        
        # Добавляем пустую строку с сообщением
        self.tree.insert(
            '', 'end',
            text='',
            values=('', '', 'Результаты поиска будут отображены здесь', '', '', ''),
            tags=('message',)
        )
    
    def _save_selected_photos(self):
        """Сохранение выбранных фотографий."""
        if not self.selected_results:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одной фотографии для сохранения")
            return
        
        # Выбор папки для сохранения
        destination_dir = filedialog.askdirectory(
            title="Выберите папку для сохранения фотографий"
        )
        
        if not destination_dir:
            return
        
        # Получаем пути к выбранным фотографиям
        photo_paths = [result.file_path for result in self.selected_results]
        
        # Здесь можно добавить логику сохранения, аналогичную оригинальной
        messagebox.showinfo("Информация", f"Сохранение {len(photo_paths)} фотографий в {destination_dir}")
        print(f"Would save {len(photo_paths)} photos to {destination_dir}")
