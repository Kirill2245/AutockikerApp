import tkinter as tk
from tkinter import ttk
from tkinter import font

class AppGUI:
    def __init__(self, root, core_instance = None):
        self.root = root
        self.core = core_instance
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Мое приложение")
        self.root.geometry("700x500")
        self.root.configure(bg = "#193750")
        custom_font = font.Font(family = "Arial", size = 14, weight = "bold")

        self.root.entry1 = tk.Entry(root, width = 30) #ENTRY URL
        self.root.entry1.place(x = 150, y = 50)
        self.root.label1 = tk.Label(root, text = "URL", fg = "White", bg = "#193750", font = custom_font) #LABEL URL
        self.root.label1.place(x = 100,y = 45)
        self.root.style = ttk.Style()
        
        self.root.style.configure("Border.TFrame", background="#696969", borderwidth = 2) #STYLE FRAME
        self.root.frame = ttk.Frame(root, style = "Border.TFrame", padding = 15) 
        self.root.frame.place(x = 50, y = 90, width = 250, height = 300)
        self.root.label2 = tk.Label(root, text = "Setting", fg = "White", bg = "#696969", font = custom_font) #LABEL Settings
        self.root.label2.place(x = 130,y = 90)
        self.root.entry2 = tk.Entry(root, width = 20) #ENTRY Settings
        self.root.entry2.place(x = 150, y = 130)
        self.root.label3 = tk.Label(root, text = "Timeout", fg = "White", bg = "#696969", font = custom_font) #LABEL 
        self.root.label3.place(x = 60,y = 125)




root = tk.Tk()

app = AppGUI(root)
root.mainloop()