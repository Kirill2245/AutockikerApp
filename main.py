import sys
import os
import tkinter as tk
import asyncio
import threading

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)
sys.path.insert(0, os.path.join(base_path, 'core'))
sys.path.insert(0, os.path.join(base_path, 'gui'))

def setup_async():
    """Настройка асинхронного event loop для tkinter"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception as e:
        print(f"Ошибка настройки async: {e}")

def main():
    try:
        print("🚀 Запуск AutoclickerApp...")
        
        # Настраиваем async loop ДО импорта модулей
        setup_async()
        
        from emitter import global_emitter
        from core.core_main import Core
        from gui.app_gui import AppGUI
        
        root = tk.Tk()
        root.title("AutoclickerApp")
        
        # Создаем core синхронно
        core = Core()
        
        # Создаем GUI
        app = AppGUI(root, core)
        
        print("✅ GUI создан, запускаем главный цикл...")
        
        # Запускаем асинхронный loop в отдельном потоке
        def run_async_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_forever()
            except Exception as e:
                print(f"Ошибка в async loop: {e}")
        
        async_thread = threading.Thread(target=run_async_loop, daemon=True)
        async_thread.start()
        
        root.mainloop()
        
        # Очистка при закрытии
        try:
            asyncio.get_event_loop().stop()
        except:
            pass
            
        print("✅ Приложение завершено")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()