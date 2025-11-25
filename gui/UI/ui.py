import tkinter as tk
from tkinter import ttk
import logging
from emitter import global_emitter
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