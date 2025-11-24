import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, filedialog
import logging
import os

class ModalReport:
    def __init__(self, parent, email_service):
        self.parent = parent
        self.email_service = email_service
        self.attached_files = []
        self.feedback_window = None
        
    def open_feedback_window(self):
        """Открывает окно для отправки отзыва с возможностью прикрепления файлов"""
        logging.info("📧 Открытие формы обратной связи")
        
        # Создаем окно для обратной связи
        self.feedback_window = Toplevel(self.parent)
        self.feedback_window.title("Обратная связь")
        self.feedback_window.geometry("600x550")
        self.feedback_window.configure(bg="#1E2B3E")
        self.feedback_window.resizable(False, False)
        
        # Центрируем окно
        self.feedback_window.transient(self.parent)
        self.feedback_window.grab_set()
        
        # Список прикрепленных файлов
        self.attached_files = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает виджеты окна обратной связи"""
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
            command=self.send_feedback,
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
    
    def send_feedback(self):
        """Отправляет обратную связь через email service"""
        subject = self.subject_entry.get().strip()
        body = self.text_area.get("1.0", tk.END).strip()
        
        if not subject:
            messagebox.showerror("Ошибка", "Введите тему письма!")
            return
        
        if not body or body == "Опишите подробно проблему, с которой столкнулись:":
            messagebox.showerror("Ошибка", "Введите текст сообщения!")
            return
        
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
        
        # Отправляем письмо через email service
        success, message = self.email_service.send_feedback_email(
            subject=subject,
            body=body,
            attached_files=self.attached_files
        )
        
        # Убираем индикатор
        sending_label.destroy()
        
        if success:
            # Показываем результат
            if self.attached_files:
                files_info = f" с {len(self.attached_files)} прикрепленными файлом(ами)"
            else:
                files_info = ""
                
            messagebox.showinfo("Успех", f"✅ Ваше сообщение отправлено{files_info}!")
            logging.info(f"📧 Письмо с обратной связью успешно отправлено{files_info}")
            
            # Закрываем окно
            self.feedback_window.destroy()
        else:
            messagebox.showerror("Ошибка", message)