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
sys.path.insert(0, os.path.join(base_path, 'service'))

def setup_async():
    """Настройка асинхронного event loop для tkinter"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception as e:
        print(f"Ошибка настройки async: {e}")

def show_auth_form():
    """Показывает форму авторизации и возвращает результат"""
    from gui.autorform import AutorForm
    
    auth_win = tk.Tk()
    auth_win.title("Авторизация")
    
    # Центрируем окно
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    center_window(auth_win, 400, 350)
    
    # Переменная для хранения результата авторизации
    auth_result = {"success": False}
    
    # Создаем форму авторизации
    auth_form = AutorForm(auth_win, None)
    
    def on_successful_login():
        """Вызывается при успешной авторизации"""
        auth_result["success"] = True
        auth_win.quit()  # Выходим из mainloop
        auth_win.destroy()  # Закрываем окно
    
    # Устанавливаем callback для успешной авторизации
    auth_form.on_login_success = on_successful_login
    
    # Запускаем главный цикл для окна авторизации
    auth_win.mainloop()
    
    return auth_result["success"]

def show_main_app():
    """Показывает основное приложение"""
    try:
        print("🚀 Запуск основного приложения...")
        
        from emitter import global_emitter
        from core.core_main import Core
        from gui.app_gui import AppGUI
        
        root = tk.Tk()
        root.title("AutoclickerApp - Авторизован")
        
        # Создаем core
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

def main():
    try:
        print("🚀 Запуск AutoclickerApp...")
        
        # Настраиваем async loop
        setup_async()
        
        # Проверяем авторизацию
        from service.auth_manager import auth_manager
        
        if auth_manager.check_auth():
            print("✅ Пользователь уже авторизован")
            show_main_app()
        else:
            print("🔐 Требуется авторизация")
            # Показываем форму авторизации
            auth_success = show_auth_form()
            
            if auth_success:
                print("✅ Авторизация успешна, запускаем основное приложение")
                show_main_app()
            else:
                print("❌ Авторизация не удалась")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()