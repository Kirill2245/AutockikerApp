import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import logging
from tkinter import font
from tkinter import scrolledtext
from emitter import global_emitter

class RoundedFrame(tk.Canvas):
    def __init__(self, master, radius=20, color="#696969", **kwargs):
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
            # Создаем точки для закругленного прямоугольника
            points = [
                self.radius, 0,
                width - self.radius, 0,
                width, 0,
                width, self.radius,
                width, height - self.radius,
                width, height,
                width - self.radius, height,
                self.radius, height,
                0, height,
                0, height - self.radius,
                0, self.radius,
                0, 0
            ]
            
            self.create_polygon(points, fill=self.color, outline="", smooth=True)


class LogTextHandler:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # Настраиваем теги для цветов
        self.text_widget.tag_config("ERROR", foreground="#FF0000")
        self.text_widget.tag_config("WARNING", foreground="#FF9100")
        self.text_widget.tag_config("INFO", foreground="#188D28")
        self.text_widget.tag_config("DEBUG", foreground="#159BE9")
        self.text_widget.tag_config("CRITICAL", foreground="#FF0000")
        
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
    
    def __init__(self, root, core_instance = None):
        self.root = root
        self.core = core_instance
        self.setup_ui()
        self.setup_logging()
    def setup_logging(self):
        # Подключаем обработчик логов к консольному текстовому полю
        self.log_handler = LogTextHandler(self.console_text)
    
    def setup_ui(self):
        self.root.title("KLIK KLAK")
        self.root.geometry("700x500")
        self.root.configure(bg = "#193750")
        custom_font = font.Font(family = "Arial", size = 14, weight = "bold")

        self.root.entry1 = tk.Entry(self.root, width = 30) #ENTRY URL
        self.root.entry1.place(x = 100, y = 50)
        self.root.label1 = tk.Label(self.root, text = "URL", fg = "White", bg = "#193750", font = custom_font) #LABEL URL
        self.root.label1.place(x = 50,y = 45)
        self.root.style = ttk.Style()
        
        settings_frame = RoundedFrame(self.root, radius=30, color="#696969", width=250, height=300) 
        settings_frame.place(x=50, y=90)
        self.root.label2 = tk.Label(self.root, text = "Setting", fg = "White", bg = "#696969", font = custom_font) #LABEL Settings
        self.root.label2.place(x = 130,y = 90)
        
        self.root.entry2 = tk.Entry(self.root, width = 20) #ENTRY Timeout
        self.root.entry2.place(x = 150, y = 140)
        self.root.label3 = tk.Label(self.root, text = "Timeout", fg = "White", bg = "#696969", font = custom_font) #LABEL Timeout
        self.root.label3.place(x = 60,y = 135)

        self.root.entry3 = tk.Entry(self.root, width = 20) #ENTRY Retries
        self.root.entry3.place(x = 150, y = 175)
        self.root.label4 = tk.Label(self.root, text = "Retries", fg = "White", bg = "#696969", font = custom_font) #LABEL Retries
        self.root.label4.place(x = 73,y = 170)

        self.root.entry3 = tk.Entry(self.root, width = 20) #ENTRY first click
        self.root.entry3.place(x = 150, y = 210)
        self.root.label4 = tk.Label(self.root, text = "First click", fg = "White", bg = "#696969", font = custom_font) #LABEL first click
        self.root.label4.place(x = 50,y = 205)

        self.root.entry3 = tk.Entry(self.root, width = 20) #ENTRY last click
        self.root.entry3.place(x = 150, y = 245)
        self.root.label4 = tk.Label(self.root, text = "Last click", fg = "White", bg = "#696969", font = custom_font) #LABEL last click
        self.root.label4.place(x = 50,y = 240)

        self.root.entry3 = tk.Entry(self.root, width = 17) #ENTRY class modal
        self.root.entry3.place(x = 170, y = 280)
        self.root.label4 = tk.Label(self.root, text = "Class modal", fg = "White", bg = "#696969", font = custom_font) #LABEL class modal
        self.root.label4.place(x = 50,y = 275)

        self.root.button1 = tk.Button(self.root, height = 2, width = 30, text = "Save and Run", bg = "#696969") #button Save and Run
        self.root.button1.place(x = 65, y = 320) 
        self.root.button2 = tk.Button(self.root, height = 2, width = 12, text = "RUN", bg = "#388662", command = self.on_run) #button Run
        self.root.button2.place(x = 60, y = 420) 
        self.root.button3 = tk.Button(self.root, height = 2, width = 12, text = "STOP", bg = "#693636", command=self.on_stop) #button Save
        self.root.button3.place(x = 200, y = 420)
    

        console_frame = RoundedFrame(self.root, radius=15, color="#696969", width=295, height=480)
        console_frame.place(x=400, y=10)
        self.root.label1 = tk.Label(self.root, text = "CONSOLE", fg = "White", bg = "#696969", font = custom_font) #LABEL CONSOLE
        self.root.label1.place(x = 490,y = 20)
        
        # Текстовое поле консоли с прокруткой
        self.console_text = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD,
            width=37,
            height=25,
            bg="#1E1E1E",  # Темный фон как у настоящей консоли
            fg="#00FF00",  # Зеленый текст
            font=("Consolas", 10),
            insertbackground="white",  # Цвет курсора
            selectbackground="#555555"  
        )
        self.console_text.place(x=410, y=50)
        
        # Добавляем возможность ввода команд
        self.console_input = tk.Entry(
            self.root,
            width=30,
            bg="#2D2D2D",
            fg="white",
            font=("Consolas", 10),
            insertbackground="white"
        )
        self.console_input.place(x=410, y=450)
        self.console_input.bind("<Return>", self.process_console_command)
        
        # Кнопка отправки команды
        self.console_button = tk.Button(
            self.root,
            text="Send",
            width=5,
            bg="#388662",
            fg="white",
            command=self.process_console_command
        )
        self.console_button.place(x=630, y=448)
        
        # Добавляем начальное сообщение в консоль
        self.write_to_console("Консоль инициализирована...\n")
        self.write_to_console("Введите 'help' для списка команд\n")
        self.write_to_console("-" * 30 + "\n")

        # Тестовые логи для демонстрации
        logging.info("Приложение запущено")
        logging.warning("Это тестовое предупреждение")
        logging.error("Это тестовая ошибка")
    
    def write_to_console(self, message, level=logging.INFO): 
        """Добавляет текст в консоль с указанным уровнем"""                          
        self.console_text.configure(state='normal')
        
        # Определяем тег в зависимости от уровня
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
        self.console_text.see(tk.END)  # Автопрокрутка к концу
    
    def process_console_command(self, event=None): 
        """Обрабатывает команды из консоли"""
        command = self.console_input.get().strip()
        if command:
            self.write_to_console(f"> {command}\n")
            
            # Обработка команд
            if command.lower() == "help":
                self.show_help()
            elif command.lower() == "clear":
                self.clear_console()
            elif command.lower() == "test":
                self.write_to_console("Тестовое сообщение из консоли\n")
                logging.info("Тестовая команда выполнена")
            elif command.lower() == "log_test":
                # Генерируем тестовые логи разных уровней
                logging.debug("Тестовое отладочное сообщение")
                logging.info("Тестовое информационное сообщение")
                logging.warning("Тестовое предупреждение")
                logging.error("Тестовая ошибка")
            else:
                self.write_to_console(f"Неизвестная команда: {command}\n")
            
            # Очищаем поле ввода
            self.console_input.delete(0, tk.END)
    
    def show_help(self):
        """Список доступных команд"""  
        help_text = """
    Доступные команды:
    - help: показать эту справку
    - clear: очистить консоль
    - test: тестовая команда
    - log_test: тест логирования разных уровней
    """
        self.write_to_console(help_text)
    
    def clear_console(self):  
        """Очистка консоли"""        
        self.console_text.configure(state='normal')
        self.console_text.delete(1.0, tk.END)
        self.console_text.configure(state='disabled')
        self.write_to_console("Консоль очищена\n")
    
    def on_save_run(self):
        """Обработчик кнопки Save and Run"""
        url = self.root.entry1.get()
        if url:
            logging.info(f"Запуск процесса для URL: {url}")
            self.start_process(url)
        else:
            logging.warning("URL не указан")
    
    def on_run(self):
        url = self.root.entry1.get()
        if url:
            logging.info(f"Запуск процесса для URL: {url}")
            self.start_process(url)
        else:
            logging.warning("URL не указан")
    
    def on_stop(self):
        """Обработчик кнопки Stop"""
        logging.info("Остановка процесса")
        self.stop_process()
        # Здесь должна быть логика остановки
        
    def stop_process(self):
        def stop_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.core:
                    loop.run_until_complete(self.core.stop_main_process())
                logging.info("Процесс остановлен")
            except Exception as e:
                logging.error(f"Ошибка при остановке: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=stop_async)
        thread.daemon = True
        thread.start()
    
    def start_process(self, url, timeout, max_retries, classOneClick, classTwoClick, classModal):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.core:
                    loop.run_until_complete(self.core.run_main_process(url))
                else:
                    # Демо-режим без core
                    logging.info(f"Запущен демо-процесс для {url}")
                    loop.run_until_complete(self.demo_process(url))
            except Exception as e:
                logging.error(f"Ошибка в процессе: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()

        
        



