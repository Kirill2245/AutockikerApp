import tkinter as tk
from gui.app_gui import AppGUI
from core.core_main import Core
def main():
    
    root = tk.Tk()
    core = Core()
    app = AppGUI(root, core)

    root.mainloop()

if __name__ == "__main__":
    main()