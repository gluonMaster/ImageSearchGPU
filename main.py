"""
Главный модуль приложения для поиска изображений.
Содержит основное окно приложения и управление пользовательским интерфейсом.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_search.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

from search_engine import SearchEngine
from gui_components import ProgressDialog, ResultsPanel, SearchOptionsFrame
from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, 
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLORS, FONTS
)

logger = logging.getLogger(__name__)

class ImageSearchApp:
    """Главный класс приложения для поиска изображений."""
    
    def __init__(self):
        """Инициализация приложения."""
        self.root = tk.Tk()
        self.search_engine = SearchEngine()
        self.current_directories = []  # Изменено на список папок
        self.recursive_search = True   # Настройка рекурсивного поиска
        
        self._setup_ui()
        self._setup_bindings()
        self._load_last_folders()  # Загрузка последних выбранных папок
        
        logger.info(f"Приложение {APP_NAME} v{APP_VERSION} запущено")
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Настройка главного окна
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Центрирование окна на экране
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Создание основных элементов интерфейса
        self._create_menu()
        self._create_toolbar()
        self._create_search_panel()
        self._create_options_panel()
        self._create_results_panel()
        self._create_status_bar()
        
        # Начальное состояние
        self._update_ui_state()
    
    def _create_menu(self):
        """Создание главного меню."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выбрать папки...", command=self._select_directories)
        file_menu.add_separator()
        file_menu.add_command(label="Очистить кэш", command=self._clear_cache)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Обновить индекс", command=self._rebuild_index)
        view_menu.add_command(label="Статистика", command=self._show_stats)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_toolbar(self):
        """Создание панели инструментов."""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Выбор папок
        ttk.Label(toolbar_frame, text="Папки для поиска:", font=FONTS['default']).pack(side=tk.LEFT)
        
        self.directories_var = tk.StringVar()
        directory_entry = ttk.Entry(
            toolbar_frame,
            textvariable=self.directories_var,
            state='readonly',
            font=FONTS['default']
        )
        directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        browse_button = ttk.Button(
            toolbar_frame,
            text="Выбрать папки...",
            command=self._select_directories
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.build_index_button = ttk.Button(
            toolbar_frame,
            text="Построить индекс",
            command=self._build_index
        )
        self.build_index_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_search_panel(self):
        """Создание панели поиска."""
        search_frame = ttk.LabelFrame(self.root, text="Поиск изображений", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поле ввода поискового запроса
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Описание:", font=FONTS['default']).pack(side=tk.LEFT)
        
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(
            input_frame,
            textvariable=self.query_var,
            font=FONTS['default']
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.search_button = ttk.Button(
            input_frame,
            text="Найти",
            command=self._perform_search
        )
        self.search_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Примеры запросов
        examples_frame = ttk.Frame(search_frame)
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(
            examples_frame,
            text="Примеры запросов: кот, собака на улице, закат, семейное фото, праздник",
            font=FONTS['small'],
            foreground=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
    
    def _create_options_panel(self):
        """Создание панели настроек."""
        self.options_frame = SearchOptionsFrame(self.root)
    
    def _create_results_panel(self):
        """Создание панели результатов."""
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_panel = ResultsPanel(results_frame)
    
    def _create_status_bar(self):
        """Создание строки состояния."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Выберите папку с изображениями.")
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=FONTS['small'],
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Индикатор статуса индекса
        self.index_status_var = tk.StringVar()
        self.index_status_var.set("Индекс не построен")
        
        index_status_label = ttk.Label(
            status_frame,
            textvariable=self.index_status_var,
            font=FONTS['small'],
            relief=tk.SUNKEN,
            width=20
        )
        index_status_label.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def _setup_bindings(self):
        """Настройка привязок клавиш."""
        # Enter в поле поиска запускает поиск
        self.query_entry.bind('<Return>', lambda e: self._perform_search())
        
        # Горячие клавиши
        self.root.bind('<Control-o>', lambda e: self._select_directories())
        self.root.bind('<Control-f>', lambda e: self.query_entry.focus_set())
        self.root.bind('<F5>', lambda e: self._rebuild_index())
    
    def _update_ui_state(self):
        """Обновление состояния элементов интерфейса."""
        has_directories = bool(self.current_directories)
        index_ready = self.search_engine.is_ready()
        
        # Состояние кнопок
        self.build_index_button.config(state='normal' if has_directories else 'disabled')
        self.search_button.config(state='normal' if index_ready else 'disabled')
        self.query_entry.config(state='normal' if index_ready else 'disabled')
        
        # Статус индекса
        if index_ready:
            stats = self.search_engine.get_index_stats_multiple_folders()
            total_images = stats.get('total_images', 0)
            total_folders = stats.get('total_folders', 0)
            self.index_status_var.set(f"Индекс: {total_images} изображений из {total_folders} папок")
        else:
            self.index_status_var.set("Индекс не построен")
    
    def _select_directories(self):
        """Выбор папок для поиска изображений."""
        from gui_components import MultipleFolderSelector
        
        # Создаем диалог выбора папок
        selector = MultipleFolderSelector(self.root, self.current_directories)
        confirmed, selected_folders, recursive = selector.show_modal()
        
        if confirmed and selected_folders:
            self.current_directories = selected_folders
            self.recursive_search = recursive
            
            # Обновляем отображение выбранных папок
            self._update_directories_display()
            
            # Сохраняем конфигурацию
            self.search_engine.cache_manager.save_multiple_folders_config(
                selected_folders, recursive
            )
            
            # Очистка текущего индекса
            self.search_engine.clear_index()
            self.results_panel.show_no_results_message()
            
            self._update_ui_state()
            logger.info(f"Выбрано {len(selected_folders)} папок для индексации")
    
    def _update_directories_display(self):
        """Обновление отображения выбранных папок."""
        if not self.current_directories:
            self.directories_var.set("Папки не выбраны")
            self.status_var.set("Готов к работе")
        elif len(self.current_directories) == 1:
            self.directories_var.set(self.current_directories[0])
            self.status_var.set(f"Выбрана папка: {self.current_directories[0]}")
        else:
            folder_names = [Path(folder).name for folder in self.current_directories]
            display_text = f"{len(self.current_directories)} папок: {', '.join(folder_names[:3])}"
            if len(self.current_directories) > 3:
                display_text += f" и еще {len(self.current_directories) - 3}..."
            
            self.directories_var.set(display_text)
            self.status_var.set(f"Выбрано {len(self.current_directories)} папок для индексации")
    
    def _load_last_folders(self):
        """Загрузка последних выбранных папок."""
        try:
            config = self.search_engine.cache_manager.load_multiple_folders_config()
            if config:
                self.current_directories = config.get('folder_paths', [])
                self.recursive_search = config.get('recursive', True)
                self._update_directories_display()
                self._update_ui_state()
                logger.info(f"Загружено {len(self.current_directories)} папок из настроек")
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек папок: {e}")
    
    def _select_directory(self):
        """Старый метод выбора одной папки (для совместимости)."""
        directory = filedialog.askdirectory(
            title="Выберите папку с изображениями",
            initialdir=self.current_directories[0] if self.current_directories else str(Path.home())
        )
        
        if directory:
            self.current_directories = [directory]
            self.recursive_search = True
            self._update_directories_display()
            
            # Очистка текущего индекса
            self.search_engine.clear_index()
            self.results_panel.show_no_results_message()
            
            self._update_ui_state()
            logger.info(f"Выбрана директория: {directory}")
    
    def _build_index(self):
        """Построение индекса изображений."""
        if not self.current_directories:
            messagebox.showwarning("Предупреждение", "Сначала выберите папки с изображениями")
            return
        
        # Получение настроек
        date_filter = self.options_frame.get_date_filter()
        
        # Запуск построения индекса в отдельном потоке
        def build_worker():
            progress_dialog = ProgressDialog(self.root, "Построение индекса")
            
            def progress_callback(current, total, message):
                if not progress_dialog.is_cancelled():
                    progress_dialog.update_progress(current, total, message)
            
            try:
                success = self.search_engine.build_index_multiple_folders(
                    self.current_directories,
                    recursive=self.recursive_search,
                    date_filter=date_filter,
                    progress_callback=progress_callback
                )
                
                if success and not progress_dialog.is_cancelled():
                    self.root.after(0, self._on_index_built_success)
                elif progress_dialog.is_cancelled():
                    self.root.after(0, self._on_index_cancelled)
                else:
                    self.root.after(0, self._on_index_built_error)
                    
            except Exception as e:
                logger.error(f"Ошибка при построении индекса: {e}")
                self.root.after(0, lambda: self._on_index_built_error(str(e)))
            finally:
                progress_dialog.close()
        
        thread = threading.Thread(target=build_worker, daemon=True)
        thread.start()
    
    def _rebuild_index(self):
        """Принудительная перестройка индекса."""
        if not self.current_directories:
            messagebox.showwarning("Предупреждение", "Сначала выберите папки с изображениями")
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            "Перестроить индекс заново? Это может занять время."
        )
        
        if result:
            # Запуск перестройки в отдельном потоке
            def rebuild_worker():
                progress_dialog = ProgressDialog(self.root, "Перестройка индекса")
                
                def progress_callback(current, total, message):
                    if not progress_dialog.is_cancelled():
                        progress_dialog.update_progress(current, total, message)
                
                try:
                    date_filter = self.options_frame.get_date_filter()
                    success = self.search_engine.build_index_multiple_folders(
                        self.current_directories,
                        recursive=self.recursive_search,
                        date_filter=date_filter,
                        progress_callback=progress_callback,
                        force_rebuild=True
                    )
                    
                    if success and not progress_dialog.is_cancelled():
                        self.root.after(0, self._on_index_built_success)
                    elif progress_dialog.is_cancelled():
                        self.root.after(0, self._on_index_cancelled)
                    else:
                        self.root.after(0, self._on_index_built_error)
                        
                except Exception as e:
                    logger.error(f"Ошибка при перестройке индекса: {e}")
                    self.root.after(0, lambda: self._on_index_built_error(str(e)))
                finally:
                    progress_dialog.close()
            
            thread = threading.Thread(target=rebuild_worker, daemon=True)
            thread.start()
    
    def _on_index_built_success(self):
        """Обработка успешного построения индекса."""
        stats = self.search_engine.get_index_stats_multiple_folders()
        total_images = stats.get('total_images', 0)
        total_folders = stats.get('total_folders', 0)
        
        self.status_var.set(f"Индекс построен успешно. Проиндексировано: {total_images} изображений из {total_folders} папок")
        self._update_ui_state()
        
        folder_info = ""
        if stats.get('folders'):
            folder_details = []
            for folder, count in stats['folders'].items():
                folder_name = Path(folder).name
                folder_details.append(f"• {folder_name}: {count} изображений")
            folder_info = "\n\nПо папкам:\n" + "\n".join(folder_details[:5])
            if len(stats['folders']) > 5:
                folder_info += f"\n... и еще {len(stats['folders']) - 5} папок"
        
        messagebox.showinfo(
            "Успех", 
            f"Индекс построен успешно!\n"
            f"Проиндексировано изображений: {total_images}\n"
            f"Из папок: {total_folders}{folder_info}"
        )
    
    def _on_index_built_error(self, error_msg: str = ""):
        """Обработка ошибки построения индекса."""
        self.status_var.set("Ошибка при построении индекса")
        self._update_ui_state()
        messagebox.showerror("Ошибка", f"Не удалось построить индекс.\n{error_msg}")
    
    def _on_index_cancelled(self):
        """Обработка отмены построения индекса."""
        self.status_var.set("Построение индекса отменено")
        self._update_ui_state()
    
    def _perform_search(self):
        """Выполнение поиска изображений."""
        query = self.query_var.get().strip()
        
        if not query:
            messagebox.showwarning("Предупреждение", "Введите описание для поиска")
            return
        
        if not self.search_engine.is_ready():
            messagebox.showwarning("Предупреждение", "Сначала постройте индекс изображений")
            return
        
        # Получение настроек поиска
        max_results = self.options_frame.get_max_results()
        
        # Выполнение поиска в отдельном потоке
        def search_worker():
            try:
                self.root.after(0, lambda: self.status_var.set(f"Поиск по запросу: '{query}'..."))
                
                results = self.search_engine.search(
                    query=query,
                    max_results=max_results
                )
                
                self.root.after(0, lambda: self._on_search_completed(results, query))
                
            except Exception as e:
                logger.error(f"Ошибка при поиске: {e}")
                self.root.after(0, lambda: self._on_search_error(str(e)))
        
        thread = threading.Thread(target=search_worker, daemon=True)
        thread.start()
    
    def _on_search_completed(self, results, query):
        """Обработка завершения поиска."""
        self.results_panel.show_results(results)
        
        if results:
            self.status_var.set(f"Найдено {len(results)} результатов по запросу: '{query}'")
        else:
            self.status_var.set(f"По запросу '{query}' ничего не найдено")
    
    def _on_search_error(self, error_msg: str):
        """Обработка ошибки поиска."""
        self.status_var.set("Ошибка при выполнении поиска")
        messagebox.showerror("Ошибка поиска", f"Не удалось выполнить поиск:\n{error_msg}")
    
    def _clear_cache(self):
        """Очистка кэша."""
        result = messagebox.askyesno(
            "Подтверждение",
            "Очистить кэш? После этого потребуется заново построить индекс."
        )
        
        if result:
            try:
                self.search_engine.clear_cache()
                self.search_engine.clear_index()
                self.results_panel.show_no_results_message()
                self._update_ui_state()
                self.status_var.set("Кэш очищен")
                messagebox.showinfo("Успех", "Кэш успешно очищен")
            except Exception as e:
                logger.error(f"Ошибка при очистке кэша: {e}")
                messagebox.showerror("Ошибка", f"Не удалось очистить кэш:\n{e}")
    
    def _show_stats(self):
        """Отображение статистики."""
        if hasattr(self.search_engine, 'get_index_stats_multiple_folders'):
            stats = self.search_engine.get_index_stats_multiple_folders()
            
            stats_text = f"""Статистика индекса:
• Состояние: {'Построен' if stats['is_ready'] else 'Не построен'}
• Проиндексировано изображений: {stats['total_images']}
• Количество папок: {stats['total_folders']}

Статистика по папкам:"""
            
            if stats.get('folders'):
                for folder_path, count in list(stats['folders'].items())[:10]:  # Показываем только первые 10
                    folder_name = Path(folder_path).name
                    stats_text += f"\n• {folder_name}: {count} изображений"
                
                if len(stats['folders']) > 10:
                    stats_text += f"\n... и еще {len(stats['folders']) - 10} папок"
            else:
                stats_text += "\n• Папки не выбраны"
        else:
            # Fallback на старый метод
            stats = self.search_engine.get_index_stats()
            stats_text = f"""Статистика индекса:
• Состояние: {'Построен' if stats.get('is_built', False) else 'Не построен'}
• Проиндексировано изображений: {stats.get('total_images', 0)}"""
        
        messagebox.showinfo("Статистика", stats_text)
    
    def _show_about(self):
        """Отображение информации о программе."""
        about_text = f"""{APP_NAME} v{APP_VERSION}

Приложение для поиска изображений по текстовому описанию с использованием технологии CLIP.

Возможности:
• Поиск изображений по текстовому описанию
• Поддержка множественного выбора папок для индексации
• Кэширование результатов для быстрого повторного поиска
• Поддержка форматов JPG и PNG
• Фильтрация по дате модификации файлов
• Настройка количества результатов
• Рекурсивный поиск в подпапках

Для работы требуется выбрать папки с изображениями и построить индекс."""
        
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запуск главного цикла приложения."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Приложение завершено пользователем")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            messagebox.showerror("Критическая ошибка", f"Произошла критическая ошибка:\n{e}")
        finally:
            logger.info("Приложение завершено")

def main():
    """Точка входа в приложение."""
    try:
        app = ImageSearchApp()
        app.run()
    except Exception as e:
        logger.error(f"Не удалось запустить приложение: {e}")
        messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение:\n{e}")

if __name__ == "__main__":
    main()