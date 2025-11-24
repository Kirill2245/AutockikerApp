import PyInstaller.__main__
import os
import shutil
import time
import stat

def remove_readonly(func, path, excinfo):
    """Обработчик для удаления read-only файлов"""
    os.chmod(path, stat.S_IWRITE)  
    func(path) 

def build_app():
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"Удаляем папку {folder}...")
            try:
                for attempt in range(3):
                    try:
                        shutil.rmtree(folder, onerror=remove_readonly)
                        print(f"✅ Папка {folder} удалена")
                        break
                    except PermissionError:
                        if attempt == 2:
                            raise
                        print(f"⚠️  Попытка {attempt + 1}: Папка занята, ждем...")
                        time.sleep(1)
            except Exception as e:
                print(f"❌ Не удалось удалить {folder}: {e}")
                print("⚠️  Продолжаем сборку без очистки...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(base_dir, 'main.py')
    
    print(f"Путь к main.py: {main_path}")
    print(f"Файл существует: {os.path.exists(main_path)}")
    
    if not os.path.exists(main_path):
        print("❌ ERROR: main.py не найден!")
        print("Создайте файл main.py в корне проекта")
        return
    
    params = [
        main_path,
        '--onefile',               
        '--windowed',             
        '--name=AutoclickerApp',   
        '--icon=assets/2.ico',  
        '--add-data=core;core',    
        '--add-data=gui;gui',      
        '--add-data=emitter.py;.', 
        '--add-data=assets/2.ico;assets',  
        '--hidden-import=undetected_chromedriver',
        '--hidden-import=selenium',
        '--hidden-import=asyncio',
        '--hidden-import=logging',
        '--clean',                 
    ]
    
    print("Начинаем сборку AutoclickerApp...")
    print("Параметры сборки:", " ".join(params))
    
    try:
        PyInstaller.__main__.run(params)
        print("✅ Сборка завершена успешно!")
        print("📁 EXE файл находится в папке: dist/AutoclickerApp.exe")
        
    except Exception as e:
        print(f"❌ Ошибка при сборке: {e}")
        print("Проверьте наличие всех зависимостей: pip install -r requirements.txt")

if __name__ == "__main__":
    build_app()