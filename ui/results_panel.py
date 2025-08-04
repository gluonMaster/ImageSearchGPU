"""
Панель для отображения результатов поиска изображений.
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


class ResultsPanel(ttk.Frame):
    """Панель для отображения результатов поиска."""
    
    def __init__(self, parent):
        """
        Инициализация панели результатов.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.parent = parent
        self.results: List[SearchResult] = []
        self.selected_results: List[SearchResult] = []  # Список выбранных результатов
        self.checkboxes: List[tk.BooleanVar] = []  # Переменные для чекбоксов
        self.photo_saver = PhotoSaver()  # Экземпляр сохранялки фотографий
        
        # Словари для управления Treeview
        self.item_to_result_map = {}  # Маппинг item_id -> индекс результата
        self.result_to_item_map = {}  # Маппинг индекс результата -> item_id
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса панели результатов."""
        # Настраиваем сам фрейм
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
        
        # Treeview для отображения результатов с иконками
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Настройка колонок Treeview: основная колонка для иконки+текст, дополнительные для информации
        columns = ('similarity', 'size', 'modified', 'path')
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show='tree headings',
            selectmode='extended'
        )
        
        # Настройка высоты строк для отображения миниатюр
        # Высота строки должна быть больше высоты миниатюры (150px) + отступы
        row_height = THUMBNAIL_SIZE[1] + 10  # 150 + 10 = 160 пикселей
        style = ttk.Style()
        style.configure("Treeview", rowheight=row_height)
        
        # Дополнительные настройки стилей для лучшего отображения
        style.configure("Treeview.Heading", font=FONTS.get('header', ('Arial', 10, 'bold')))
        style.configure("Treeview", font=FONTS.get('default', ('Arial', 9)))
        
        # Настройка заголовков
        self.tree.heading('#0', text='Фото', anchor='w')
        self.tree.heading('similarity', text='Схожесть', anchor='center')
        self.tree.heading('size', text='Размер', anchor='center')  
        self.tree.heading('modified', text='Изменен', anchor='center')
        self.tree.heading('path', text='Путь', anchor='w')
        
        # Настройка ширины колонок с учетом увеличенной высоты строк
        self.tree.column('#0', width=400, minwidth=300)  # Увеличена для лучшего отображения имени с иконкой
        self.tree.column('similarity', width=100, minwidth=80)
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('modified', width=150, minwidth=120)
        self.tree.column('path', width=350, minwidth=250)
        
        # Scrollbar для Treeview
        self.scrollbar = ttk.Scrollbar(
            self.tree_frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Размещение элементов
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Привязка событий
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_single_click)
        self.tree.bind('<space>', self._on_space_key)
        self.tree.bind('<Return>', self._on_enter_key)
        
        # Привязка прокрутки колесом мыши (Treeview поддерживает это автоматически)
        self.tree.bind("<MouseWheel>", self._on_mousewheel)
        
        # Словарь для хранения checkbox состояний по item_id
        self.item_checkboxes = {}
        
        # Кэш миниатюр для оптимизации
        self.thumbnail_cache = {}
        
        # Устанавливаем фокус на treeview
        self.tree.focus_set()
        
        # Начальное состояние
        self._update_control_panel()
        
        # Начальное сообщение
        self.show_no_results_message()
    
    def _on_mousewheel(self, event):
        """Обработка прокрутки колесом мыши для Treeview."""
        try:
            # Treeview автоматически обрабатывает прокрутку, 
            # но мы можем добавить дополнительную логику если нужно
            if event.delta:
                # Windows
                delta = int(-1 * (event.delta / 120))
            else:
                # Linux/Mac
                delta = -1 if event.num == 4 else 1
            
            # Передаем событие прокрутки в Treeview
            self.tree.yview_scroll(delta, "units")
            
        except Exception as e:
            print(f"Mousewheel error: {e}")
    
    def _on_double_click(self, event):
        """Обработка двойного клика - открытие файла."""
        item = self.tree.selection()
        if item:
            self._open_selected_file()
    
    def _on_single_click(self, event):
        """Обработка одиночного клика для переключения выбора."""
        # Определяем элемент и регион клика
        item = self.tree.identify('item', event.x, event.y)
        region = self.tree.identify('region', event.x, event.y)
        
        if item and region == 'cell':
            # Переключаем выбор элемента
            self._toggle_item_selection(item)
    
    def _on_space_key(self, event):
        """Обработка нажатия пробела для переключения выбора."""
        selected_items = self.tree.selection()
        if selected_items:
            for item in selected_items:
                self._toggle_item_selection(item)
    
    def _on_enter_key(self, event):
        """Обработка нажатия Enter - открытие файла."""
        selected_items = self.tree.selection()
        if selected_items:
            self._open_selected_file()
    
    def _toggle_item_selection(self, item_id):
        """Переключение выбранного состояния элемента."""
        if item_id not in self.item_to_result_map:
            return
        
        result_index = self.item_to_result_map[item_id]
        if result_index >= len(self.checkboxes):
            return
        
        # Переключаем состояние checkbox
        checkbox_var = self.checkboxes[result_index]
        checkbox_var.set(not checkbox_var.get())
        
        # Обновляем визуальное представление
        self._update_item_visual_state(item_id, result_index)
    
    def _update_item_visual_state(self, item_id, result_index):
        """Обновление визуального состояния элемента."""
        if result_index >= len(self.checkboxes):
            return
        
        is_selected = self.checkboxes[result_index].get()
        
        # Получаем текущий текст элемента
        current_text = self.tree.item(item_id, 'text')
        
        # Удаляем предыдущие маркеры выбора
        if current_text.startswith('☑ ') or current_text.startswith('☐ '):
            current_text = current_text[2:]
        
        # Добавляем новый маркер
        if is_selected:
            new_text = f'☑ {current_text}'
            self.tree.item(item_id, tags=('selected',))
        else:
            new_text = f'☐ {current_text}'
            self.tree.item(item_id, tags=('unselected',))
        
        self.tree.item(item_id, text=new_text)
        
        # Настраиваем стили для выбранных/невыбранных элементов с учетом увеличенной высоты
        self.tree.tag_configure('selected', background='#e6f3ff', foreground='black')
        self.tree.tag_configure('unselected', background='white', foreground='black')
        
        # Дополнительные стили для лучшего визуального представления
        self.tree.tag_configure('message', background='#f8f8f8', foreground='gray')
    
    def show_results(self, results: List[SearchResult]):
        """
        Отображение результатов поиска в Treeview.
        
        Args:
            results: Список результатов поиска
        """
        self.results = results
        self.selected_results = []
        self.checkboxes = []
        self._clear_results()
        
        if not results:
            self.show_no_results_message()
            self._update_control_panel()
            return
        
        print(f"Loading {len(results)} results into Treeview...")
        
        # Очищаем маппинги
        self.item_to_result_map.clear()
        self.result_to_item_map.clear()
        
        # Создаем checkbox переменные для всех результатов
        for i in range(len(results)):
            checkbox_var = tk.BooleanVar()
            checkbox_var.trace('w', self._on_selection_changed)
            self.checkboxes.append(checkbox_var)
        
        # Добавляем результаты в Treeview пакетами для лучшей производительности
        batch_size = 50
        for i in range(0, len(results), batch_size):
            batch_end = min(i + batch_size, len(results))
            self._load_results_batch(results, i, batch_end)
            
            # Обновление интерфейса для отзывчивости
            if i > 0:
                self.tree.update_idletasks()
                print(f"Loaded {batch_end} of {len(results)} results...")
        
        print(f"All {len(results)} results loaded into Treeview")
        
        # Устанавливаем фокус и обновляем панель управления
        self.tree.focus_set()
        self._update_control_panel()
    
    def _load_results_batch(self, results: List[SearchResult], start_index: int, end_index: int):
        """Загрузка пакета результатов в Treeview."""
        for i in range(start_index, end_index):
            result = results[i]
            
            # Создаем миниатюру изображения
            thumbnail = self._get_or_create_thumbnail(result.file_path)
            
            # Форматируем данные для отображения
            file_size = result.file_info.get('size', result.file_info.get('file_size', 0))
            size_text = self._format_file_size(file_size)
            
            mod_time = result.file_info.get('modification_time', result.file_info.get('modified_date', ''))
            if isinstance(mod_time, str):
                mod_time_text = mod_time if mod_time else 'Неизвестно'
            else:
                mod_time_text = mod_time.strftime('%d.%m.%Y %H:%M') if mod_time else 'Неизвестно'
            
            # Создаем текст для основной колонки
            file_name = result.file_info.get('name', Path(result.file_path).name)
            main_text = f'☐ {file_name}'
            
            # Добавляем элемент в Treeview
            item_id = self.tree.insert(
                '', 'end',
                text=main_text,
                image=thumbnail,
                values=(
                    f"{result.similarity_score:.1%}",
                    size_text,
                    mod_time_text,
                    result.file_path
                ),
                tags=('unselected',)
            )
            
            # Сохраняем маппинги
            self.item_to_result_map[item_id] = i
            self.result_to_item_map[i] = item_id
    
    def _get_or_create_thumbnail(self, image_path: str) -> ImageTk.PhotoImage:
        """Получение или создание миниатюры изображения с кэшированием."""
        if image_path in self.thumbnail_cache:
            return self.thumbnail_cache[image_path]
        
        try:
            thumbnail = self._create_thumbnail(image_path)
            self.thumbnail_cache[image_path] = thumbnail
            return thumbnail
        except Exception as e:
            logger.warning(f"Не удалось создать миниатюру для {image_path}: {e}")
            # Возвращаем пустую иконку или placeholder
            if 'placeholder' not in self.thumbnail_cache:
                # Создаем улучшенный placeholder точного размера
                placeholder_img = Image.new('RGB', THUMBNAIL_SIZE, color='#f0f0f0')
                
                # Добавляем текст "Нет изображения" в placeholder
                try:
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(placeholder_img)
                    
                    # Пытаемся использовать стандартный шрифт
                    try:
                        font = ImageFont.truetype("arial.ttf", 12)
                    except:
                        font = ImageFont.load_default()
                    
                    # Рисуем текст по центру
                    text = "Нет\nизображения"
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    x = (THUMBNAIL_SIZE[0] - text_width) // 2
                    y = (THUMBNAIL_SIZE[1] - text_height) // 2
                    
                    draw.text((x, y), text, fill='#888888', font=font, align='center')
                    
                except ImportError:
                    # Если PIL.ImageDraw недоступен, создаем простой серый квадрат
                    pass
                    
                self.thumbnail_cache['placeholder'] = ImageTk.PhotoImage(placeholder_img)
            return self.thumbnail_cache['placeholder']
    
    def _clear_results(self):
        """Очистка текущих результатов."""
        # Очищаем все элементы из Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Очищаем маппинги
        self.item_to_result_map.clear()
        self.result_to_item_map.clear()
        
        # Очищаем кэш миниатюр (кроме placeholder)
        placeholder = self.thumbnail_cache.get('placeholder')
        self.thumbnail_cache.clear()
        if placeholder:
            self.thumbnail_cache['placeholder'] = placeholder
    
    def _create_thumbnail(self, image_path: str) -> ImageTk.PhotoImage:
        """
        Создание миниатюры изображения точного размера.
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            ImageTk.PhotoImage: Миниатюра изображения
        """
        try:
            image = Image.open(image_path)
            
            # Создаем миниатюру с сохранением пропорций
            image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Создаем фон нужного размера для центрирования изображения
            background = Image.new('RGB', THUMBNAIL_SIZE, color='white')
            
            # Вычисляем позицию для центрирования
            x = (THUMBNAIL_SIZE[0] - image.width) // 2
            y = (THUMBNAIL_SIZE[1] - image.height) // 2
            
            # Вставляем изображение в центр
            background.paste(image, (x, y))
            
            return ImageTk.PhotoImage(background)
            
        except Exception as e:
            # В случае ошибки возвращаем placeholder
            logger.warning(f"Не удалось создать миниатюру для {image_path}: {e}")
            raise
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Форматирование размера файла в читаемый вид.
        
        Args:
            size_bytes: Размер в байтах
            
        Returns:
            str: Отформатированный размер
        """
        if size_bytes < 1024:
            return f"{size_bytes} Б"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} КБ"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} МБ"
    
    def _open_file(self, file_path: str):
        """
        Открытие файла в приложении по умолчанию.
        
        Args:
            file_path: Путь к файлу
        """
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
    
    def _open_folder(self, file_path: str):
        """
        Открытие папки с файлом в проводнике.
        
        Args:
            file_path: Путь к файлу
        """
        try:
            folder_path = os.path.dirname(file_path)
            os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{e}")
    
    def show_no_results_message(self):
        """Отображение сообщения об отсутствии результатов."""
        self._clear_results()
        
        # Добавляем элемент с информационным сообщением
        self.tree.insert(
            '', 'end',
            text='Результаты поиска будут отображены здесь',
            values=('', '', '', ''),
            tags=('message',)
        )
        
        # Настраиваем стиль для сообщения
        self.tree.tag_configure('message', background='#f8f8f8', foreground='gray')
    
    def _open_selected_file(self):
        """Открытие выбранного в Treeview файла."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        if item in self.item_to_result_map:
            result_index = self.item_to_result_map[item]
            if result_index < len(self.results):
                file_path = self.results[result_index].file_path
                self._open_file(file_path)
    
    def _open_selected_folder(self):
        """Открытие папки выбранного в Treeview файла."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        if item in self.item_to_result_map:
            result_index = self.item_to_result_map[item]
            if result_index < len(self.results):
                file_path = self.results[result_index].file_path
                self._open_folder(file_path)
    
    def _select_all(self):
        """Выбор всех результатов."""
        for i, checkbox_var in enumerate(self.checkboxes):
            if not checkbox_var.get():  # Только если еще не выбран
                checkbox_var.set(True)
                if i in self.result_to_item_map:
                    item_id = self.result_to_item_map[i]
                    self._update_item_visual_state(item_id, i)
    
    def _deselect_all(self):
        """Снятие выбора со всех результатов."""
        for i, checkbox_var in enumerate(self.checkboxes):
            if checkbox_var.get():  # Только если выбран
                checkbox_var.set(False)
                if i in self.result_to_item_map:
                    item_id = self.result_to_item_map[i]
                    self._update_item_visual_state(item_id, i)
    
    def _on_selection_changed(self, *args):
        """Обработчик изменения выбора результатов."""
        self._update_selected_results()
        self._update_control_panel()
    
    def _update_selected_results(self):
        """Обновление списка выбранных результатов."""
        self.selected_results = []
        for i, checkbox_var in enumerate(self.checkboxes):
            if checkbox_var.get() and i < len(self.results):
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
        
        # Показываем предварительный просмотр организации
        try:
            from .dialogs import PhotoPreviewDialog
            from .progress_dialog import ProgressDialog
            
            organization = self.photo_saver.preview_organization(photo_paths)
            
            # Показываем диалог предпросмотра
            preview_dialog = PhotoPreviewDialog(self.parent, organization, destination_dir)
            if not preview_dialog.show_modal():
                return
            
            # Выполнение сохранения с прогрессом
            self._execute_save_operation(photo_paths, destination_dir)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении фотографий: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при сохранении фотографий:\n{e}")
    
    def _execute_save_operation(self, photo_paths: list, destination_dir: str):
        """
        Выполнение операции сохранения с отображением прогресса.
        
        Args:
            photo_paths: Список путей к фотографиям
            destination_dir: Целевая папка
        """
        from .progress_dialog import ProgressDialog
        
        # Создаем диалог прогресса
        progress_dialog = ProgressDialog(
            self.parent,
            "Сохранение фотографий"
        )
        
        def progress_callback(current, total, message):
            if not progress_dialog.is_cancelled():
                progress_dialog.update_progress(current, total, message)
        
        def save_worker():
            """Рабочая функция для сохранения в отдельном потоке."""
            try:
                results = self.photo_saver.save_photos(
                    photo_paths,
                    destination_dir,
                    progress_callback
                )
                
                # Закрываем диалог прогресса в основном потоке
                self.parent.after(0, lambda: progress_dialog.close())
                
                # Показываем результаты в основном потоке
                self.parent.after(0, lambda: self._show_save_results(results, destination_dir))
                
            except Exception as e:
                logger.error(f"Ошибка в потоке сохранения: {e}")
                self.parent.after(0, lambda: progress_dialog.close())
                self.parent.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}"))
        
        # Запускаем сохранение в отдельном потоке
        save_thread = threading.Thread(target=save_worker, daemon=True)
        save_thread.start()
    
    def _show_save_results(self, results: dict, destination_dir: str):
        """
        Отображение результатов сохранения.
        
        Args:
            results: Результаты операции сохранения
            destination_dir: Путь к папке сохранения
        """
        if results['success']:
            message_lines = [
                f"✅ Сохранение завершено успешно!",
                f"",
                f"Сохранено фотографий: {results['saved_photos']} из {results['total_photos']}",
                f"Создано папок: {len(results['created_folders'])}",
                f"Папка назначения: {destination_dir}"
            ]
            
            if results['created_folders']:
                message_lines.append("")
                message_lines.append("Созданные папки:")
                for folder in sorted(results['created_folders']):
                    message_lines.append(f"  • {folder}")
            
            if results['failed_photos'] > 0:
                message_lines.append(f"")
                message_lines.append(f"⚠️ Не удалось сохранить: {results['failed_photos']} фотографий")
            
            messagebox.showinfo("Сохранение завершено", "\n".join(message_lines))
            
            # Предлагаем открыть папку с результатами
            if messagebox.askyesno("Открыть папку", "Открыть папку с сохраненными фотографиями?"):
                try:
                    os.startfile(destination_dir)
                except Exception as e:
                    logger.error(f"Не удалось открыть папку {destination_dir}: {e}")
        else:
            error_message = f"❌ Ошибка при сохранении:\n{results.get('error', 'Неизвестная ошибка')}"
            messagebox.showerror("Ошибка сохранения", error_message)
