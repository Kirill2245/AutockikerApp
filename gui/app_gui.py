import tkinter as tk
from tkinter import ttk

class AppGUI:
    
    def __init__(self, root, core_instance = None):
        self.root = root
        self.core = core_instance
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Мое приложение")
        self.root.geometry("400x300")
        
    

root = tk.Tk()

app = AppGUI(root)
root.mainloop()