import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import logging
from tkinter import font
from tkinter import scrolledtext
from emitter import global_emitter
from service.auth_manager import auth_manager
from service.emailservice import EmailService
from tkinter import scrolledtext, messagebox, Toplevel, filedialog
import smtplib
from modalreport import ModalReport
from modalinfo import ModalInfo
from .UI.ui import *
from .UI.header import Header
import os
import config as cfg

class AppGUI:
    def __init__(self, root, core_instance=None):
        self.root = root
        self.core = core_instance
        self.header = Header(self.root)
        self.setup_ui()  # Сначала создаем UI
        self.setup_logging()  # Затем настраиваем логирование
        self.email_service = EmailService()
        self.modal_report = ModalReport(self.root, self.email_service)
        self.modal_info = ModalInfo(self.root)
    
    def setup_logging(self):
        """Настройка логирования - ВЫЗЫВАЕТСЯ ПОСЛЕ создания console_text"""
        # Проверяем что console_text существует
        if hasattr(self, 'console_text'):
            self.log_handler = LogTextHandler(self.console_text)
            print("✅ Логирование настроено")
        else:
            print("⚠️ console_text еще не создан")
    
    def setup_ui(self):
        if not auth_manager.check_auth():
            self.show_auth_warning()
            return
        
        self.root.title("🚀 KLIK KLAK")
        self.root.geometry("800x650")
        self.root.configure(bg="#152238")
        self.root.resizable(True, True)
        
        # Создаем стиль для виджетов
        self.setup_styles()
        
        # Заголовок приложения
        self.header.create_header()
        
        # Основной контент
        self.create_main_content()
        
        # Футер
        self.create_footer()

        
        # Тестовые логи для демонстрации
        logging.info("🚀 Приложение KLIK KLAK запущено")
        logging.info("✅ Все системы работают нормально")
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настраиваем стили для различных элементов
        self.style.configure("Modern.TLabel", 
                           background="#152238", 
                           foreground="white",
                           font=("Arial", 10))

    def create_main_content(self):
        main_frame = tk.Frame(self.root, bg="#152238")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая панель - настройки
        self.create_settings_panel(main_frame)
        
        # Правая панель - консоль
        self.create_console_panel(main_frame)  # Здесь создается console_text
    
    def create_settings_panel(self, parent):
        settings_container = tk.Frame(parent, bg="#152238")
        settings_container.pack(side="left", fill="both", padx=(0, 10))
        
        # Фрейм настроек
        settings_frame = RoundedFrame(settings_container, radius=15, color="#1E2B3E", width=350, height=450)
        settings_frame.pack(fill="both", expand=True)
        
        # Заголовок настроек
        settings_title = tk.Label(
            settings_container,
            text="⚙️ Настройки браузера",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        settings_title.place(x=20, y=10)
        
        # Поля ввода
        input_y = 50
        field_spacing = 55
        
        # URL
        tk.Label(settings_container, text="URL сайта", fg="white", bg="#1E2B3E", 
                font=("Arial", 10, "bold")).place(x=30, y=input_y)
        self.url_entry = ModernEntry(settings_container, placeholder="https://example.com", width=25)
        self.url_entry.place(x=30, y=input_y + 25)
        
        # Таймаут
        tk.Label(settings_container, text="Таймаут (сек)", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing)
        self.timeout_entry = ModernEntry(settings_container, placeholder="0.5", width=25)
        self.timeout_entry.place(x=30, y=input_y + field_spacing + 25)
        
        # Повторы
        tk.Label(settings_container, text="Количество повторов", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*2)
        self.retries_entry = ModernEntry(settings_container, placeholder="3", width=25)
        self.retries_entry.place(x=30, y=input_y + field_spacing*2 + 25)
        
        # Классы для кликов
        tk.Label(settings_container, text="Класс первого клика", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*3)
        self.first_click_entry = ModernEntry(settings_container, placeholder="MuiTableRow-root", width=25)
        self.first_click_entry.place(x=30, y=input_y + field_spacing*3 + 25)
        
        tk.Label(settings_container, text="Класс второго клика", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*4)
        self.last_click_entry = ModernEntry(settings_container, placeholder="MuiButtonBase-root", width=25)
        self.last_click_entry.place(x=30, y=input_y + field_spacing*4 + 25)
        
        tk.Label(settings_container, text="Класс модального окна", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*5)
        self.modal_entry = ModernEntry(settings_container, placeholder="MuiPaper-root", width=25)
        self.modal_entry.place(x=30, y=input_y + field_spacing*5 + 25)
        
        # Кнопки управления
        buttons_y = input_y + field_spacing*6 + 30
        
        # Кнопка Save and Run
        self.save_run_btn = tk.Button(
            settings_container,
            text="Сохранить и Запустить",
            command=self.on_save_run,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2,
            relief="flat"
        )
        self.save_run_btn.place(x=25, y=buttons_y)

        self.run_btn = tk.Button(
            settings_container,
            text="Запуск",
            command=self.on_run,
            bg="#388662",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=1,
            relief="flat"
        )
        self.run_btn.place(x=25, y=buttons_y + 60)

        self.stop_btn = tk.Button(
            settings_container,
            text="Стоп",
            command=self.on_stop,
            bg="#D32F2F",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=1,
            relief="flat"
        )
        self.stop_btn.place(x=165, y=buttons_y + 60)
    
    def create_console_panel(self, parent):
        console_container = tk.Frame(parent, bg="#152238")
        console_container.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Фрейм консоли
        console_frame = RoundedFrame(console_container, radius=15, color="#1E2B3E")
        console_frame.pack(fill="both", expand=True)
        
        # Заголовок консоли
        console_title = tk.Label(
            console_container,
            text="📟 Консоль выполнения",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        console_title.place(x=20, y=10)
        
        # Текстовое поле консоли - СОЗДАЕТСЯ ЗДЕСЬ
        self.console_text = scrolledtext.ScrolledText(
            console_container,
            wrap=tk.WORD,
            width=45,
            height=20,
            bg="#0D1B2A",
            fg="#E0E0E0",
            font=("Consolas", 9),
            insertbackground="white",
            selectbackground="#2D4A5D",
            relief="flat",
            padx=10,
            pady=10
        )
        self.console_text.place(x=20, y=50, width=360, height=350)
        
        # Поле ввода команд
        input_frame = tk.Frame(console_container, bg="#1E2B3E")
        input_frame.place(x=20, y=410, width=360, height=40)
        
        self.console_input = ModernEntry(input_frame, placeholder="Введите команду...", width=30)
        self.console_input.place(x=0, y=0)
        
        # Кнопка отправки команды
        self.send_btn = tk.Button(
            input_frame,
            text="📤",
            command=self.process_console_command,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12),
            width=3,
            height=1,
            relief="flat"
        )
        self.send_btn.place(x=323, y=2)
    
    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg="#1E2B3E", height=30)
        footer_frame.pack(fill="x", side="bottom", padx=20, pady=5)

        # Кнопка информации (теперь слева)
        info_btn = tk.Label(
            footer_frame,
            text="ℹ Информаиця",
            font=("Arial", 9, "underline"),
            fg="#4FC3F7",
            bg="#1E2B3E",
            cursor="hand2"
        )
        info_btn.pack(side="left", padx=10) 
        info_btn.bind("<Button-1>", lambda e: self.modal_info.open_windowinfo())

        # Кнопка обратной связи 
        feedback_btn = tk.Label(
            footer_frame,
            text="📧 Сообщить об ошибке",
            font=("Arial", 9, "underline"),
            fg="#4FC3F7",
            bg="#1E2B3E",
            cursor="hand2"
        )
        feedback_btn.pack(side="right", padx=10) 
        feedback_btn.bind("<Button-1>", lambda e: self.modal_report.open_feedback_window())

    def write_to_console(self, message, level=logging.INFO):
        """Добавляет текст в консоль с указанным уровнем"""
        if not hasattr(self, 'console_text'):
            print(f"⚠️ Console text not available: {message}")
            return
            
        self.console_text.configure(state='normal')
        
        if level >= logging.ERROR:
            tag = "ERROR"
        elif level >= logging.WARNING:
            tag = "WARNING"
        elif level >= logging.INFO:
            tag = "INFO"
        elif level >= logging.CRITICAL:
            tag = "CRITICAL"
        else:
            tag = "DEBUG"
            
        self.console_text.insert(tk.END, message, tag)
        self.console_text.configure(state='disabled')
        self.console_text.see(tk.END)
    
    def process_console_command(self, event=None):
        """Обрабатывает команды из консоли"""
        command = self.console_input.entry.get().strip()
        if command and command != self.console_input.placeholder:
            self.write_to_console(f"→ {command}\n")
            
            if command.lower() == "help":
                self.show_help()
            elif command.lower() == "clear":
                self.clear_console()
            elif command.lower() == "status":
                self.write_to_console("✅ Система работает нормально\n")
            else:
                self.write_to_console(f"❌ Неизвестная команда: {command}\n")
            
            self.console_input.entry.delete(0, tk.END)
    
    def show_help(self):
        """Список доступных команд"""
        help_text = """
        Доступные команды:
        • help - показать справку
        • clear - очистить консоль  
        • status - статус системы
        """
        self.write_to_console(help_text)
    
    def clear_console(self):
        """Очистка консоли"""
        if hasattr(self, 'console_text'):
            self.console_text.configure(state='normal')
            self.console_text.delete(1.0, tk.END)
            self.console_text.configure(state='disabled')
            self.write_to_console("🧹 Консоль очищена\n")
    
    def show_auth_warning(self):
        """Показывает предупреждение об отсутствии авторизации"""
        warning_frame = tk.Frame(self.root, bg='#1E2B3E', padx=20, pady=20)
        warning_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            warning_frame, 
            text="🔒 Требуется авторизация", 
            font=("Arial", 16, "bold"),
            fg="#FF6B6B",
            bg='#1E2B3E'
        ).pack(pady=20)
        
        tk.Label(
            warning_frame,
            text="Для использования KLIK KLAK требуется авторизация",
            font=("Arial", 12),
            fg="#B0BEC5",
            bg='#1E2B3E'
        ).pack(pady=10)

    def on_save_run(self):
        """Обработчик кнопки Save and Run"""
        params = {
            'url': self.url_entry.get(),
            'timeout': float(self.timeout_entry.get()) if self.timeout_entry.get().strip() else 0.5,
            'max_retries': int(self.retries_entry.get()) if self.retries_entry.get().strip() else 3,
            'classOneClick': self.first_click_entry.get(),
            'classTwoClick': self.last_click_entry.get(),
            'classModal': self.modal_entry.get()
        }
        
        # Фильтруем только заполненные параметры
        filtered_params = {k: v for k, v in params.items() if v}
        
        if params['url']:
            logging.info(f"🚀 Запуск процесса для URL: {params['url']}")
            # Передаем параметры как аргументы
            self.start_process(
                url=filtered_params.get('url', ''),
                timeout=filtered_params.get('timeout', 0.5),
                max_retries=filtered_params.get('max_retries', 3),
                classOneClick=filtered_params.get('classOneClick', 'MuiTableRow-root'),
                classTwoClick=filtered_params.get('classTwoClick', 'MuiButtonBase-root'),
                classModal=filtered_params.get('classModal', 'MuiPaper-root')
            )
        else:
            logging.warning("⚠️ URL не указан")
    
    def on_run(self):
        url = self.url_entry.get()
        if url:
            logging.info(f"🚀 Запуск процесса для URL: {url}")
            self.start_process(url)
        else:
            logging.warning("⚠️ URL не указан")
    
    def on_stop(self):
        logging.info("🛑 Остановка процесса")
        self.stop_process()
    
    def stop_process(self):
        def stop_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.core:
                    loop.run_until_complete(self.core.stop_main_process())
                logging.info("✅ Процесс остановлен")
            except Exception as e:
                logging.error(f"❌ Ошибка при остановке: {e}")
            finally:
                loop.close()

        thread = threading.Thread(target=stop_async)
        thread.daemon = True
        thread.start()

    def start_process(self, url, timeout=0.5, max_retries=3, classOneClick="MuiTableRow-root", classTwoClick="MuiButtonBase-root", classModal="MuiPaper-root"):
        """Запускает основной процесс в отдельном потоке"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.core:
                    loop.run_until_complete(self.core.run_main_process(url, timeout, max_retries, classOneClick, classTwoClick, classModal))
                else:
                    logging.info(f"🔧 Запущен демо-процесс для {url}")
                    loop.run_until_complete(self.demo_process(url))
            except Exception as e:
                logging.error(f"❌ Ошибка в процессе: {e}")
            finally:
                loop.close()

        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()