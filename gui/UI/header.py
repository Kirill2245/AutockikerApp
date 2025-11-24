import tkinter as tk
from tkinter import ttk
class Header():
    def __init__(self, root):
        self.root = root
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