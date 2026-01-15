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
import json
import base64
import hashlib
from cryptography.fernet import Fernet

class AppGUI:
    def __init__(self, root, core_instance=None):
        self.root = root
        self.core = core_instance
        self.header = Header(self.root)
        self.encryption_key = self._get_encryption_key() # Ключ для шифрования (можно сохранить в отдельный файл или использовать фиксированный)
        self.setup_ui()  # Сначала создаем UI
        self.setup_logging()  # Затем настраиваем логирование
        self.email_service = EmailService()
        self.modal_report = ModalReport(self.root, self.email_service)
        self.modal_info = ModalInfo(self.root)

        # Загружаем сохраненную конфигурацию
        self.load_config()

    def _get_encryption_key(self):
        "Получаем или создаем ключ шифрования"
        key_path = os.path.join(os.path.dirname(__file__), 'config_key.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # Создаем новый ключ
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
        
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
        self.root.geometry("800x690")
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
        settings_frame = RoundedFrame(settings_container, radius=15, color="#1E2B3E", width=350, height=500)
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
        
        # Поля ввода - исправлены координаты
        input_y = 50
        field_spacing = 55
        
        # URL (первое поле)
        tk.Label(settings_container, text="URL сайта", fg="white", bg="#1E2B3E", 
                font=("Arial", 10, "bold")).place(x=30, y=input_y)
        self.url_entry = ModernEntry(settings_container, placeholder="https://example.com", width=25)
        self.url_entry.place(x=30, y=input_y + 25)

        # EMAIL (второе поле)
        tk.Label(settings_container, text="Email", fg="white", bg="#1E2B3E", 
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing)
        self.email_entry = ModernEntry(settings_container, placeholder="user@example.com", width=25)
        self.email_entry.place(x=30, y=input_y + field_spacing + 25)

        # ПАРОЛЬ (третье поле)
        tk.Label(settings_container, text="Пароль", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*2)
        self.password_entry = ModernEntry(settings_container, placeholder="password", width=25, show="*")
        self.password_entry.place(x=30, y=input_y + field_spacing*2 + 25)

        # Кнопка показа/скрытия пароля
        self.show_password = tk.BooleanVar(value=False)
        
        self.password_toggle = tk.Checkbutton(
            settings_container,
            text="👁",
            variable=self.show_password,
            bg="#1E2B3E",
            fg="#888888",
            selectcolor="#1E2B3E",
            activebackground="#1E2B3E",
            activeforeground="#888888",
            font=("Arial", 9),
            command=self.toggle_password_visibility
        )
        self.password_toggle.place(x=310, y=input_y + field_spacing*2 + 30)
        
        # Таймаут (четвертое поле)
        tk.Label(settings_container, text="Таймаут (сек)", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*3)
        self.timeout_entry = ModernEntry(settings_container, placeholder="0.5", width=25)
        self.timeout_entry.place(x=30, y=input_y + field_spacing*3 + 25)
        
        # Повторы (пятое поле)
        tk.Label(settings_container, text="Количество повторов", fg="white", bg="#1E2B3E",
                font=("Arial", 10, "bold")).place(x=30, y=input_y + field_spacing*4)
        self.retries_entry = ModernEntry(settings_container, placeholder="3", width=25)
        self.retries_entry.place(x=30, y=input_y + field_spacing*4 + 25)
        
        # ЧЕКБОКС ДЛЯ ПЕРЕЗАГРУЗКИ СТРАНИЦЫ (шестое)
        self.is_refresh = tk.BooleanVar(value=True)  # По умолчанию включено
        
        self.refresh_checkbox = tk.Checkbutton(
            settings_container,
            text="Автоперезагрузка страницы",
            variable=self.is_refresh,
            bg="#1E2B3E",
            fg="white",
            selectcolor="#1E2B3E",
            activebackground="#1E2B3E",
            activeforeground="white",
            font=("Arial", 10),
            anchor="w",
            command=self.toggle_refresh_entry
        )
        self.refresh_checkbox.place(x=30, y=input_y + field_spacing*5)
        
        # Поле для времени перезагрузки
        tk.Label(settings_container, text="Интервал перезагрузки (сек)", 
                fg="#888888", bg="#1E2B3E",
                font=("Arial", 9)).place(x=30, y=input_y + field_spacing*5 + 25)
        
        self.time_refresh_entry = ModernEntry(settings_container, placeholder="20", width=10)
        self.time_refresh_entry.place(x=30, y=input_y + field_spacing*5 + 45)
        
        # Позиция для кнопки и чекбокса Firefox
        buttons_y = input_y + field_spacing*6 + 40
        
        # Кнопка Save and Run
        self.save_run_btn = tk.Button(
            settings_container,
            text="Сохранить и Запустить",
            command=self.on_save_run,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=1,
            relief="flat"
        )
        self.save_run_btn.place(x=25, y=buttons_y)

        # Привязываем правый клик для сохранения без запуска
        self.save_run_btn.bind("<Button-3>", lambda e: self.save_config_only())
        
        # ЧЕКБОКС ФАЕРФОКС
        self.is_browser = tk.BooleanVar(value=False)
        
        self.firefox_checkbox = tk.Checkbutton(
            settings_container,
            text="Использовать Firefox",
            variable=self.is_browser,
            bg="#1E2B3E",
            fg="white",
            selectcolor="#1E2B3E",
            activebackground="#1E2B3E",
            activeforeground="white",
            font=("Arial", 10),
            anchor="w"
        )
        self.firefox_checkbox.place(x=23, y=buttons_y + 75)
        
        # Кнопки Запуск/Стоп
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
        self.run_btn.place(x=25, y=buttons_y + 40)

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
        self.stop_btn.place(x=165, y=buttons_y + 40)

    def save_config_only(self):
        "Сохраняет конфиг без запуска процесса"
        if self.save_config():
            logging.info("✅ Конфигурация сохранена")

    def toggle_refresh_entry(self):
        "Активация/деактивация поля времени перезагрузки"
        if hasattr(self, 'time_refresh_entry'):
            if self.is_refresh.get():
                self.time_refresh_entry.entry.config(state='normal')
                self.time_refresh_entry.entry.config(fg='white')
            else:
                self.time_refresh_entry.entry.config(state='disabled')
                self.time_refresh_entry.entry.config(fg='#888888')

    def toggle_password_visibility(self):
        "Показывает или скрывает пароль"
        if hasattr(self, 'password_entry'):
            if self.show_password.get():
                self.password_entry.entry.config(show="")
                self.password_toggle.config(text="🙈")
            else:
                self.password_entry.entry.config(show="*")
                self.password_toggle.config(text="👁")
    
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
        self.console_text.place(x=20, y=50, width=360, height=450)
        
        # Поле ввода команд
        input_frame = tk.Frame(console_container, bg="#1E2B3E")
        input_frame.place(x=10, y=480, width=326, height=40)
        
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
        self.send_btn.place(x=290, y=2)
    
    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg="#1E2B3E", height=30)
        footer_frame.pack(fill="x", side="bottom", padx=20, pady=5)

        # Кнопка информации (теперь слева)
        info_btn = tk.Label(
            footer_frame,
            text="ℹ Информация",
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
        # Сохраняем конфигурацию
        self.save_config()


        # Получаем состояние чекбоксов
        is_browser = self.is_browser.get() if hasattr(self, 'is_browser') else True
        is_refresh = self.is_refresh.get() if hasattr(self, 'is_refresh') else True
        time_refresh = int(self.time_refresh_entry.get()) if self.time_refresh_entry.get().strip() and is_refresh else 20

        # Получаем email и пароль
        email = self.email_entry.get()
        password = self.password_entry.get()


        params = {
            'email': email,
            'password': password,
            'url': self.url_entry.get(),
            'timeout': float(self.timeout_entry.get()) if self.timeout_entry.get().strip() else 0.5,
            'max_retries': int(self.retries_entry.get()) if self.retries_entry.get().strip() else 3,
            'is_browser': is_browser,
            'is_refresh': is_refresh,
            'time_refresh': time_refresh
        }
        
        # Фильтруем только заполненные параметры
        filtered_params = {k: v for k, v in params.items() if v}
        
        if params['url'] and params['email'] and params['password']:
            logging.info(f"🚀 Запуск процесса для URL: {params['url']}")
            logging.info(f"📧 Email: {params['email']}")
            logging.info(f"🔐 Пароль: {'*' * len(params['password'])}")
            logging.info(f"🌐 Браузер: {'Firefox' if not is_browser else 'Chrome'}")
            logging.info(f"🔄 Автоперезагрузка: {'Включена' if is_refresh else 'Выключена'}")
            if is_refresh:
                logging.info(f"⏱️ Интервал перезагрузки: {time_refresh} сек")


            # Передаем параметры как аргументы
            self.start_process(
                email_user=params['email'],
                password_user=params['password'],
                url=params['url'],
                timeout=params['timeout'],
                max_retries=params['max_retries'],
                is_browser=params['is_browser'],
                is_refresh=params['is_refresh'],
                time_refresh=params['time_refresh']
            )
        else:
            missing = []
            if not params['url']:
                missing.append("URL")
            if not params['email']:
                missing.append("Email")
            if not params['password']:
                missing.append("Пароль")
            
            logging.warning(f"⚠️ Не заполнены поля: {', '.join(missing)}")
    
    def on_run(self):
        url = self.url_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if url and email and password:
            is_browser = self.is_browser.get() if hasattr(self, 'is_browser') else True
            is_refresh = self.is_refresh.get() if hasattr(self, 'is_refresh') else True
            time_refresh = int(self.time_refresh_entry.get()) if self.time_refresh_entry.get().strip() and is_refresh else 20
            
            # ПРАВИЛЬНОЕ ИМЯ ПЕРЕМЕННОЙ
            timeout = float(self.timeout_entry.get()) if self.timeout_entry.get().strip() else 0.5
            max_retries = int(self.retries_entry.get()) if self.retries_entry.get().strip() else 3
            
            logging.info(f"🚀 Запуск процесса для URL: {url}")
            logging.info(f"📧 Email: {email}")
            logging.info(f"🔐 Пароль: {'*' * len(password)}")
            logging.info(f"🌐 Браузер: {'Firefox' if not is_browser else 'Chrome'}")
            logging.info(f"🔄 Автоперезагрузка: {'Включена' if is_refresh else 'Выключена'}")
            if is_refresh:
                logging.info(f"⏱️ Интервал перезагрузки: {time_refresh} сек")

            self.start_process(
                email_user=email,
                password_user=password,
                url=url,
                timeout=timeout,  
                max_retries=max_retries,
                is_browser=is_browser,
                is_refresh=is_refresh,
                time_refresh=time_refresh
            )
        else:
            missing = []
            if not url:
                missing.append("URL")
            if not email:
                missing.append("Email")
            if not password:
                missing.append("Пароль")
            
            logging.warning(f"⚠️ Не заполнены поля: {', '.join(missing)}")
    
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
    
    def save_config(self):
        "Сохраняет конфигурацию в файл"
        try:
            config = {
                'url': self.url_entry.get(),
                'email': self.email_entry.get(),
                'password': self._encrypt_password(self.password_entry.get()),
                'timeout': self.timeout_entry.get(),
                'max_retries': self.retries_entry.get(),
                'is_browser': self.is_browser.get(),
                'is_refresh': self.is_refresh.get(),
                'time_refresh': self.time_refresh_entry.get(),
                'show_password': self.show_password.get()
            }
            
            # Фильтруем пустые значения
            config = {k: v for k, v in config.items() if v is not None and v != ''}
            
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logging.info("✅ Конфигурация сохранена")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка сохранения конфигурации: {e}")
            return False
    
    def load_config(self):
        "Загружает конфигурацию из файла"
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if not os.path.exists(config_path):
                logging.info("📄 Файл конфигурации не найден, используется конфигурация по умолчанию")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Устанавливаем значения в поля
            if 'url' in config:
                self.url_entry.entry.delete(0, tk.END)
                self.url_entry.entry.insert(0, config['url'])
            
            if 'email' in config:
                self.email_entry.entry.delete(0, tk.END)
                self.email_entry.entry.insert(0, config['email'])
            
            if 'password' in config:
                decrypted_password = self._decrypt_password(config['password'])
                self.password_entry.entry.delete(0, tk.END)
                self.password_entry.entry.insert(0, decrypted_password)
            
            if 'timeout' in config:
                self.timeout_entry.entry.delete(0, tk.END)
                self.timeout_entry.entry.insert(0, config['timeout'])
            
            if 'max_retries' in config:
                self.retries_entry.entry.delete(0, tk.END)
                self.retries_entry.entry.insert(0, config['max_retries'])
            
            if 'is_browser' in config:
                self.is_browser.set(config['is_browser'])
            
            if 'is_refresh' in config:
                self.is_refresh.set(config['is_refresh'])
                self.toggle_refresh_entry()  # Обновляем состояние поля перезагрузки
            
            if 'time_refresh' in config:
                self.time_refresh_entry.entry.delete(0, tk.END)
                self.time_refresh_entry.entry.insert(0, config['time_refresh'])
            
            if 'show_password' in config:
                self.show_password.set(config['show_password'])
                self.toggle_password_visibility()  # Обновляем видимость пароля
            
            logging.info("✅ Конфигурация загружена")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки конфигурации: {e}")
            return False
    
    def _encrypt_password(self, password):
        "Шифрует пароль"
        if not password:
            return ""
        try:
            cipher = Fernet(self.encryption_key)
            encrypted_password = cipher.encrypt(password.encode())
            return encrypted_password.decode('utf-8')
        except Exception:
            # Если шифрование не удалось, возвращаем как есть (не безопасно)
            return password
    
    def _decrypt_password(self, encrypted_password):
        "Расшифровывает пароль"
        if not encrypted_password:
            return ""
        try:
            cipher = Fernet(self.encryption_key)
            decrypted_password = cipher.decrypt(encrypted_password.encode())
            return decrypted_password.decode('utf-8')
        except Exception:
            # Если расшифровка не удалась, возвращаем как есть
            return encrypted_password

    def start_process(self, email_user, password_user, url, timeout=0.5, max_retries=3,
                      is_browser=False,
                      is_refresh=True,
                      time_refresh=20):
        """Запускает основной процесс в отдельном потоке"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.core:
                    loop.run_until_complete(
                        self.core.run_main_process(
                            email_user=email_user,
                            password_user=password_user,
                            url=url, 
                            timeout=timeout, 
                            max_retries=max_retries,
                            is_browser=is_browser,  # <-- Передаем состояние чекбокса
                            is_refresh=is_refresh,  # <-- Передаем состояние чекбокса
                            time_refresh=time_refresh,  # <-- Передаем время перезагру
                        )
                    )
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