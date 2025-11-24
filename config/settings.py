import os
import sys
from dotenv import load_dotenv
from pathlib import Path

class EnvService:
    def __init__(self):
        self.load_env_variables()
    
    def load_env_variables(self):
        """
        Загружает переменные из .env файла, работает в exe и при разработке
        """
        try:
            # Определяем путь к .env файлу
            if getattr(sys, 'frozen', False):
                # Если запущено как exe - ищем .env рядом с exe
                base_dir = Path(sys.executable).parent
                print(f"🔍 Режим EXE, базовый путь: {base_dir}")
            else:
                # Если запущено как скрипт
                base_dir = Path(__file__).parent
                print(f"🔍 Режим разработки, базовый путь: {base_dir}")
            
            # Пробуем несколько возможных путей
            possible_paths = [
                base_dir / '.env',                    # Рядом с exe/скриптом
                base_dir.parent / '.env',             # На уровень выше
                Path.cwd() / '.env',                  # Текущая рабочая директория
                Path.home() / '.env',                 # Домашняя директория
            ]
            
            env_path = None
            for path in possible_paths:
                if path.exists():
                    env_path = path
                    print(f"✅ Найден .env файл: {path}")
                    break
            
            if env_path:
                # Загружаем переменные
                load_dotenv(env_path)
                print(f"✅ .env файл загружен: {env_path}")
                
                # Проверяем что переменные загружены
                token = os.getenv('YANDEX_OAUTH_TOKEN')
                table_path = os.getenv('TABLE_PATH')
                
                if token:
                    print(f"✅ YANDEX_OAUTH_TOKEN загружен ({len(token)} символов)")
                else:
                    print("❌ YANDEX_OAUTH_TOKEN не найден в .env")
                    
                if table_path:
                    print(f"✅ TABLE_PATH: {table_path}")
                else:
                    print("❌ TABLE_PATH не найден в .env")
                    
                return True
            else:
                print("❌ .env файл не найден ни по одному из путей:")
                for path in possible_paths:
                    print(f"   - {path}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки .env: {e}")
            return False

    def get_env_var(self, var_name, default=None):
        """
        Безопасное получение переменной окружения
        """
        value = os.getenv(var_name, default)
        if value is None:
            print(f"⚠️ Переменная {var_name} не найдена, используется значение по умолчанию: {default}")
        return value

# Глобальный экземпляр
env_service = EnvService()