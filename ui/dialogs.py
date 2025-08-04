"""
Диалоговые окна для приложения поиска изображений.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List, Tuple
import os
import logging

from config import FONTS, COLORS, MAX_SELECTED_FOLDERS

logger = logging.getLogger(__name__)


class PhotoPreviewDialog:
    """Диалог предварительного просмотра организации фотографий."""
    
    def __init__(self, parent, organization: dict, destination_dir: str):
        """
        Инициализация диалога предпросмотра.
        
        Args:
            parent: Родительское окно
            organization: Словарь с организацией файлов по папкам
            destination_dir: Целевая директория
        """
        self.parent = parent
        self.organization = organization
        self.destination_dir = destination_dir
        self.confirmed = False
        
        self.window = tk.Toplevel(parent)
        self.window.title("Предварительный просмотр сохранения")
        self.window.geometry("700x600")  # Увеличили размер окна
        self.window.transient(parent)
        self.window.grab_set()
        
        # Устанавливаем минимальный размер окна
        self.window.minsize(600, 500)
        
        # Центрирование окна
        self.window.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 30
        ))
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога."""
        # Основная рамка
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Предварительный просмотр организации фотографий",
            font=FONTS['header']
        )
        title_label.pack(pady=(0, 10))
        
        # Информация о целевой папке
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(dest_frame, text="Папка назначения:", font=FONTS['default']).pack(anchor=tk.W)
        ttk.Label(dest_frame, text=self.destination_dir, font=FONTS['small'], 
                 foreground=COLORS['text_secondary']).pack(anchor=tk.W, padx=(20, 0))
        
        # Список папок и файлов
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Создание дерева с прокруткой
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Настройка колонок
        self.tree["columns"] = ("count",)
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("count", width=100, minwidth=80)
        self.tree.heading("#0", text="Папка/Файл", anchor=tk.W)
        self.tree.heading("count", text="Количество", anchor=tk.CENTER)
        
        # Заполнение дерева
        self._populate_tree()
        
        # Разделитель перед кнопками
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 10))
        
        # Информационная строка
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_files = sum(len(files) for files in self.organization.values())
        info_text = f"Будет сохранено {total_files} файлов в {len(self.organization)} папок"
        ttk.Label(
            info_frame, 
            text=info_text, 
            font=FONTS.get('default', ('Arial', 10)),
            foreground=COLORS.get('text_primary', 'black')
        ).pack()
        
        # Кнопки в отдельной рамке с явным размером
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Создаем кнопки с увеличенным размером
        cancel_button = ttk.Button(
            buttons_frame,
            text="❌ Отмена",
            command=self._on_cancel,
            width=15
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        confirm_button = ttk.Button(
            buttons_frame,
            text="✅ Продолжить",
            command=self._on_confirm,
            width=15
        )
        confirm_button.pack(side=tk.RIGHT)
        
        # Делаем кнопку "Продолжить" кнопкой по умолчанию
        confirm_button.focus_set()
        self.window.bind('<Return>', lambda e: self._on_confirm())
        self.window.bind('<Escape>', lambda e: self._on_cancel())
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _populate_tree(self):
        """Заполнение дерева организации файлов."""
        total_files = 0
        
        for folder, files in sorted(self.organization.items()):
            total_files += len(files)
            
            # Добавляем папку
            folder_item = self.tree.insert("", tk.END, text=f"📁 {folder}", values=(f"{len(files)} файлов",))
            
            # Добавляем файлы в папку (показываем только первые 10 для экономии места)
            for i, filename in enumerate(files[:10]):
                self.tree.insert(folder_item, tk.END, text=f"  📷 {filename}", values=("",))
            
            if len(files) > 10:
                self.tree.insert(folder_item, tk.END, text=f"  ... и еще {len(files) - 10} файлов", values=("",))
        
        # Добавляем общую информацию в начало
        summary_item = self.tree.insert("", 0, text="📊 Сводка", values=(f"{total_files} файлов",))
        self.tree.insert(summary_item, tk.END, text=f"  Всего папок: {len(self.organization)}", values=("",))
        self.tree.insert(summary_item, tk.END, text=f"  Всего файлов: {total_files}", values=("",))
        
        # Разворачиваем сводку
        self.tree.item(summary_item, open=True)
    
    def _on_confirm(self):
        """Подтверждение операции."""
        logger.info("PhotoPreviewDialog: Пользователь подтвердил операцию")
        print("DEBUG: PhotoPreviewDialog - подтверждение операции")
        self.confirmed = True
        self.window.destroy()
    
    def _on_cancel(self):
        """Отмена операции."""
        logger.info("PhotoPreviewDialog: Пользователь отменил операцию")
        print("DEBUG: PhotoPreviewDialog - отмена операции")
        self.confirmed = False
        self.window.destroy()
    
    def show_modal(self) -> bool:
        """
        Показать диалог в модальном режиме.
        
        Returns:
            bool: True если пользователь подтвердил операцию
        """
        self.window.wait_window()
        return self.confirmed


class MultipleFolderSelector:
    """Диалог для выбора множественных папок для индексации."""
    
    def __init__(self, parent, initial_folders: List[str] = None):
        """
        Инициализация селектора папок.
        
        Args:
            parent: Родительское окно
            initial_folders: Список изначально выбранных папок
        """
        self.parent = parent
        self.selected_folders = initial_folders.copy() if initial_folders else []
        self.folder_stats = {}  # Статистика по папкам {path: count}
        self.recursive = True
        self.confirmed = False
        
        self.window = tk.Toplevel(parent)
        self.window.title("Выбор папок для индексации")
        self.window.geometry("800x650")  # Увеличили размер окна
        self.window.transient(parent)
        self.window.grab_set()
        
        # Устанавливаем минимальный размер окна
        self.window.minsize(700, 550)
        
        # Центрирование окна
        self.window.geometry("+{}+{}".format(
            parent.winfo_rootx() + 30,
            parent.winfo_rooty() + 30
        ))
        
        self._setup_ui()
        self._update_stats()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога."""
        # Основная рамка
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="Выбор папок для индексации",
            font=FONTS['header']
        )
        title_label.pack(pady=(0, 10))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Добавить папку",
            command=self._add_folder
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Очистить все",
            command=self._clear_all_folders
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Список выбранных папок
        list_label = ttk.Label(main_frame, text="Выбранные папки:")
        list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Фрейм для списка с прокруткой
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview для отображения папок
        columns = ('path', 'count', 'status')
        self.folders_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            height=12
        )
        
        # Настройка колонок
        self.folders_tree.heading('#0', text='☑')
        self.folders_tree.heading('path', text='Путь к папке')
        self.folders_tree.heading('count', text='Изображений')
        self.folders_tree.heading('status', text='Статус')
        
        self.folders_tree.column('#0', width=30, minwidth=30)
        self.folders_tree.column('path', width=350, minwidth=200)
        self.folders_tree.column('count', width=100, minwidth=80)
        self.folders_tree.column('status', width=100, minwidth=80)
        
        # Прокрутка для списка
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.folders_tree.yview)
        self.folders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.folders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязки событий
        self.folders_tree.bind('<Button-3>', self._on_right_click)
        self.folders_tree.bind('<Delete>', self._on_delete_key)
        self.folders_tree.bind('<Double-Button-1>', self._on_double_click)
        
        # Чекбокс для рекурсивного поиска
        recursive_frame = ttk.Frame(main_frame)
        recursive_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.recursive_var = tk.BooleanVar(value=self.recursive)
        recursive_check = ttk.Checkbutton(
            recursive_frame,
            text="Включать подпапки",
            variable=self.recursive_var,
            command=self._on_recursive_changed
        )
        recursive_check.pack(side=tk.LEFT)
        
        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(
            stats_frame,
            text="Всего изображений: 0",
            font=FONTS['default']
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Разделитель перед кнопками действий
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(15, 10))
        
        # Информационная строка перед кнопками
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = f"Выбрано папок: {len(self.selected_folders)}"
        self.info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=FONTS.get('default', ('Arial', 10)),
            foreground=COLORS.get('text_primary', 'black')
        )
        self.info_label.pack()
        
        # Кнопки действий с улучшенным отображением
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Создаем кнопки с увеличенным размером и иконками
        cancel_button = ttk.Button(
            action_frame,
            text="❌ Отмена",
            command=self._on_cancel,
            width=15
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        confirm_button = ttk.Button(
            action_frame,
            text="🔍 Построить индекс",
            command=self._on_confirm,
            width=20
        )
        confirm_button.pack(side=tk.RIGHT)
        
        # Делаем кнопку "Построить индекс" кнопкой по умолчанию
        confirm_button.focus_set()
        self.window.bind('<Return>', lambda e: self._on_confirm())
        self.window.bind('<Escape>', lambda e: self._on_cancel())
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Удалить", command=self._remove_selected_folder)
        self.context_menu.add_command(label="Открыть в проводнике", command=self._open_in_explorer)
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _add_folder(self):
        """Добавление новой папки."""
        if len(self.selected_folders) >= MAX_SELECTED_FOLDERS:
            messagebox.showwarning(
                "Предупреждение",
                f"Максимальное количество папок: {MAX_SELECTED_FOLDERS}"
            )
            return
        
        directory = filedialog.askdirectory(
            title="Выберите папку с изображениями",
            parent=self.window
        )
        
        if directory and directory not in self.selected_folders:
            # Проверка на вложенные папки
            is_nested = False
            folders_to_remove = []
            
            for existing_folder in self.selected_folders:
                if directory.startswith(existing_folder + os.sep):
                    messagebox.showinfo(
                        "Информация",
                        f"Папка уже включена в: {existing_folder}"
                    )
                    is_nested = True
                    break
                elif existing_folder.startswith(directory + os.sep):
                    folders_to_remove.append(existing_folder)
            
            if not is_nested:
                # Удаляем вложенные папки
                for folder in folders_to_remove:
                    self.selected_folders.remove(folder)
                
                self.selected_folders.append(directory)
                self._refresh_folder_list()
                self._update_stats()
    
    def _clear_all_folders(self):
        """Очистка всех выбранных папок."""
        if self.selected_folders and messagebox.askyesno(
            "Подтверждение", 
            "Удалить все выбранные папки?"
        ):
            self.selected_folders.clear()
            self.folder_stats.clear()
            self._refresh_folder_list()
            self._update_stats()
    
    def _refresh_folder_list(self):
        """Обновление списка папок в интерфейсе."""
        # Очистка списка
        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)
        
        # Добавление папок
        for folder_path in self.selected_folders:
            count = self.folder_stats.get(folder_path, "...")
            status = "Готова" if count != "..." else "Подсчет..."
            
            self.folders_tree.insert(
                '',
                'end',
                text='☑',
                values=(folder_path, count, status)
            )
        
        # Обновляем информационную строку
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"Выбрано папок: {len(self.selected_folders)}")
    
    def _update_stats(self):
        """Обновление статистики по папкам."""
        def count_worker():
            from file_scanner import FileScanner
            scanner = FileScanner()
            
            total_images = 0
            for folder_path in self.selected_folders:
                try:
                    if os.path.exists(folder_path):
                        files = scanner.scan_directory(
                            folder_path, 
                            recursive=self.recursive_var.get()
                        )
                        count = len(files)
                        self.folder_stats[folder_path] = count
                        total_images += count
                    else:
                        self.folder_stats[folder_path] = "Не найдена"
                except Exception as e:
                    logger.error(f"Ошибка при подсчете файлов в {folder_path}: {e}")
                    self.folder_stats[folder_path] = "Ошибка"
            
            # Обновление интерфейса в главном потоке
            self.window.after(0, self._on_stats_updated, total_images)
        
        if self.selected_folders:
            threading.Thread(target=count_worker, daemon=True).start()
        else:
            self._on_stats_updated(0)
    
    def _on_stats_updated(self, total_images: int):
        """Обработка обновления статистики."""
        self.stats_label.config(text=f"Всего изображений: {total_images:,}")
        self._refresh_folder_list()
    
    def _on_recursive_changed(self):
        """Обработка изменения настройки рекурсивного поиска."""
        self.recursive = self.recursive_var.get()
        if self.selected_folders:
            self._update_stats()
    
    def _on_right_click(self, event):
        """Обработка правого клика."""
        item = self.folders_tree.identify_row(event.y)
        if item:
            self.folders_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _on_delete_key(self, event):
        """Обработка клавиши Delete."""
        self._remove_selected_folder()
    
    def _on_double_click(self, event):
        """Обработка двойного клика."""
        self._open_in_explorer()
    
    def _remove_selected_folder(self):
        """Удаление выбранной папки."""
        selection = self.folders_tree.selection()
        if selection:
            item = selection[0]
            values = self.folders_tree.item(item, 'values')
            folder_path = values[0]
            
            if folder_path in self.selected_folders:
                self.selected_folders.remove(folder_path)
                if folder_path in self.folder_stats:
                    del self.folder_stats[folder_path]
                self._refresh_folder_list()
                self._update_stats()
    
    def _open_in_explorer(self):
        """Открытие папки в проводнике."""
        selection = self.folders_tree.selection()
        if selection:
            item = selection[0]
            values = self.folders_tree.item(item, 'values')
            folder_path = values[0]
            
            if os.path.exists(folder_path):
                os.startfile(folder_path)
    
    def _on_confirm(self):
        """Подтверждение выбора папок."""
        logger.info(f"MultipleFolderSelector: Пользователь подтвердил выбор {len(self.selected_folders)} папок")
        print(f"DEBUG: MultipleFolderSelector - подтверждение выбора {len(self.selected_folders)} папок")
        
        if not self.selected_folders:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну папку")
            return
        
        self.recursive = self.recursive_var.get()
        self.confirmed = True
        self.window.destroy()
    
    def _on_cancel(self):
        """Отмена выбора папок."""
        logger.info("MultipleFolderSelector: Пользователь отменил выбор папок")
        print("DEBUG: MultipleFolderSelector - отмена выбора папок")
        self.confirmed = False
        self.window.destroy()
    
    def show_modal(self) -> Tuple[bool, List[str], bool]:
        """
        Показать диалог в модальном режиме.
        
        Returns:
            Tuple[bool, List[str], bool]: (подтверждено, список_папок, рекурсивный_поиск)
        """
        self.window.wait_window()
        return self.confirmed, self.selected_folders, self.recursive
