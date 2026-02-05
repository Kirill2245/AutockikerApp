# gui/modaltelegram.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, simpledialog
import logging
import threading
import asyncio

class ModalTelegram:
    def __init__(self, parent):
        self.parent = parent
        self.telegram_window = None  
        self.telegram_service = None
        
    def set_telegram_service(self, service):
        """Устанавливает сервис Telegram"""
        self.telegram_service = service
        
    def open_windowtelegram(self):  
        # Создаем окно для настроек
        self.telegram_window = Toplevel(self.parent)
        self.telegram_window.title("Настройки Telegram")
        self.telegram_window.geometry("500x800")
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
            text="📱 Настройки Telegram API",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        title_label.pack(pady=15)

        # Инструкция
        instruction = tk.Label(
            self.telegram_window,
            text="Для получения API ID и API Hash посетите:\nhttps://my.telegram.org",
            font=("Arial", 10, "italic"),
            fg="#4FC3F7",
            bg="#1E2B3E",
            justify="center"
        )
        instruction.pack(pady=(0, 20))

        # Фрейм для API ID
        api_id_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        api_id_frame.pack(fill="x", padx=30, pady=(10, 5))
        
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
            width=35
        )
        self.api_id_entry.pack(fill="x", pady=(0, 5))

        # Фрейм для API Hash
        api_hash_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        api_hash_frame.pack(fill="x", padx=30, pady=(5, 10))
        
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
            width=35,
            show="*"
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

        # Фрейм для номера телефона
        phone_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        phone_frame.pack(fill="x", padx=30, pady=(5, 10))
        
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
            width=35
        )
        self.phone_entry.pack(fill="x", pady=(0, 5))
        self.phone_entry.insert(0, "+79991234567")
        
        # Разделитель
        separator = tk.Frame(self.telegram_window, height=2, bg="#2D4A5D")
        separator.pack(fill="x", padx=30, pady=15)

        # Фрейм для сообщения
        message_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        message_frame.pack(fill="both", expand=True, padx=30, pady=(5, 10))
        
        tk.Label(
            message_frame,
            text="Тестовое сообщение:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1E2B3E"
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(
            message_frame,
            wrap=tk.WORD,
            width=45,
            height=8,
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            font=("Arial", 10),
            relief="flat"
        )
        self.text_area.pack(fill="both", expand=True, pady=(0, 5))
        self.text_area.insert("1.0", "Привет от KLIK KLAK! 🚀")

        # Фрейм для кнопок
        button_frame = tk.Frame(self.telegram_window, bg="#1E2B3E")
        button_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        # Кнопка отправки
        send_btn = tk.Button(
            button_frame,
            text="📤 Отправить тестовое сообщение",
            font=("Arial", 11, "bold"),
            bg="#4FC3F7",
            fg="white",
            activebackground="#2DB5F5",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._send_test_message
        )
        send_btn.pack(fill="x", pady=(0, 10))
        
        # Кнопка отмены
        cancel_btn = tk.Button(
            button_frame,
            text="Закрыть",
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

    def _send_test_message(self):
        """Отправляет тестовое сообщение в Telegram"""
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
            
        if phone == "+79991234567":
            messagebox.showerror("Ошибка", "Введите свой номер телефона")
            return
        
        try:
            # Преобразуем API ID в число
            api_id_int = int(api_id)
            
            # Запускаем процесс в отдельном потоке
            threading.Thread(
                target=self._send_message_thread,
                args=(api_id_int, api_hash, phone, message),
                daemon=True
            ).start()
            
        except ValueError:
            messagebox.showerror("Ошибка", "API ID должен быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
    
    def _send_message_thread(self, api_id: int, api_hash: str, phone: str, message: str):
        """Отправляет сообщение в отдельном потоке"""
        async def send():
            try:
                from telethon import TelegramClient
                
                # Создаем клиента
                client = TelegramClient('session', api_id, api_hash)
                await client.connect()
                
                # Проверяем авторизацию
                if not await client.is_user_authorized():
                    # Запрашиваем код
                    await client.send_code_request(phone)
                    
                    # Запрашиваем код у пользователя в основном потоке
                    code = await self._get_code_from_user()
                    
                    if not code:
                        self._show_message("Отменено", "Ввод кода отменен")
                        return
                    
                    # Пытаемся войти с кодом
                    try:
                        await client.sign_in(phone, code)
                    except Exception as e:
                        self._show_message("Ошибка", f"Неверный код: {str(e)}")
                        return
                
                # Отправляем сообщение
                await client.send_message('me', message)
                await client.disconnect()
                
                self._show_message("Успех", "✅ Сообщение отправлено в Избранное!")
                
            except Exception as e:
                self._show_message("Ошибка", f"❌ Ошибка: {str(e)}")
        
        # Запускаем асинхронную функцию
        asyncio.run(send())
    
    def _show_message(self, title: str, message: str):
        """Показывает сообщение в основном потоке"""
        self.parent.after(0, lambda: messagebox.showinfo(title, message))
    
    async def _get_code_from_user(self):
        """Запрашивает код у пользователя"""
        import asyncio
        future = asyncio.Future()
        
        def ask_code():
            code = simpledialog.askstring(
                "Код подтверждения",
                f"Введите 5-значный код из Telegram,\nотправленный на номер {self.phone_entry.get().strip()}",
                parent=self.telegram_window
            )
            future.set_result(code)
        
        self.parent.after(0, ask_code)
        return await future