import os
import sys
from dotenv import load_dotenv
from pathlib import Path

class EnvService:
    def __init__(self):
        self.load_env_variables()
    
    def load_env_variables(self):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
            
            env_path = base_dir / '.env'
        
            load_dotenv(env_path)
            
            print(f"✅ .env файл загружен: {env_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки .env: {e}")
            return False

    def get_env_var(self, var_name, default=None):
        value = os.getenv(var_name, default)
        if value is None:
            print(f"⚠️ Переменная {var_name} не найдена, используется значение по умолчанию: {default}")
        return value

env_service = EnvService()