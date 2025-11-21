import tkinter as tk
from tkinter import font
from tkinter import messagebox
from service.auth_manager import auth_manager

class AutorForm:
    def __init__(self, root, service):
        self.win = root
        self.service = service
        self.on_login_success = None 
        self.setup_ui()
    def setup_ui(self):
        win = self.win
        win.config(bg="#FFFFFF")
        custom_font = font.Font(family="Arial", size=14, weight="bold")

        def center_window(window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f'{width}x{height}+{x}+{y}')

        window_width = 400
        window_height = 350
        center_window(win, window_width, window_height)

        def check_login():
            username = entry1.get()
            password = entry2.get()
            has_error = False
            
            entry1.config(bg="white")
            entry2.config(bg="white")
            
            if not username or username == "Введите логин...":
                entry1.config(bg="#ffebee")
                has_error = True
            
            if not password or password == "Введите пароль...":
                entry2.config(bg="#ffebee")
                has_error = True
            
            if has_error:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            # Проверяем авторизацию
            if auth_manager.login(username, password):
                print(f"✅ Успешная авторизация: {username}")
                messagebox.showinfo("Успех", "Авторизация прошла успешно!")
                
                # Вызываем callback при успешной авторизации
                if self.on_login_success:
                    self.on_login_success()
            else:
                messagebox.showerror("Ошибка", "Неверные данные для входа")

        label1 = tk.Label(text="Вход в систему", fg="black", bg="#FFFFFF", font=custom_font)
        label1.place(x=120, y=45)

        frame1 = tk.Frame(win, bg="#ffffff", bd=1, relief="solid")
        frame1.place(x=50, y=100, width=300, height=40)

        icon_label1 = tk.Label(frame1, text="👤", bg="#ffffff", font=("Arial", 14))
        icon_label1.pack(side="left", padx=(10, 5))

        entry1 = tk.Entry(
            frame1,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#2c3e50",
            bd=0,
            relief="flat"
        )
        entry1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        entry1.insert(0, "Введите логин...")

        frame2 = tk.Frame(win, bg="#ffffff", bd=1, relief="solid")
        frame2.place(x=50, y=150, width=300, height=40)

        icon_label2 = tk.Label(frame2, text="🔒", bg="#ffffff", font=("Arial", 14))
        icon_label2.pack(side="left", padx=(10, 5))

        entry2 = tk.Entry(
            frame2,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#2c3e50",
            bd=0,
            relief="flat",
            show="•"  
        )
        entry2.pack(side="left", fill="both", expand=True, padx=(5, 5))
        entry2.insert(0, "Введите пароль...")

        password_visible = False

        def toggle_password():
            nonlocal password_visible
            if password_visible:
                entry2.config(show="•")
                eye_btn.config(text="👁️")
                password_visible = False
            else:
                entry2.config(show="")
                eye_btn.config(text="🔒")
                password_visible = True

        eye_btn = tk.Button(
            frame2,
            text="👁️",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#2c3e50",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=toggle_password
        )
        eye_btn.pack(side="right", padx=(0, 5))

        login_btn = tk.Button(
            win,
            text="Войти",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            bd=0,
            relief="flat",
            width=15,
            height=2,
            command=check_login
        )
        login_btn.place(x=125, y=250)

        def on_entry_focus_in(event):
            widget = event.widget
            if widget.get() in ["Введите логин...", "Введите пароль..."]:
                widget.delete(0, tk.END)
                if widget == entry2:  
                    widget.config(show="•" if not password_visible else "")
            widget.config(bg="#ffffff", fg="#000000")

        def on_entry_focus_out(event):
            widget = event.widget
            if not widget.get():
                if widget == entry1:
                    widget.insert(0, "Введите логин...")
                else:
                    widget.insert(0, "Введите пароль...")
                    widget.config(show="")
                widget.config(bg="#ffffff", fg="#6c757d")

        entry1.bind("<FocusIn>", on_entry_focus_in)
        entry1.bind("<FocusOut>", on_entry_focus_out)
        entry2.bind("<FocusIn>", on_entry_focus_in)
        entry2.bind("<FocusOut>", on_entry_focus_out)

        # Добавляем обработку Enter для быстрой авторизации
        def on_enter_pressed(event):
            check_login()

        entry1.bind("<Return>", on_enter_pressed)
        entry2.bind("<Return>", on_enter_pressed)


