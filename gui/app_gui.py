import tkinter as tk
from tkinter import ttk
import threading
import asyncio
class AppGUI:
    
    def __init__(self, root, core_instance = None):
        self.root = root
        self.core = core_instance
        self.setup_ui()
        self.start_process("http://localhost:5173/")
    
    def setup_ui(self):
        self.root.title("Мое приложение")
        self.root.geometry("400x300")
        
    def start_process(self, url):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.core.run_main_process(url))
            loop.close()
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()
