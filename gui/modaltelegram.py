import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
import logging

class ModalTelegram:
    def __init__(self, parent):
        self.parent = parent
        self.telegram_window = None  
        
    def open_windowtelegram(self):  
        # Создаем окно для информации
        self.telegram_window = Toplevel(self.parent)
        self.telegram_window.title("Настройки Telegram")
        self.telegram_window.geometry("450x550")
        self.telegram_window.configure(bg="#1E2B3E")
        self.telegram_window.resizable(False, False)
        
        # Центрируем окно
        self.telegram_window.transient(self.parent)
        self.telegram_window.grab_set()
        
        self._create_widgets()

    def _create_widgets(self):
        """Создает виджеты окна настроек Telegram"""
        # Заголовок
        title_label = tk.Label(
            self.telegram_window,
            text="Настройки Telegram API",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        title_label.pack(pady=15)

        # Фрейм для API ID
        api_id_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        api_id_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        tk.Label(
            api_id_frame,
            text="API ID:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w", pady=(0, 5))
        
        self.api_id_entry = tk.Entry(
            api_id_frame,
            font=("Arial", 11),
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            relief="flat",
            width=40
        )
        self.api_id_entry.pack(fill="x", pady=(0, 5))
        
        # Информация о том, где получить API ID
        api_id_info = tk.Label(
            api_id_frame,
            text="Получить можно на my.telegram.org",
            font=("Arial", 9, "italic"),
            fg="#4FC3F7",
            bg="#1E2B3E"
        )
        api_id_info.pack(anchor="w")

        # Фрейм для API Hash
        api_hash_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        api_hash_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        tk.Label(
            api_hash_frame,
            text="API Hash:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w", pady=(0, 5))
        
        self.api_hash_entry = tk.Entry(
            api_hash_frame,
            font=("Arial", 11),
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            relief="flat",
            width=40,
            show="*"  # Скрываем ввод для безопасности
        )
        self.api_hash_entry.pack(fill="x", pady=(0, 5))
        
        # Checkbox для показа/скрытия API Hash
        self.show_hash_var = tk.BooleanVar(value=False)
        show_hash_check = tk.Checkbutton(
            api_hash_frame,
            text="Показать API Hash",
            variable=self.show_hash_var,
            command=self._toggle_api_hash_visibility,
            font=("Arial", 9),
            fg="white",
            bg="#1E2B3E",
            selectcolor="#1E2B3E",
            activebackground="#1E2B3E",
            activeforeground="white"
        )
        show_hash_check.pack(anchor="w", pady=(5, 0))

        # Фрейм для номера телефона (опционально)
        phone_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        phone_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        tk.Label(
            phone_frame,
            text="Номер телефона (с кодом страны):",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w", pady=(0, 5))
        
        self.phone_entry = tk.Entry(
            phone_frame,
            font=("Arial", 11),
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            relief="flat",
            width=40
        )
        self.phone_entry.pack(fill="x", pady=(0, 5))
        
        # Добавляем плейсхолдер вручную
        self.phone_entry.insert(0, "+79991234567")
        self.phone_entry.config(fg="gray")
        self.phone_entry.bind("<FocusIn>", self._on_phone_focus_in)
        self.phone_entry.bind("<FocusOut>", self._on_phone_focus_out)

        # Разделитель
        separator = tk.Frame(self.telegram_window, height=2, bg="#2D4A5D")
        separator.pack(fill="x", padx=20, pady=10)

        # ВАЖНО: добавляем self. чтобы сделать атрибутом класса
        self.text_area = scrolledtext.ScrolledText(
            wrap=tk.WORD,
            width=50,
            height=8,
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            font=("Arial", 10),
            relief="flat"
        )
        self.text_area.pack(fill="both", expand=True, pady=(0, 5))

        # Фрейм для кнопок
        button_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Кнопка отправки
        send_btn = tk.Button(
            button_frame,
            text="Подключиться и отправить",
            font=("Arial", 11, "bold"),
            bg="#4FC3F7",
            fg="white",
            activebackground="#2DB5F5",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._send_to_telegram
        )
        send_btn.pack(side="right", padx=(10, 0))
        
        # Кнопка отмены
        cancel_btn = tk.Button(
            button_frame,
            text="Отмена",
            font=("Arial", 11),
            bg="#2D4A5D",
            fg="white",
            activebackground="#3D5B6D",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.telegram_window.destroy
        )
        cancel_btn.pack(side="right")

    def _toggle_api_hash_visibility(self):
        """Переключает видимость API Hash"""
        if self.show_hash_var.get():
            self.api_hash_entry.config(show="")
        else:
            self.api_hash_entry.config(show="*")

    def _on_phone_focus_in(self, event):
        """Обработчик фокуса на поле номера телефона"""
        if self.phone_entry.get() == "+79991234567":
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.config(fg="white")

    def _on_phone_focus_out(self, event):
        """Обработчик потери фокуса полем номера телефона"""
        if not self.phone_entry.get():
            self.phone_entry.insert(0, "+79991234567")
            self.phone_entry.config(fg="gray")

    def _send_to_telegram(self):
        """Обработчик отправки в Telegram"""
        # Получаем данные из полей ввода
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        # Теперь self.text_area доступен как атрибут класса
        message = self.text_area.get("1.0", tk.END).strip()
        
        # Валидация
        if not api_id:
            messagebox.showerror("Ошибка", "Введите API ID")
            return
            
        if not api_hash:
            messagebox.showerror("Ошибка", "Введите API Hash")
            return
            
        if not api_id.isdigit():
            messagebox.showerror("Ошибка", "API ID должен состоять только из цифр")
            return
            
            
        if phone == "+79991234567":  # Если остался плейсхолдер
            phone = ""
        
        try:
            # Здесь будет логика подключения к Telegram API
            # Например:
            # from telethon import TelegramClient
            # client = TelegramClient('session', int(api_id), api_hash)
            # await client.start(phone=phone if phone else None)
            
            
            messagebox.showinfo("Успех", 
                f"Данные получены:\n"
                f"API ID: {api_id}\n"
                f"API Hash: {'*' * len(api_hash)}\n"
                f"Телефон: {phone if phone else 'не указан'}\n"
            )
                
            # Закрываем окно
            self.telegram_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить: {str(e)}")

    def get_credentials(self):
        """Возвращает введенные учетные данные"""
        if hasattr(self, 'api_id_entry') and hasattr(self, 'api_hash_entry'):
            phone = self.phone_entry.get()
            if phone == "+79991234567":  # Если плейсхолдер
                phone = ""
                
            return {
                'api_id': self.api_id_entry.get(),
                'api_hash': self.api_hash_entry.get(),
                'phone': phone
            }
        return None
    
    def _send_to_telegram(self):
        """Обработчик отправки в Telegram"""
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        phone = self.phone_entry.get().strip()
        message = self.text_area.get("1.0", tk.END).strip()
        
        # Валидация
        if not api_id:
            messagebox.showerror("Ошибка", "Введите API ID")
            return
            
        if not api_hash:
            messagebox.showerror("Ошибка", "Введите API Hash")
            return
            
        if not api_id.isdigit():
            messagebox.showerror("Ошибка", "API ID должен состоять только из цифр")
            return
            
        if not message:
            messagebox.showerror("Ошибка", "Введите сообщение для отправки")
            return
            
        if phone == "+79991234567":  # Если остался плейсхолдер
            phone = ""
        
        try:
            # Закрываем окно
            self.telegram_window.destroy()
            
            # Вызываем callback в основном приложении если он есть
            if hasattr(self.parent, 'on_telegram_credentials_saved'):
                self.parent.on_telegram_credentials_saved({
                    'api_id': api_id,
                    'api_hash': api_hash,
                    'phone': phone,
                    'message': message
                })
            else:
                # Или просто показываем сообщение
                messagebox.showinfo("Успех", 
                    f"Данные получены:\n"
                    f"API ID: {api_id}\n"
                    f"Телефон: {phone if phone else 'не указан'}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")