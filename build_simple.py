# build_simple.py
import os
import shutil
import stat
import subprocess

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)  
    func(path) 

def build_with_spec():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Сборка из: {project_dir}")

    spec_file = os.path.join(project_dir, 'AutoclickerApp.spec')
    if not os.path.exists(spec_file):
        print(f"❌ Файл {spec_file} не найден!")
        return
    
    for folder in ['build', 'dist']:
        folder_path = os.path.join(project_dir, folder)
        if os.path.exists(folder_path):
            print(f"🗑️  Удаляем {folder}...")
            try:
                shutil.rmtree(folder_path, onerror=remove_readonly)
                print(f"✅ {folder} удалена")
            except Exception as e:
                print(f"⚠️  Не удалось удалить {folder}: {e}")
    
    os.chdir(project_dir)
    print("🚀 Запускаем сборку через .spec файл...")
    
    try:
        result = subprocess.run([
            'pyinstaller', 'AutoclickerApp.spec'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Сборка завершена успешно!")
            print("📦 EXE файл: dist/AutoclickerApp.exe")
        else:
            print(f"❌ Ошибка сборки: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    build_with_spec()