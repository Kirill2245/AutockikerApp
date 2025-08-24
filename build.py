import PyInstaller.__main__
import os
import shutil

def build_app():

    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Удалена папка {folder}")
    

    params = [
        'gui/app_gui.py',          
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