import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import logging
from tkinter import font
from tkinter import scrolledtext
from emitter import global_emitter
from service.auth_manager import auth_manager
from tkinter import scrolledtext, messagebox, Toplevel, filedialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import config as cfg

class ModernButton(tk.Canvas):
    def __init__(self, master, text, command, width=120, height=40, 
                 bg_color="#388662", hover_color="#2a6450", text_color="white", 
                 radius=10, font_size=12, **kwargs):
        super().__init__(master, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font_size = font_size
        self.text = text
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
        self._draw_button(bg_color)
    
    def _draw_button(self, color):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Рисуем закругленный прямоугольник
        self.create_round_rect(0, 0, width, height, self.radius, fill=color, outline="")
        
        # Добавляем текст
        self.create_text(width/2, height/2, text=self.text, 
                        fill=self.text_color, 
                        font=("Arial", self.font_size, "bold"))
    
    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self._draw_button(self.hover_color)
    
    def _on_leave(self, event):
        self._draw_button(self.bg_color)
    
    def _on_click(self, event):
        self.command()

class RoundedFrame(tk.Canvas):
    def __init__(self, master, radius=20, color="#2D4A5D", **kwargs):
        super().__init__(master, highlightthickness=0, bg=master.cget("bg"), **kwargs)
        self.radius = radius
        self.color = color
        self.bind("<Configure>", self._draw_rounded_rect)
    
    def _draw_rounded_rect(self, event=None):
        """Рисует закругленный прямоугольник"""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width > 0 and height > 0:
            self.create_round_rect(0, 0, width, height, self.radius, fill=self.color, outline="")
    
    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

class ModernEntry(tk.Frame):
    def __init__(self, master, placeholder="", width=30, **kwargs):
        super().__init__(master, bg=master.cget("bg"))
        self.placeholder = placeholder
        self.placeholder_color = "#888888"
        self.text_color = "white"
        
        self.entry = tk.Entry(
            self, 
            width=width,
            bg="#3A556F",
            fg=self.placeholder_color,
            insertbackground="white",
            relief="flat",
            font=("Arial", 10)
        )
        self.entry.pack(fill="both", padx=10, pady=8)
        
        # Добавляем привязки для вставки
        self.entry.bind("<Control-v>", self._handle_paste)
        self.entry.bind("<Button-3>", self._show_context_menu)  # ПКМ
        
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.bind("<FocusIn>", self._on_focus_in)
            self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Создаем рамку
        self.canvas = tk.Canvas(self, height=2, bg="#4A657F", highlightthickness=0)
        self.canvas.pack(fill="x", padx=10)
        self.canvas.create_line(0, 1, width*10, 1, fill="#5D7A95", width=2)
        
        # Создаем контекстное меню
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Создает контекстное меню для поля ввода"""
        self.context_menu = tk.Menu(self.entry, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self._cut)
        self.context_menu.add_command(label="Копировать", command=self._copy)
        self.context_menu.add_command(label="Вставить", command=self._paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self._select_all)
    
    def _show_context_menu(self, event):
        """Показывает контекстное меню"""
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def _handle_paste(self, event=None):
        """Обрабатывает вставку через Ctrl+V"""
        self._paste()
        return "break"  # Предотвращаем стандартное поведение
    
    def _cut(self):
        """Вырезание текста"""
        self.entry.event_generate("<<Cut>>")
    
    def _copy(self):
        """Копирование текста"""
        self.entry.event_generate("<<Copy>>")
    
    def _paste(self):
        """Вставка текста"""
        try:
            # Очищаем плейсхолдер при вставке
            if self.entry.get() == self.placeholder:
                self.entry.delete(0, tk.END)
                self.entry.config(fg=self.text_color)
            
            self.entry.event_generate("<<Paste>>")
        except Exception:
            pass
    
    def _select_all(self):
        """Выделение всего текста"""
        self.entry.select_range(0, tk.END)
        self.entry.icursor(tk.END)
    
    def _on_focus_in(self, event):
        """При фокусе убираем плейсхолдер"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.text_color)
    
    def _on_focus_out(self, event):
        """При потере фокуса возвращаем плейсхолдер если поле пустое"""
        if not self.entry.get().strip():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
    
    def get(self):
        value = self.entry.get()
        return value if value != self.placeholder else ""

class LogTextHandler:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # Настраиваем теги для цветов
        self.text_widget.tag_config("ERROR", foreground="#FF6B6B")
        self.text_widget.tag_config("WARNING", foreground="#FFA726")
        self.text_widget.tag_config("INFO", foreground="#4FC3F7")
        self.text_widget.tag_config("DEBUG", foreground="#BA68C8")
        self.text_widget.tag_config("CRITICAL", foreground="#FF5252")
        self.text_widget.tag_config("SUCCESS", foreground="#66BB6A")
        
        # Регистрируем себя в emitter
        global_emitter.register_callback(self.handle_log)
    
    def _is_chrome_stacktrace(self, message):
        if not message:
            return False
            
        stacktrace_indicators = [
            'Stacktrace:',
            'GetHandleVerifier',
            '(No symbol)',
            'BaseThreadInitThunk',
            'RtlGetAppContainerNamedObjectPath',
            'from invalid argument:',
            'unrecognized chrome option:'
        ]
        
        message_str = str(message).lower()
        return any(indicator.lower() in message_str for indicator in stacktrace_indicators)
    
    def handle_log(self, message, level=logging.INFO):
        if self._is_chrome_stacktrace(message):
            return 
        
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
            
        # Добавляем запись в текстовое поле
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, f"{message}\n", tag)
        self.text_widget.configure(state='disabled')
        # Автопрокрутка к концу
        self.text_widget.see(tk.END)

class AppGUI:
    def __init__(self, root, core_instance=None):
        self.root = root
        self.core = core_instance
        self.setup_ui()
        self.setup_logging()
    
    def setup_logging(self):
        # Подключаем обработчик логов к консольному текстовому полю
        self.log_handler = LogTextHandler(self.console_text)
    
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
        self.create_header()
        
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
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#1E2B3E", height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        # Логотип и название
        logo_label = tk.Label(
            header_frame,
            text="⚡ KLIK KLAK",
            font=("Arial", 20, "bold"),
            fg="#4FC3F7",
            bg="#1E2B3E"
        )
        logo_label.pack(side="left", padx=20, pady=20)
        
        # Статус приложения
        status_label = tk.Label(
            header_frame,
            text="✅ Система активна",
            font=("Arial", 10),
            fg="#66BB6A",
            bg="#1E2B3E"
        )
        status_label.pack(side="right", padx=20, pady=20)
    
    def create_main_content(self):
        main_frame = tk.Frame(self.root, bg="#152238")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая панель - настройки
        self.create_settings_panel(main_frame)
        
        # Правая панель - консоль
        self.create_console_panel(main_frame)
    
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
        
        # Текстовое поле консоли
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
        feedback_btn.bind("<Button-1>", lambda e: self.open_feedback_window())
    
    def open_feedback_window(self):
        """Открывает окно для отправки отзыва с возможностью прикрепления файлов"""
        logging.info("📧 Открытие формы обратной связи")
        
        # Создаем окно для обратной связи
        self.feedback_window = Toplevel(self.root)
        self.feedback_window.title("Обратная связь")
        self.feedback_window.geometry("600x550")
        self.feedback_window.configure(bg="#1E2B3E")
        self.feedback_window.resizable(False, False)
        
        # Центрируем окно
        self.feedback_window.transient(self.root)
        self.feedback_window.grab_set()
        
        # Список прикрепленных файлов
        self.attached_files = []
        
        # Заголовок
        title_label = tk.Label(
            self.feedback_window,
            text="📧 Обратная связь",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        title_label.pack(pady=15)
        
        # Тема письма
        subject_frame = tk.Frame(self.feedback_window, bg="#1E2B3E")
        subject_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            subject_frame,
            text="Тема:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w")
        
        self.subject_entry = tk.Entry(
            subject_frame,
            width=50,
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Arial", 10)
        )
        self.subject_entry.pack(fill="x", pady=5)
        self.subject_entry.insert(0, "Сообщение об ошибке в KLIK KLAK")
        
        # Текст письма
        message_frame = tk.Frame(self.feedback_window, bg="#1E2B3E")
        message_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(
            message_frame,
            text="Сообщение:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w")
        
        self.text_area = scrolledtext.ScrolledText(
            message_frame,
            wrap=tk.WORD,
            width=50,
            height=10,
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            font=("Arial", 10),
            relief="flat"
        )
        self.text_area.pack(fill="both", expand=True, pady=5)
        
        # Подсказка в текстовом поле
        self.text_area.insert("1.0", "Опишите подробно проблему, с которой столкнулись:")
        
        # Фрейм для прикрепленных файлов
        attachment_frame = tk.Frame(self.feedback_window, bg="#1E2B3E")
        attachment_frame.pack(fill="x", padx=20, pady=10)
        
        # Кнопка прикрепления файлов
        attach_button = tk.Button(
            attachment_frame,
            text="📎 Прикрепить файлы",
            command=self.attach_files,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            relief="flat"
        )
        attach_button.pack(side="left")
        
        # Список прикрепленных файлов
        self.attachment_list = tk.Listbox(
            attachment_frame, 
            height=3, 
            width=40,
            bg="#2D4A5D",
            fg="white",
            selectbackground="#3A556F"
        )
        self.attachment_list.pack(side="left", padx=10, fill="x", expand=True)
        
        # Кнопка удаления выбранного файла
        remove_button = tk.Button(
            attachment_frame,
            text="❌ Удалить",
            command=self.remove_attachment,
            bg="#D32F2F",
            fg="white",
            font=("Arial", 8),
            relief="flat"
        )
        remove_button.pack(side="right")
        
        # Кнопки
        button_frame = tk.Frame(self.feedback_window, bg="#1E2B3E")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        send_button = tk.Button(
            button_frame,
            text="📤 Отправить",
            command=self.send_feedback_email,
            bg="#388662",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=1,
            relief="flat"
        )
        send_button.pack(side="right", padx=5)
        
        cancel_button = tk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.feedback_window.destroy,
            bg="#D32F2F",
            fg="white",
            font=("Arial", 11),
            width=10,
            height=1,
            relief="flat"
        )
        cancel_button.pack(side="right", padx=5)
    
    def attach_files(self):
        """Прикрепление файлов к письму"""
        filetypes = [
            ("Все файлы", "*.*"),
            ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("Скриншоты", "*.png *.jpg *.jpeg"),
            ("Документы", "*.pdf *.doc *.docx *.txt"),
            ("Архивы", "*.zip *.rar *.7z")
        ]
        
        files = filedialog.askopenfilenames(
            title="Выберите файлы для прикрепления",
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                if file_path not in self.attached_files:
                    self.attached_files.append(file_path)
                    # Показываем только имя файла в списке
                    file_name = os.path.basename(file_path)
                    self.attachment_list.insert(tk.END, file_name)
            
            messagebox.showinfo("Успех", f"Прикреплено {len(files)} файл(ов)")
    
    def remove_attachment(self):
        """Удаление выбранного файла из списка прикрепленных"""
        selected = self.attachment_list.curselection()
        if selected:
            index = selected[0]
            self.attached_files.pop(index)
            self.attachment_list.delete(index)
    
    def send_feedback_email(self):
        """Отправляет письмо с обратной связью и прикрепленными файлами"""
        subject = self.subject_entry.get().strip()
        body = self.text_area.get("1.0", tk.END).strip()
        
        if not subject:
            messagebox.showerror("Ошибка", "Введите тему письма!")
            return
        
        if not body or body == "Опишите подробно проблему, с которой столкнулись:":
            messagebox.showerror("Ошибка", "Введите текст сообщения!")
            return
        
        try:
            # Показываем индикатор отправки
            sending_label = tk.Label(
                self.feedback_window,
                text="⏳ Отправка...",
                fg="#FFA726",
                bg="#1E2B3E",
                font=("Arial", 10)
            )
            sending_label.pack(pady=5)
            self.feedback_window.update()
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = cfg.LOGIN
            msg['To'] = "rzovliev@gmail.com"
            
            # Форматируем тело письма
            formatted_body = f"""
Сообщение от пользователя KLIK KLAK:

{body}

---
Отправлено из приложения KLIK KLAK
"""
            
            msg.attach(MIMEText(formatted_body, 'plain', 'utf-8'))
            
            # Прикрепляем файлы
            for file_path in self.attached_files:
                try:
                    with open(file_path, "rb") as file:
                        # Создаем MIME часть для файла
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        
                    # Кодируем файл в base64
                    encoders.encode_base64(part)
                    
                    # Добавляем заголовки
                    file_name = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{file_name}"'
                    )
                    
                    # Добавляем файл к сообщению
                    msg.attach(part)
                    
                except Exception as file_error:
                    messagebox.showerror("Ошибка", f"Не удалось прикрепить файл {file_path}: {file_error}")
                    sending_label.destroy()
                    return
            
            # Отправка через Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.send_message(msg)
            server.quit()
            
            # Убираем индикатор и показываем успех
            sending_label.destroy()
            
            # Показываем результат
            if self.attached_files:
                files_info = f" с {len(self.attached_files)} прикрепленными файлом(ами)"
            else:
                files_info = ""
                
            messagebox.showinfo("Успех", f"✅ Ваше сообщение отправлено{files_info}!")
            logging.info(f"📧 Письмо с обратной связью успешно отправлено{files_info}")
            
            # Закрываем окно
            self.feedback_window.destroy()
            
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Ошибка", "❌ Ошибка авторизации. Проверьте настройки почты.")
            logging.error("❌ Ошибка авторизации при отправке письма")
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Не удалось отправить письмо: {e}")
            logging.error(f"❌ Ошибка отправки письма: {e}")

    def write_to_console(self, message, level=logging.INFO):
        """Добавляет текст в консоль с указанным уровнем"""
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

    # ДОБАВЬТЕ ЭТИ МЕТОДЫ ПОСЛЕ stop_process:

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

    async def demo_process(self, url):
        """Демо-процесс для тестирования без core"""
        logging.info(f"🔧 Демо-процесс запущен для: {url}")
        for i in range(5):
            await asyncio.sleep(1)
            logging.info(f"🔧 Демо-процесс выполняется... шаг {i+1}/5")
        logging.info("✅ Демо-процесс завершен")
