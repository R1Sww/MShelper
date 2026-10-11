"""
MasterSCADA Helper - Приложение для работы со всеми версиями MasterSCADA
Версия 5.0 - Полная функциональность
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import sys
import pyperclip
import re
from datetime import datetime
from pathlib import Path
import time
import threading
import shutil

# Импорты для работы с окнами Windows
try:
    import win32gui
    import win32con
    import win32api
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# Импорты для трея
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# Предустановленные настройки для разных версий MasterSCADA
MASTERSCADA_VERSIONS = {
    "MasterSCADA 4.0": "MasterSCADA",
    "MasterSCADA 4.1": "MasterSCADA",
    "MasterSCADA 4.2": "MasterSCADA",
    "MasterSCADA 4D": "MasterSCADA",
    "MasterSCADA 3.x": "MasterSCADA",
    "MasterSCADA (любая версия)": "MasterSCADA"
}

# База данных типичных элементов MasterSCADA
DEFAULT_DATA = {
    "categories": [
        {
            "name": "Теги и переменные",
            "icon": "🏷️",
            "items": [
                {"name": "Температура", "value": "Temp", "description": "Тег температуры", "favorite": False, "hotkey": None},
                {"name": "Давление", "value": "Pressure", "description": "Тег давления", "favorite": False, "hotkey": None},
                {"name": "Расход", "value": "Flow", "description": "Тег расхода", "favorite": False, "hotkey": None},
                {"name": "Уровень", "value": "Level", "description": "Тег уровня", "favorite": False, "hotkey": None},
                {"name": "Скорость", "value": "Speed", "description": "Тег скорости", "favorite": False, "hotkey": None},
                {"name": "Мощность", "value": "Power", "description": "Тег мощности", "favorite": False, "hotkey": None},
                {"name": "Напряжение", "value": "Voltage", "description": "Тег напряжения", "favorite": False, "hotkey": None},
                {"name": "Ток", "value": "Current", "description": "Тег тока", "favorite": False, "hotkey": None},
                {"name": "Частота", "value": "Frequency", "description": "Тег частоты", "favorite": False, "hotkey": None},
                {"name": "Счётчик", "value": "Counter", "description": "Тег счётчика", "favorite": False, "hotkey": None}
            ]
        },
        {
            "name": "Команды управления",
            "icon": "⚡",
            "items": [
                {"name": "Пуск", "value": "Start", "description": "Команда пуска", "favorite": False, "hotkey": None},
                {"name": "Стоп", "value": "Stop", "description": "Команда останова", "favorite": False, "hotkey": None},
                {"name": "Аварийный стоп", "value": "EmergencyStop", "description": "Аварийный останов", "favorite": False, "hotkey": None},
                {"name": "Сброс", "value": "Reset", "description": "Сброс ошибок", "favorite": False, "hotkey": None},
                {"name": "Подтверждение", "value": "Ack", "description": "Подтверждение события", "favorite": False, "hotkey": None},
                {"name": "Включить", "value": "Enable", "description": "Включить устройство", "favorite": False, "hotkey": None},
                {"name": "Выключить", "value": "Disable", "description": "Выключить устройство", "favorite": False, "hotkey": None},
                {"name": "Ручной режим", "value": "ManualMode", "description": "Перевод в ручной режим", "favorite": False, "hotkey": None},
                {"name": "Автоматический режим", "value": "AutoMode", "description": "Перевод в автоматический режим", "favorite": False, "hotkey": None}
            ]
        },
        {
            "name": "Типы данных",
            "icon": "📊",
            "items": [
                {"name": "Целое число", "value": "INT", "description": "Целочисленный тип", "favorite": False, "hotkey": None},
                {"name": "Вещественное число", "value": "REAL", "description": "Число с плавающей точкой", "favorite": False, "hotkey": None},
                {"name": "Логический", "value": "BOOL", "description": "Булев тип (истина/ложь)", "favorite": False, "hotkey": None},
                {"name": "Строка", "value": "STRING", "description": "Строковый тип", "favorite": False, "hotkey": None},
                {"name": "Дата и время", "value": "DATETIME", "description": "Дата и время", "favorite": False, "hotkey": None},
                {"name": "Массив", "value": "ARRAY", "description": "Массив значений", "favorite": False, "hotkey": None},
                {"name": "Структура", "value": "STRUCT", "description": "Структурированный тип", "favorite": False, "hotkey": None}
            ]
        },
        {
            "name": "Устройства",
            "icon": "🔧",
            "items": [
                {"name": "Контроллер", "value": "PLC", "description": "Программируемый контроллер", "favorite": False, "hotkey": None},
                {"name": "Датчик", "value": "Sensor", "description": "Датчик", "favorite": False, "hotkey": None},
                {"name": "Исполнительный механизм", "value": "Actuator", "description": "Исполнительный механизм", "favorite": False, "hotkey": None},
                {"name": "Частотный преобразователь", "value": "VFD", "description": "ЧП/ПЧ", "favorite": False, "hotkey": None},
                {"name": "Реле", "value": "Relay", "description": "Реле", "favorite": False, "hotkey": None},
                {"name": "Контактор", "value": "Contactor", "description": "Контактор", "favorite": False, "hotkey": None},
                {"name": "Клапан", "value": "Valve", "description": "Клапан", "favorite": False, "hotkey": None},
                {"name": "Двигатель", "value": "Motor", "description": "Электродвигатель", "favorite": False, "hotkey": None},
                {"name": "Насос", "value": "Pump", "description": "Насос", "favorite": False, "hotkey": None},
                {"name": "Вентилятор", "value": "Fan", "description": "Вентилятор", "favorite": False, "hotkey": None}
            ]
        },
        {
            "name": "События и алармы",
            "icon": "🚨",
            "items": [
                {"name": "Авария", "value": "Alarm", "description": "Аварийное событие", "favorite": False, "hotkey": None},
                {"name": "Предупреждение", "value": "Warning", "description": "Предупреждение", "favorite": False, "hotkey": None},
                {"name": "Информация", "value": "Info", "description": "Информационное сообщение", "favorite": False, "hotkey": None},
                {"name": "Критический уровень", "value": "Critical", "description": "Критический уровень", "favorite": False, "hotkey": None},
                {"name": "Высокий уровень", "value": "High", "description": "Высокий уровень", "favorite": False, "hotkey": None},
                {"name": "Низкий уровень", "value": "Low", "description": "Низкий уровень", "favorite": False, "hotkey": None},
                {"name": "Отклонение", "value": "Deviation", "description": "Отклонение от нормы", "favorite": False, "hotkey": None}
            ]
        },
        {
            "name": "Шаблоны скриптов",
            "icon": "📝",
            "items": [
                {"name": "IF-THEN-ELSE", "value": "IF condition THEN\n    // действие\nELSE\n    // альтернативное действие\nEND_IF", "description": "Условный оператор", "favorite": False, "hotkey": None},
                {"name": "Цикл FOR", "value": "FOR i := 1 TO 10 DO\n    // действие\nEND_FOR", "description": "Цикл с параметром", "favorite": False, "hotkey": None},
                {"name": "Цикл WHILE", "value": "WHILE condition DO\n    // действие\nEND_WHILE", "description": "Цикл с условием", "favorite": False, "hotkey": None},
                {"name": "Функция", "value": "FUNCTION MyFunction : REAL\nVAR_INPUT\n    param : REAL;\nEND_VAR\n    // тело функции\nEND_FUNCTION", "description": "Объявление функции", "favorite": False, "hotkey": None},
                {"name": "Функциональный блок", "value": "FUNCTION_BLOCK MyFB\nVAR_INPUT\n    input : REAL;\nEND_VAR\nVAR_OUTPUT\n    output : REAL;\nEND_VAR\n// тело блока\nEND_FUNCTION_BLOCK", "description": "Функциональный блок", "favorite": False, "hotkey": None}
            ]
        }
    ]
}


class MasterSCADAHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("MasterSCADA Helper v5.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Определяем путь к папке данных
        self.data_dir = self.get_data_dir()
        
        # Настройки
        self.settings = {
            "masterscada_window_title": "MasterSCADA",
            "auto_insert": True,
            "insert_delay": 0.5,
            "search_mode": "contains",
            "minimize_to_tray": True,
            "autostart": False,
            "backup_enabled": True,
            "backup_interval_hours": 24
        }
        
        # Загрузка данных
        self.data_file = os.path.join(self.data_dir, "masterscada_data.json")
        self.settings_file = os.path.join(self.data_dir, "masterscada_settings.json")
        self.history_file = os.path.join(self.data_dir, "masterscada_history.json")
        self.templates_file = os.path.join(self.data_dir, "masterscada_templates.json")
        self.stats_file = os.path.join(self.data_dir, "masterscada_stats.json")
        
        self.data = self.load_data()
        self.load_settings()
        self.load_history()
        self.load_templates()
        self.load_stats()
        
        # Трей
        self.tray_icon = None
        self.is_in_tray = False
        
        # Создание интерфейса
        self.create_menu()
        self.create_main_interface()
        
        # Привязка горячих клавиш
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-s>', lambda e: self.scan_masterscada())
        self.root.bind('<Control-i>', lambda e: self.insert_to_masterscada())
        self.root.bind('<Control-b>', lambda e: self.batch_insert())
        self.root.bind('<Control-t>', lambda e: self.show_templates())
        self.root.bind('<Control-h>', lambda e: self.show_history())
        
        # Горячие клавиши F1-F12
        for i in range(1, 13):
            self.root.bind(f'<F{i}>', lambda e, idx=i: self.trigger_hotkey(idx))
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Автозапуск резервного копирования
        if self.settings.get("backup_enabled", True):
            self.schedule_backup()
    
    def get_data_dir(self):
        """Получение пути к папке данных (создаёт при необходимости)"""
        # Определяем базовую директорию (рядом с exe или скриптом)
        if getattr(sys, 'frozen', False):
            # Запущено как .exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # Запущено как скрипт
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    
    def load_data(self):
        """Загрузка данных из файла или создание по умолчанию"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_DATA
    
    def save_data(self):
        """Сохранение данных в файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def load_settings(self):
        """Загрузка настроек"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except:
                pass
    
    def save_settings(self):
        """Сохранение настроек"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def load_history(self):
        """Загрузка истории операций"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        """Сохранение истории операций"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def load_templates(self):
        """Загрузка шаблонов проектов"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except:
                self.templates = []
        else:
            self.templates = []
    
    def save_templates(self):
        """Сохранение шаблонов проектов"""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def load_stats(self):
        """Загрузка статистики"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                self.stats = {}
        else:
            self.stats = {}
    
    def save_stats(self):
        """Сохранение статистики"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сканировать MasterSCADA", command=self.scan_masterscada, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить базу", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт базы", command=self.export_data)
        file_menu.add_command(label="Импорт базы", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в текстовый файл", command=self.export_to_text)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit_app)
        
        # Вставка
        insert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вставка", menu=insert_menu)
        insert_menu.add_command(label="Вставить в MasterSCADA", command=self.insert_to_masterscada, accelerator="Ctrl+I")
        insert_menu.add_command(label="Пакетная вставка", command=self.batch_insert, accelerator="Ctrl+B")
        insert_menu.add_separator()
        insert_menu.add_command(label="Настройки вставки", command=self.show_insert_settings)
        insert_menu.add_separator()
        
        # Подменю для выбора версии MasterSCADA
        version_menu = tk.Menu(insert_menu, tearoff=0)
        insert_menu.add_cascade(label="Версия MasterSCADA", menu=version_menu)
        for version_name, window_title in MASTERSCADA_VERSIONS.items():
            version_menu.add_command(
                label=version_name,
                command=lambda v=window_title: self.set_masterscada_version(v)
            )
        
        # Избранное
        favorite_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Избранное", menu=favorite_menu)
        favorite_menu.add_command(label="Показать избранное", command=self.show_favorites)
        favorite_menu.add_command(label="Добавить в избранное", command=self.add_to_favorites)
        favorite_menu.add_command(label="Убрать из избранного", command=self.remove_from_favorites)
        
        # Шаблоны
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Шаблоны", menu=template_menu)
        template_menu.add_command(label="Показать шаблоны", command=self.show_templates, accelerator="Ctrl+T")
        template_menu.add_command(label="Создать шаблон", command=self.create_template)
        template_menu.add_command(label="Применить шаблон", command=self.apply_template)
        
        # История
        history_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="История", menu=history_menu)
        history_menu.add_command(label="Показать историю", command=self.show_history, accelerator="Ctrl+H")
        history_menu.add_command(label="Очистить историю", command=self.clear_history)
        
        # Статистика
        stats_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Статистика", menu=stats_menu)
        stats_menu.add_command(label="Показать статистику", command=self.show_statistics)
        stats_menu.add_command(label="Сбросить статистику", command=self.reset_statistics)
        
        # Настройки
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Настройки вставки", command=self.show_insert_settings)
        settings_menu.add_command(label="Настройки автозапуска", command=self.show_autostart_settings)
        settings_menu.add_command(label="Настройки резервного копирования", command=self.show_backup_settings)
        
        # Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Горячие клавиши", command=self.show_hotkeys)
    
    def create_main_interface(self):
        """Создание основного интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растяжения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Верхняя панель - поиск и кнопки
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        
        # Поиск
        search_frame = ttk.LabelFrame(top_frame, text="Поиск", padding="5")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12))
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(search_frame, text="🔍 Найти", command=self.perform_search).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(search_frame, text="✕ Очистить", command=self.clear_search).grid(row=0, column=2)
        
        # Кнопки действий
        action_frame = ttk.LabelFrame(top_frame, text="Действия", padding="5")
        action_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="📋 Копировать", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📥 Вставить", command=self.insert_to_masterscada).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📦 Пакетная", command=self.batch_insert).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Сканировать", command=self.scan_masterscada).pack(side=tk.LEFT, padx=5)
        
        # Левая панель - категории
        left_frame = ttk.LabelFrame(main_frame, text="Категории", padding="5")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # Список категорий
        self.category_listbox = tk.Listbox(left_frame, width=35, font=('Arial', 11))
        self.category_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Скроллбар для категорий
        cat_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.category_listbox.yview)
        cat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.category_listbox.configure(yscrollcommand=cat_scrollbar.set)
        
        # Кнопки управления категориями
        cat_btn_frame = ttk.Frame(left_frame)
        cat_btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(cat_btn_frame, text="➕", width=3, command=self.add_category).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(cat_btn_frame, text="✏️", width=3, command=self.edit_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_btn_frame, text="🗑️", width=3, command=self.delete_category).pack(side=tk.LEFT, padx=2)
        
        # Правая панель - элементы
        right_frame = ttk.LabelFrame(main_frame, text="Элементы", padding="5")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Таблица элементов
        columns = ('favorite', 'name', 'value', 'description', 'hotkey')
        self.item_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=30)
        
        self.item_tree.heading('favorite', text='⭐')
        self.item_tree.heading('name', text='Название')
        self.item_tree.heading('value', text='Значение')
        self.item_tree.heading('description', text='Описание')
        self.item_tree.heading('hotkey', text='Клавиша')
        
        self.item_tree.column('favorite', width=30, anchor='center')
        self.item_tree.column('name', width=200)
        self.item_tree.column('value', width=200)
        self.item_tree.column('description', width=300)
        self.item_tree.column('hotkey', width=80, anchor='center')
        
        self.item_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.item_tree.bind('<Double-1>', self.on_item_double_click)
        self.item_tree.bind('<Button-3>', self.show_context_menu)
        
        # Скроллбар для элементов
        item_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.item_tree.yview)
        item_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.item_tree.configure(yscrollcommand=item_scrollbar.set)
        
        # Кнопки действий
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(action_frame, text="📋 Копировать", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📥 Вставить", command=self.insert_to_masterscada).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="⭐ В избранное", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="⌨️ Назначить клавишу", command=self.assign_hotkey).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✏️ Редактировать", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🗑️ Удалить", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        
        # Нижняя панель - предпросмотр и статус
        bottom_frame = ttk.LabelFrame(main_frame, text="Предпросмотр", padding="5")
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        self.preview_text = tk.Text(bottom_frame, height=4, wrap=tk.WORD, font=('Consolas', 10))
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.preview_text.config(state=tk.DISABLED)
        
        # Статус-бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово. Выберите элемент и нажмите 'Вставить в MasterSCADA'.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Заполнение категорий
        self.populate_categories()
    
    def populate_categories(self):
        """Заполнение списка категорий"""
        self.category_listbox.delete(0, tk.END)
        for category in self.data['categories']:
            display_text = f"{category['icon']} {category['name']}"
            self.category_listbox.insert(tk.END, display_text)
    
    def on_category_select(self, event):
        """Обработка выбора категории"""
        selection = self.category_listbox.curselection()
        if selection:
            category = self.data['categories'][selection[0]]
            self.populate_items(category)
            self.status_var.set(f"Категория: {category['name']} | Элементов: {len(category['items'])}")
    
    def populate_items(self, category):
        """Заполнение списка элементов выбранной категории (сортировка по алфавиту)"""
        # Очистка таблицы
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
        
        # Сортировка по алфавиту
        sorted_items = sorted(category['items'], key=lambda x: x['name'].lower())
        
        # Заполнение
        for item in sorted_items:
            favorite_mark = "⭐" if item.get('favorite', False) else ""
            hotkey_mark = item.get('hotkey', '') or ''
            # Показываем только первую строку значения в таблице
            display_value = item['value'].split('\n')[0]
            self.item_tree.insert('', tk.END, values=(favorite_mark, item['name'], display_value, item['description'], hotkey_mark))
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по элементу"""
        self.insert_to_masterscada()
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        selected = self.item_tree.selection()
        if not selected:
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📋 Копировать", command=self.copy_selected)
        menu.add_command(label="📥 Вставить в MasterSCADA", command=self.insert_to_masterscada)
        menu.add_separator()
        menu.add_command(label="⭐ Добавить в избранное", command=self.add_to_favorites)
        menu.add_command(label="⭐ Убрать из избранного", command=self.remove_from_favorites)
        menu.add_separator()
        menu.add_command(label="⌨️ Назначить горячую клавишу", command=self.assign_hotkey)
        menu.add_separator()
        menu.add_command(label="✏️ Редактировать", command=self.edit_selected)
        menu.add_command(label="🗑️ Удалить", command=self.delete_selected)
        
        menu.post(event.x_root, event.y_root)
    
    def copy_selected(self):
        """Копирование выбранного элемента в буфер обмена"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для копирования")
            return
        
        item_values = self.item_tree.item(selected[0])['values']
        value_to_copy = item_values[2]  # Значение (value)
        
        try:
            pyperclip.copy(value_to_copy)
            self.status_var.set(f"Скопировано в буфер обмена: {value_to_copy}")
            
            # Добавление в историю
            self.add_to_history('copy', value_to_copy)
            
            # Обновление статистики
            self.update_stats(value_to_copy)
            
            # Обновление предпросмотра
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, value_to_copy)
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать: {str(e)}")
    
    def insert_to_masterscada(self):
        """Автоматическая вставка выбранного элемента в MasterSCADA"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для вставки")
            return
        
        item_values = self.item_tree.item(selected[0])['values']
        value_to_insert = item_values[2]  # Значение (value)
        
        if not WIN32_AVAILABLE:
            pyperclip.copy(value_to_insert)
            self.status_var.set(f"win32 недоступен. Скопировано в буфер обмена: {value_to_insert}")
            messagebox.showinfo(
                "Ручная вставка",
                "Модуль pywin32 не установлен.\n\n"
                "Текст скопирован в буфер обмена.\n"
                "Перейдите в MasterSCADA и нажмите Ctrl+V для вставки.\n\n"
                "Для автоматической вставки установите pywin32:\n"
                "pip install pywin32"
            )
            return
        
        try:
            pyperclip.copy(value_to_insert)
            
            window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
            hwnd = self.find_masterscada_window(window_title)
            
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                self.simulate_paste()
                
                self.status_var.set(f"Вставлено в MasterSCADA: {value_to_insert}")
                self.add_to_history('insert', value_to_insert)
                self.update_stats(value_to_insert)
                
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, value_to_insert)
                self.preview_text.config(state=tk.DISABLED)
                
            else:
                self.status_var.set(f"Окно MasterSCADA не найдено. Скопировано в буфер обмена: {value_to_insert}")
                messagebox.showinfo(
                    "MasterSCADA не найдена",
                    f"Окно с заголовком '{window_title}' не найдено.\n\n"
                    "Текст скопирован в буфер обмена.\n"
                    "Перейдите в MasterSCADA и нажмите Ctrl+V для вставки.\n\n"
                    "Убедитесь, что MasterSCADA запущена."
                )
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить: {str(e)}")
    
    def batch_insert(self):
        """Пакетная вставка нескольких элементов"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элементы для пакетной вставки")
            return
        
        values = []
        for item_id in selected:
            item_values = self.item_tree.item(item_id)['values']
            values.append(item_values[2])  # Значение (value)
        
        # Объединяем значения с разделителем
        separator = simpledialog.askstring(
            "Пакетная вставка",
            "Введите разделитель (Enter - новая строка):",
            initialvalue="\n"
        )
        
        if separator is None:
            return
        
        combined_text = separator.join(values)
        
        try:
            pyperclip.copy(combined_text)
            
            window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
            hwnd = self.find_masterscada_window(window_title)
            
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                self.simulate_paste()
                
                self.status_var.set(f"Пакетная вставка завершена: {len(values)} элементов")
                self.add_to_history('batch_insert', f"{len(values)} элементов")
                
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, combined_text)
                self.preview_text.config(state=tk.DISABLED)
                
            else:
                self.status_var.set(f"Окно MasterSCADA не найдено. Скопировано в буфер обмена: {len(values)} элементов")
                messagebox.showinfo(
                    "MasterSCADA не найдена",
                    f"Окно MasterSCADA не найдено.\n\n"
                    f"Скопировано {len(values)} элементов в буфер обмена.\n"
                    "Перейдите в MasterSCADA и нажмите Ctrl+V для вставки."
                )
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить пакетную вставку: {str(e)}")
    
    def find_masterscada_window(self, title_pattern):
        """Поиск окна MasterSCADA по заголовку"""
        if not WIN32_AVAILABLE:
            return None
        
        result = []
        search_mode = self.settings.get("search_mode", "contains")
        
        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if search_mode == "contains":
                    if title_pattern.lower() in window_title.lower():
                        result.append(hwnd)
                else:
                    if title_pattern.lower() == window_title.lower():
                        result.append(hwnd)
            return True
        
        win32gui.EnumWindows(enum_windows_callback, None)
        
        return result[0] if result else None
    
    def simulate_paste(self):
        """Симуляция нажатия Ctrl+V"""
        if not WIN32_AVAILABLE:
            return
        
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def add_to_favorites(self):
        """Добавление выбранного элемента в избранное"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для добавления в избранное")
            return
        
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        category = self.data['categories'][selection[0]]
        
        for item_id in selected:
            item_values = self.item_tree.item(item_id)['values']
            item_name = item_values[1]
            
            for item in category['items']:
                if item['name'] == item_name:
                    item['favorite'] = True
                    break
        
        self.populate_items(category)
        self.save_data()
        self.status_var.set("Элемент добавлен в избранное")
    
    def remove_from_favorites(self):
        """Удаление выбранного элемента из избранного"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления из избранного")
            return
        
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        category = self.data['categories'][selection[0]]
        
        for item_id in selected:
            item_values = self.item_tree.item(item_id)['values']
            item_name = item_values[1]
            
            for item in category['items']:
                if item['name'] == item_name:
                    item['favorite'] = False
                    break
        
        self.populate_items(category)
        self.save_data()
        self.status_var.set("Элемент удалён из избранного")
    
    def show_favorites(self):
        """Показать избранное"""
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Избранное")
        favorites_window.geometry("800x600")
        favorites_window.transient(self.root)
        
        # Создаём таблицу избранного
        columns = ('name', 'value', 'description')
        tree = ttk.Treeview(favorites_window, columns=columns, show='headings', height=20)
        
        tree.heading('name', text='Название')
        tree.heading('value', text='Значение')
        tree.heading('description', text='Описание')
        
        tree.column('name', width=200)
        tree.column('value', width=200)
        tree.column('description', width=300)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заполняем избранное
        for category in self.data['categories']:
            for item in category['items']:
                if item.get('favorite', False):
                    tree.insert('', tk.END, values=(item['name'], item['value'], item['description']))
        
        # Кнопки
        btn_frame = ttk.Frame(favorites_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="📥 Вставить", command=lambda: self.insert_from_favorites(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⭐ Убрать из избранного", command=lambda: self.remove_from_favorites_tree(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=favorites_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def insert_from_favorites(self, tree):
        """Вставка элемента из окна избранного"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        value_to_insert = item_values[1]
        
        pyperclip.copy(value_to_insert)
        
        window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
        hwnd = self.find_masterscada_window(window_title)
        
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            self.simulate_paste()
            self.status_var.set(f"Вставлено из избранного: {value_to_insert}")
    
    def remove_from_favorites_tree(self, tree):
        """Удаление элемента из избранного через окно"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        item_name = item_values[0]
        
        for category in self.data['categories']:
            for item in category['items']:
                if item['name'] == item_name:
                    item['favorite'] = False
                    break
        
        tree.delete(selected[0])
        self.save_data()
    
    def assign_hotkey(self):
        """Назначение горячей клавиши для элемента"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для назначения клавиши")
            return
        
        if len(selected) > 1:
            messagebox.showwarning("Внимание", "Выберите только один элемент")
            return
        
        item_values = self.item_tree.item(selected[0])['values']
        item_name = item_values[1]
        
        # Создаём окно для выбора клавиши
        hotkey_window = tk.Toplevel(self.root)
        hotkey_window.title("Назначение горячей клавиши")
        hotkey_window.geometry("300x150")
        hotkey_window.transient(self.root)
        hotkey_window.grab_set()
        
        ttk.Label(hotkey_window, text=f"Элемент: {item_name}").pack(pady=10)
        ttk.Label(hotkey_window, text="Нажмите клавишу (F1-F12):").pack(pady=5)
        
        hotkey_var = tk.StringVar()
        hotkey_combo = ttk.Combobox(hotkey_window, textvariable=hotkey_var, values=[f"F{i}" for i in range(1, 13)], state="readonly")
        hotkey_combo.pack(pady=5)
        
        def save_hotkey():
            hotkey = hotkey_var.get()
            if not hotkey:
                return
            
            selection = self.category_listbox.curselection()
            if selection:
                category = self.data['categories'][selection[0]]
                for item in category['items']:
                    if item['name'] == item_name:
                        item['hotkey'] = hotkey
                        break
                
                self.populate_items(category)
                self.save_data()
                self.status_var.set(f"Клавиша {hotkey} назначена для: {item_name}")
            
            hotkey_window.destroy()
        
        ttk.Button(hotkey_window, text="Сохранить", command=save_hotkey).pack(pady=10)
    
    def trigger_hotkey(self, hotkey_num):
        """Обработка нажатия горячей клавиши"""
        hotkey = f"F{hotkey_num}"
        
        # Ищем элемент с этой клавишей
        for category in self.data['categories']:
            for item in category['items']:
                if item.get('hotkey') == hotkey:
                    # Вставляем элемент
                    pyperclip.copy(item['value'])
                    
                    window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
                    hwnd = self.find_masterscada_window(window_title)
                    
                    if hwnd:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                        self.simulate_paste()
                        self.status_var.set(f"Вставлено по клавише {hotkey}: {item['name']}")
                        self.add_to_history('hotkey_insert', item['value'])
                        self.update_stats(item['value'])
                    else:
                        self.status_var.set(f"Окно MasterSCADA не найдено. Скопировано: {item['value']}")
                    
                    return
    
    def add_to_history(self, action, value):
        """Добавление записи в историю"""
        self.history.append({
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'value': value
        })
        
        # Ограничиваем историю последними 1000 записями
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self.save_history()
    
    def show_history(self):
        """Показать историю операций"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История операций")
        history_window.geometry("800x600")
        history_window.transient(self.root)
        
        # Создаём таблицу истории
        columns = ('time', 'action', 'value')
        tree = ttk.Treeview(history_window, columns=columns, show='headings', height=25)
        
        tree.heading('time', text='Время')
        tree.heading('action', text='Действие')
        tree.heading('value', text='Значение')
        
        tree.column('time', width=150)
        tree.column('action', width=150)
        tree.column('value', width=400)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заполняем историю (в обратном порядке)
        for record in reversed(self.history):
            action_text = {
                'copy': 'Копирование',
                'insert': 'Вставка',
                'batch_insert': 'Пакетная вставка',
                'hotkey_insert': 'Вставка по клавише'
            }.get(record['action'], record['action'])
            
            tree.insert('', tk.END, values=(record['time'], action_text, record['value']))
        
        # Кнопки
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="📋 Копировать выбранное", command=lambda: self.copy_from_history(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Очистить историю", command=lambda: self.clear_history_from_window(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def copy_from_history(self, tree):
        """Копирование записи из истории"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        value = item_values[2]
        
        pyperclip.copy(value)
        self.status_var.set(f"Скопировано из истории: {value}")
    
    def clear_history_from_window(self, tree):
        """Очистка истории через окно"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            tree.delete(*tree.get_children())
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.status_var.set("История очищена")
    
    def update_stats(self, value):
        """Обновление статистики использования"""
        if value not in self.stats:
            self.stats[value] = 0
        self.stats[value] += 1
        self.save_stats()
    
    def show_statistics(self):
        """Показать статистику использования"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика использования")
        stats_window.geometry("600x400")
        stats_window.transient(self.root)
        
        # Создаём таблицу статистики
        columns = ('value', 'count')
        tree = ttk.Treeview(stats_window, columns=columns, show='headings', height=15)
        
        tree.heading('value', text='Значение')
        tree.heading('count', text='Количество использований')
        
        tree.column('value', width=300)
        tree.column('count', width=150)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Сортируем по количеству использований
        sorted_stats = sorted(self.stats.items(), key=lambda x: x[1], reverse=True)
        
        for value, count in sorted_stats:
            tree.insert('', tk.END, values=(value, count))
        
        # Кнопки
        btn_frame = ttk.Frame(stats_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="📋 Копировать выбранное", command=lambda: self.copy_from_stats(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Сбросить статистику", command=lambda: self.reset_stats_from_window(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=stats_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def copy_from_stats(self, tree):
        """Копирование записи из статистики"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        value = item_values[0]
        
        pyperclip.copy(value)
        self.status_var.set(f"Скопировано из статистики: {value}")
    
    def reset_stats_from_window(self, tree):
        """Сброс статистики через окно"""
        if messagebox.askyesno("Подтверждение", "Сбросить всю статистику?"):
            self.stats = {}
            self.save_stats()
            tree.delete(*tree.get_children())
    
    def reset_statistics(self):
        """Сброс статистики"""
        if messagebox.askyesno("Подтверждение", "Сбросить всю статистику?"):
            self.stats = {}
            self.save_stats()
            self.status_var.set("Статистика сброшена")
    
    def create_template(self):
        """Создание шаблона проекта из выбранных элементов"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элементы для создания шаблона")
            return
        
        template_name = simpledialog.askstring("Новый шаблон", "Введите название шаблона:")
        if not template_name:
            return
        
        items = []
        for item_id in selected:
            item_values = self.item_tree.item(item_id)['values']
            items.append({
                'name': item_values[1],
                'value': item_values[2],
                'description': item_values[3]
            })
        
        self.templates.append({
            'name': template_name,
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'items': items
        })
        
        self.save_templates()
        self.status_var.set(f"Шаблон '{template_name}' создан ({len(items)} элементов)")
    
    def show_templates(self):
        """Показать шаблоны проектов"""
        templates_window = tk.Toplevel(self.root)
        templates_window.title("Шаблоны проектов")
        templates_window.geometry("800x600")
        templates_window.transient(self.root)
        
        # Создаём таблицу шаблонов
        columns = ('name', 'created', 'items_count')
        tree = ttk.Treeview(templates_window, columns=columns, show='headings', height=20)
        
        tree.heading('name', text='Название')
        tree.heading('created', text='Создан')
        tree.heading('items_count', text='Элементов')
        
        tree.column('name', width=250)
        tree.column('created', width=150)
        tree.column('items_count', width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заполняем шаблоны
        for template in self.templates:
            tree.insert('', tk.END, values=(template['name'], template['created'], len(template['items'])))
        
        # Кнопки
        btn_frame = ttk.Frame(templates_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="📥 Применить шаблон", command=lambda: self.apply_template_from_window(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="👁️ Просмотреть", command=lambda: self.view_template(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=lambda: self.delete_template(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=templates_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def apply_template_from_window(self, tree):
        """Применение шаблона через окно"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        template_name = item_values[0]
        
        # Находим шаблон
        template = None
        for t in self.templates:
            if t['name'] == template_name:
                template = t
                break
        
        if not template:
            return
        
        # Объединяем все элементы шаблона
        values = [item['value'] for item in template['items']]
        combined_text = '\n'.join(values)
        
        pyperclip.copy(combined_text)
        
        window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
        hwnd = self.find_masterscada_window(window_title)
        
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            self.simulate_paste()
            self.status_var.set(f"Шаблон '{template_name}' применён ({len(values)} элементов)")
            self.add_to_history('template_apply', f"{template_name}: {len(values)} элементов")
        else:
            self.status_var.set(f"Окно MasterSCADA не найдено. Шаблон скопирован: {len(values)} элементов")
    
    def view_template(self, tree):
        """Просмотр содержимого шаблона"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        template_name = item_values[0]
        
        # Находим шаблон
        template = None
        for t in self.templates:
            if t['name'] == template_name:
                template = t
                break
        
        if not template:
            return
        
        # Создаём окно просмотра
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Шаблон: {template_name}")
        view_window.geometry("600x400")
        view_window.transient(self.root)
        
        text = tk.Text(view_window, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for item in template['items']:
            text.insert(tk.END, f"{item['name']}: {item['value']}\n")
            text.insert(tk.END, f"  {item['description']}\n\n")
        
        text.config(state=tk.DISABLED)
    
    def delete_template(self, tree):
        """Удаление шаблона"""
        selected = tree.selection()
        if not selected:
            return
        
        item_values = tree.item(selected[0])['values']
        template_name = item_values[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить шаблон '{template_name}'?"):
            self.templates = [t for t in self.templates if t['name'] != template_name]
            self.save_templates()
            tree.delete(selected[0])
    
    def apply_template(self):
        """Быстрое применение шаблона"""
        if not self.templates:
            messagebox.showinfo("Шаблоны", "Нет сохранённых шаблонов")
            return
        
        # Создаём простой диалог выбора
        template_names = [t['name'] for t in self.templates]
        
        apply_window = tk.Toplevel(self.root)
        apply_window.title("Применить шаблон")
        apply_window.geometry("300x200")
        apply_window.transient(self.root)
        apply_window.grab_set()
        
        ttk.Label(apply_window, text="Выберите шаблон:").pack(pady=10)
        
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(apply_window, textvariable=template_var, values=template_names, state="readonly")
        template_combo.pack(pady=5)
        if template_names:
            template_combo.current(0)
        
        def do_apply():
            template_name = template_var.get()
            if not template_name:
                return
            
            for t in self.templates:
                if t['name'] == template_name:
                    values = [item['value'] for item in t['items']]
                    combined_text = '\n'.join(values)
                    
                    pyperclip.copy(combined_text)
                    
                    window_title = self.settings.get("masterscada_window_title", "MasterSCADA")
                    hwnd = self.find_masterscada_window(window_title)
                    
                    if hwnd:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                        self.simulate_paste()
                        self.status_var.set(f"Шаблон '{template_name}' применён ({len(values)} элементов)")
                        self.add_to_history('template_apply', f"{template_name}: {len(values)} элементов")
                    else:
                        self.status_var.set(f"Окно MasterSCADA не найдено. Шаблон скопирован: {len(values)} элементов")
                    
                    break
            
            apply_window.destroy()
        
        ttk.Button(apply_window, text="Применить", command=do_apply).pack(pady=10)
    
    def export_to_text(self):
        """Экспорт выбранных элементов в текстовый файл"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элементы для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for item_id in selected:
                    item_values = self.item_tree.item(item_id)['values']
                    f.write(f"{item_values[2]}\n")
            
            self.status_var.set(f"Экспортировано {len(selected)} элементов в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.settings.get("minimize_to_tray", True) and TRAY_AVAILABLE:
            self.minimize_to_tray()
        else:
            self.quit_app()
    
    def minimize_to_tray(self):
        """Минимизация в трей"""
        if not TRAY_AVAILABLE:
            self.quit_app()
            return
        
        self.root.withdraw()
        self.is_in_tray = True
        
        # Создаём иконку для трея
        image = self.create_tray_icon()
        
        menu = (
            pystray.MenuItem("Открыть", self.restore_from_tray),
            pystray.MenuItem("Выход", self.quit_from_tray)
        )
        
        self.tray_icon = pystray.Icon("MasterSCADA Helper", image, "MasterSCADA Helper", menu)
        self.tray_icon.run()
    
    def create_tray_icon(self):
        """Создание иконки для трея"""
        # Создаём простую иконку
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        dc.rectangle([0, 0, width, height], fill='blue')
        dc.text((10, 10), "MS", fill='white')
        return image
    
    def restore_from_tray(self):
        """Восстановление из трея"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.is_in_tray = False
        self.root.deiconify()
    
    def quit_from_tray(self):
        """Выход из трея"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.quit_app()
    
    def quit_app(self):
        """Полный выход из приложения"""
        self.save_data()
        self.save_settings()
        self.save_history()
        self.save_templates()
        self.save_stats()
        self.root.quit()
    
    def schedule_backup(self):
        """Планирование резервного копирования"""
        if not self.settings.get("backup_enabled", True):
            return
        
        interval_ms = self.settings.get("backup_interval_hours", 24) * 3600 * 1000
        
        def backup_task():
            self.create_backup()
            self.root.after(interval_ms, backup_task)
        
        self.root.after(interval_ms, backup_task)
    
    def create_backup(self):
        """Создание резервной копии"""
        try:
            backup_dir = os.path.join(self.data_dir, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Копируем основные файлы
            files_to_backup = [
                self.data_file,
                self.settings_file,
                self.history_file,
                self.templates_file,
                self.stats_file
            ]
            
            for file in files_to_backup:
                if os.path.exists(file):
                    backup_name = f"{timestamp}_{file}"
                    shutil.copy2(file, os.path.join(backup_dir, backup_name))
            
            # Удаляем старые резервные копии (оставляем последние 10)
            self.cleanup_old_backups()
            
        except Exception as e:
            print(f"Backup error: {e}")
    
    def cleanup_old_backups(self):
        """Очистка старых резервных копий"""
        backup_dir = os.path.join(self.data_dir, "backups")
        if not os.path.exists(backup_dir):
            return
        
        backups = []
        for file in os.listdir(backup_dir):
            if file.endswith('.json'):
                backups.append(os.path.join(backup_dir, file))
        
        backups.sort(key=os.path.getmtime, reverse=True)
        
        # Удаляем все, кроме последних 10
        for backup in backups[10:]:
            try:
                os.remove(backup)
            except:
                pass
    
    def show_backup_settings(self):
        """Настройки резервного копирования"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки резервного копирования")
        settings_window.geometry("400x200")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        backup_enabled_var = tk.BooleanVar(value=self.settings.get("backup_enabled", True))
        ttk.Checkbutton(settings_window, text="Включить резервное копирование", variable=backup_enabled_var).pack(pady=10)
        
        ttk.Label(settings_window, text="Интервал резервного копирования (часы):").pack(pady=5)
        interval_var = tk.IntVar(value=self.settings.get("backup_interval_hours", 24))
        ttk.Spinbox(settings_window, from_=1, to=168, textvariable=interval_var, width=10).pack(pady=5)
        
        def save_settings():
            self.settings["backup_enabled"] = backup_enabled_var.get()
            self.settings["backup_interval_hours"] = interval_var.get()
            self.save_settings()
            settings_window.destroy()
            self.status_var.set("Настройки резервного копирования сохранены")
        
        ttk.Button(settings_window, text="Сохранить", command=save_settings).pack(pady=10)
    
    def show_autostart_settings(self):
        """Настройки автозапуска"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки автозапуска")
        settings_window.geometry("400x150")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        autostart_var = tk.BooleanVar(value=self.settings.get("autostart", False))
        ttk.Checkbutton(settings_window, text="Запускать при старте Windows", variable=autostart_var).pack(pady=20)
        
        def save_settings():
            self.settings["autostart"] = autostart_var.get()
            self.save_settings()
            
            if autostart_var.get():
                self.enable_autostart()
            else:
                self.disable_autostart()
            
            settings_window.destroy()
            self.status_var.set("Настройки автозапуска сохранены")
        
        ttk.Button(settings_window, text="Сохранить", command=save_settings).pack(pady=10)
    
    def enable_autostart(self):
        """Включение автозапуска"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            exe_path = os.path.abspath(__file__)
            winreg.SetValueEx(key, "MasterSCADAHelper", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось включить автозапуск: {str(e)}")
    
    def disable_autostart(self):
        """Выключение автозапуска"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "MasterSCADAHelper")
            except:
                pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выключить автозапуск: {str(e)}")
    
    def show_insert_settings(self):
        """Настройки вставки"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки вставки")
        settings_window.geometry("500x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Заголовок окна MasterSCADA:").pack(pady=(10, 5))
        title_var = tk.StringVar(value=self.settings.get("masterscada_window_title", "MasterSCADA"))
        ttk.Entry(settings_window, textvariable=title_var, width=50).pack(pady=5)
        
        ttk.Label(settings_window, text="Режим поиска:").pack(pady=(10, 5))
        search_mode_var = tk.StringVar(value=self.settings.get("search_mode", "contains"))
        ttk.Radiobutton(settings_window, text="Содержит (гибкий поиск)", variable=search_mode_var, value="contains").pack()
        ttk.Radiobutton(settings_window, text="Точное совпадение", variable=search_mode_var, value="exact").pack()
        
        auto_insert_var = tk.BooleanVar(value=self.settings.get("auto_insert", True))
        ttk.Checkbutton(settings_window, text="Автоматическая вставка при двойном клике", variable=auto_insert_var).pack(pady=10)
        
        minimize_tray_var = tk.BooleanVar(value=self.settings.get("minimize_to_tray", True))
        ttk.Checkbutton(settings_window, text="Минимизировать в трей при закрытии", variable=minimize_tray_var).pack(pady=5)
        
        def save_settings():
            self.settings["masterscada_window_title"] = title_var.get()
            self.settings["auto_insert"] = auto_insert_var.get()
            self.settings["search_mode"] = search_mode_var.get()
            self.settings["minimize_to_tray"] = minimize_tray_var.get()
            self.save_settings()
            settings_window.destroy()
            self.status_var.set("Настройки сохранены")
        
        ttk.Button(settings_window, text="Сохранить", command=save_settings).pack(pady=10)
    
    def set_masterscada_version(self, window_title):
        """Установка версии MasterSCADA"""
        self.settings["masterscada_window_title"] = window_title
        self.save_settings()
        self.status_var.set(f"Установлена версия MasterSCADA: {window_title}")
    
    def on_search_change(self, *args):
        """Обработка изменения текста поиска"""
        search_text = self.search_var.get().lower()
        if len(search_text) >= 2:
            self.perform_search()
    
    def perform_search(self):
        """Выполнение поиска по всем элементам"""
        search_text = self.search_var.get().lower()
        if not search_text:
            return
        
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
        
        found_items = []
        for category in self.data['categories']:
            for item in category['items']:
                if (search_text in item['name'].lower() or 
                    search_text in item['value'].lower() or 
                    search_text in item['description'].lower()):
                    found_items.append(item)
        
        found_items.sort(key=lambda x: x['name'].lower())
        
        for item in found_items:
            favorite_mark = "⭐" if item.get('favorite', False) else ""
            hotkey_mark = item.get('hotkey', '') or ''
            # Показываем только первую строку значения в таблице
            display_value = item['value'].split('\n')[0]
            self.item_tree.insert('', tk.END, values=(favorite_mark, item['name'], display_value, item['description'], hotkey_mark))
        
        self.status_var.set(f"Поиск: '{search_text}' | Найдено: {len(found_items)}")
    
    def clear_search(self):
        """Очистка поиска"""
        self.search_var.set("")
        selection = self.category_listbox.curselection()
        if selection:
            category = self.data['categories'][selection[0]]
            self.populate_items(category)
    
    def find_masterscada_installation(self):
        """Поиск установленной версии MasterSCADA"""
        possible_paths = []
        
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if "masterscada" in display_name.lower():
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                if install_location:
                                    possible_paths.append(install_location)
                    except:
                        pass
        except:
            pass
        
        standard_paths = [
            r"C:\Program Files\MasterSCADA",
            r"C:\Program Files (x86)\MasterSCADA",
            r"C:\MasterSCADA",
            os.path.expanduser(r"~\Documents\MasterSCADA"),
            os.path.expanduser(r"~\Desktop\MasterSCADA"),
        ]
        
        for path in standard_paths:
            if os.path.exists(path):
                possible_paths.append(path)
        
        return possible_paths
    
    def select_masterscada_folder(self):
        """Ручной выбор папки MasterSCADA"""
        folder = filedialog.askdirectory(title="Выберите папку с проектами MasterSCADA")
        if folder:
            self.scan_masterscada_folder(folder)
    
    def scan_masterscada(self):
        """Сканирование установленной версии MasterSCADA"""
        self.status_var.set("Поиск установленной версии MasterSCADA...")
        self.root.update()
        
        paths = self.find_masterscada_installation()
        
        if not paths:
            messagebox.showinfo(
                "MasterSCADA не найдена",
                "Установленная версия MasterSCADA не найдена автоматически.\n\n"
                "Пожалуйста, укажите папку с проектами MasterSCADA вручную."
            )
            self.select_masterscada_folder()
            return
        
        selected_path = paths[0]
        self.scan_masterscada_folder(selected_path)
    
    def scan_masterscada_folder(self, folder_path):
        """Сканирование папки с проектами MasterSCADA"""
        self.status_var.set(f"Сканирование: {folder_path}")
        self.root.update()
        
        project_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.mprj', '.mdb', '.xml', '.cfg', '.ini', '.json')):
                    project_files.append(os.path.join(root, file))
        
        if not project_files:
            messagebox.showinfo(
                "Файлы не найдены",
                f"В папке {folder_path} не найдены файлы проектов MasterSCADA.\n\n"
                "Поддерживаемые форматы: .mprj, .mdb, .xml, .cfg, .ini, .json"
            )
            return
        
        extracted_data = self.extract_data_from_files(project_files)
        
        if not extracted_data:
            messagebox.showinfo(
                "Данные не найдены",
                "Не удалось извлечь данные из файлов проекта.\n"
                "Возможно, формат файлов не поддерживается."
            )
            return
        
        self.update_database_from_scan(extracted_data)
        
        self.status_var.set(f"Сканирование завершено. Найдено файлов: {len(project_files)}")
        messagebox.showinfo(
            "Сканирование завершено",
            f"Успешно просканировано файлов: {len(project_files)}\n"
            f"Извлечено элементов: {sum(len(cat['items']) for cat in self.data['categories'])}"
        )
    
    def extract_data_from_files(self, file_paths):
        """Извлечение данных из файлов проекта MasterSCADA"""
        extracted = {
            "tags": [],
            "devices": [],
            "alarms": [],
            "scripts": [],
            "parameters": []
        }
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                tag_pattern = r'(?:Tag|Переменная|Variable)[\s]*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)'
                tags = re.findall(tag_pattern, content, re.IGNORECASE)
                for tag in set(tags):
                    if len(tag) > 2 and tag not in [t['value'] for t in extracted['tags']]:
                        extracted['tags'].append({
                            "name": tag,
                            "value": tag,
                            "description": f"Тег из проекта ({os.path.basename(file_path)})",
                            "favorite": False,
                            "hotkey": None
                        })
                
                device_pattern = r'(?:Device|Устройство)[\s]*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)'
                devices = re.findall(device_pattern, content, re.IGNORECASE)
                for device in set(devices):
                    if len(device) > 2 and device not in [d['value'] for d in extracted['devices']]:
                        extracted['devices'].append({
                            "name": device,
                            "value": device,
                            "description": f"Устройство из проекта ({os.path.basename(file_path)})",
                            "favorite": False,
                            "hotkey": None
                        })
                
                alarm_pattern = r'(?:Alarm|Авар|Событие)[\s]*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)'
                alarms = re.findall(alarm_pattern, content, re.IGNORECASE)
                for alarm in set(alarms):
                    if len(alarm) > 2 and alarm not in [a['value'] for a in extracted['alarms']]:
                        extracted['alarms'].append({
                            "name": alarm,
                            "value": alarm,
                            "description": f"Событие из проекта ({os.path.basename(file_path)})",
                            "favorite": False,
                            "hotkey": None
                        })
                
            except Exception as e:
                continue
        
        return extracted
    
    def update_database_from_scan(self, extracted_data):
        """Обновление базы данных из результатов сканирования"""
        new_categories = []
        
        if extracted_data['tags']:
            new_categories.append({
                "name": "Теги проекта",
                "icon": "🏷️",
                "items": sorted(extracted_data['tags'], key=lambda x: x['name'].lower())
            })
        
        if extracted_data['devices']:
            new_categories.append({
                "name": "Устройства проекта",
                "icon": "🔧",
                "items": sorted(extracted_data['devices'], key=lambda x: x['name'].lower())
            })
        
        if extracted_data['alarms']:
            new_categories.append({
                "name": "События проекта",
                "icon": "🚨",
                "items": sorted(extracted_data['alarms'], key=lambda x: x['name'].lower())
            })
        
        self.data['categories'] = new_categories + self.data['categories']
        self.populate_categories()
        self.save_data()
    
    def add_category(self):
        """Добавление новой категории"""
        name = simpledialog.askstring("Новая категория", "Введите название категории:")
        if name:
            icon = simpledialog.askstring("Иконка", "Введите иконку (emoji):", initialvalue="📁")
            if icon:
                new_category = {
                    "name": name,
                    "icon": icon,
                    "items": []
                }
                self.data['categories'].append(new_category)
                self.populate_categories()
                self.save_data()
                self.status_var.set(f"Добавлена категория: {name}")
    
    def edit_category(self):
        """Редактирование категории"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для редактирования")
            return
        
        category = self.data['categories'][selection[0]]
        name = simpledialog.askstring("Редактирование", "Название категории:", initialvalue=category['name'])
        if name:
            icon = simpledialog.askstring("Редактирование", "Иконка:", initialvalue=category['icon'])
            if icon:
                category['name'] = name
                category['icon'] = icon
                self.populate_categories()
                self.save_data()
    
    def delete_category(self):
        """Удаление категории"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для удаления")
            return
        
        category = self.data['categories'][selection[0]]
        if messagebox.askyesno("Подтверждение", f"Удалить категорию '{category['name']}'?"):
            self.data['categories'].pop(selection[0])
            self.populate_categories()
            self.save_data()
            self.status_var.set(f"Удалена категория: {category['name']}")
    
    def add_item(self):
        """Добавление нового элемента"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите категорию")
            return
        
        category = self.data['categories'][selection[0]]
        
        name = simpledialog.askstring("Новый элемент", "Название:")
        if name:
            value = simpledialog.askstring("Новый элемент", "Значение (текст для вставки):")
            if value:
                description = simpledialog.askstring("Новый элемент", "Описание:", initialvalue="")
                if description is not None:
                    new_item = {
                        "name": name,
                        "value": value,
                        "description": description,
                        "favorite": False,
                        "hotkey": None
                    }
                    category['items'].append(new_item)
                    self.populate_items(category)
                    self.save_data()
                    self.status_var.set(f"Добавлен элемент: {name}")
    
    def edit_selected(self):
        """Редактирование выбранного элемента"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для редактирования")
            return
        
        item_values = self.item_tree.item(selected[0])['values']
        
        name = simpledialog.askstring("Редактирование", "Название:", initialvalue=item_values[1])
        if name:
            value = simpledialog.askstring("Редактирование", "Значение:", initialvalue=item_values[2])
            if value:
                description = simpledialog.askstring("Редактирование", "Описание:", initialvalue=item_values[3])
                if description is not None:
                    selection = self.category_listbox.curselection()
                    if selection:
                        category = self.data['categories'][selection[0]]
                        for item in category['items']:
                            if item['name'] == item_values[1]:
                                item['name'] = name
                                item['value'] = value
                                item['description'] = description
                                break
                        self.populate_items(category)
                        self.save_data()
    
    def delete_selected(self):
        """Удаление выбранного элемента"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return
        
        item_values = self.item_tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", f"Удалить элемент '{item_values[1]}'?"):
            selection = self.category_listbox.curselection()
            if selection:
                category = self.data['categories'][selection[0]]
                category['items'] = [item for item in category['items'] if item['name'] != item_values[1]]
                self.populate_items(category)
                self.save_data()
                self.status_var.set(f"Удалён элемент: {item_values[1]}")
    
    def export_data(self):
        """Экспорт базы данных"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"База экспортирована: {filename}")
    
    def import_data(self):
        """Импорт базы данных"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.populate_categories()
                self.save_data()
                self.status_var.set(f"База импортирована: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {str(e)}")
    
    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo(
            "О программе",
            "MasterSCADA Helper\n\n"
            "Версия: 5.0\n"
            "Назначение: Помощник для работы со всеми версиями MasterSCADA\n\n"
            "Поддерживаемые версии:\n"
            "• MasterSCADA 4.0\n"
            "• MasterSCADA 4.1\n"
            "• MasterSCADA 4.2\n"
            "• MasterSCADA 4D\n"
            "• MasterSCADA 3.x\n"
            "• И другие версии\n\n"
            "Возможности:\n"
            "• Автоматическое сканирование проектов MasterSCADA\n"
            "• Автоматическая вставка в MasterSCADA\n"
            "• Избранное для быстрого доступа\n"
            "• Горячие клавиши (F1-F12)\n"
            "• Пакетная вставка нескольких элементов\n"
            "• Шаблоны проектов\n"
            "• История операций\n"
            "• Статистика использования\n"
            "• Минимизация в трей\n"
            "• Автозапуск при старте Windows\n"
            "• Резервное копирование\n"
            "• Экспорт/импорт базы данных\n\n"
            "Совместимо со всеми версиями MasterSCADA"
        )
    
    def show_hotkeys(self):
        """Показать горячие клавиши"""
        messagebox.showinfo(
            "Горячие клавиши",
            "Ctrl+F - Фокус на поле поиска\n"
            "Ctrl+C - Копировать выбранный элемент\n"
            "Ctrl+I - Вставить в MasterSCADA\n"
            "Ctrl+B - Пакетная вставка\n"
            "Ctrl+T - Показать шаблоны\n"
            "Ctrl+H - Показать историю\n"
            "Ctrl+S - Сканировать MasterSCADA\n"
            "Ctrl+Q - Выход из программы\n"
            "F1-F12 - Вставка элементов с назначенными клавишами\n"
            "Двойной клик - Вставить в MasterSCADA\n"
            "Правый клик - Контекстное меню"
        )


def main():
    root = tk.Tk()
    app = MasterSCADAHelper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
