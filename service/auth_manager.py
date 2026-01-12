import os
from config.settings import env_service
from datebase_service import db_service
from detected_device import detected_device
from pathlib import Path
import getpass
class AuthManager:
    def __init__(self):
        self.is_authenticated = False
        self.user = None
        # self.oauth_token = env_service.get_env_var('YANDEX_OAUTH_TOKEN')
        # self.file_path = env_service.get_env_var('TABLE_PATH')
        self.oauth_token = "y0__xDD0OCrBRjblgMg9-z6qhW5_m8Dq2c_V4cpAP-EAM53ucT-sw"
        self.file_path = "/BaseUserAuto.xlsx"
        self.users_data = []
        self.auth_file = self._get_auth_file_path()
        
        # Пытаемся автоматически авторизоваться по сохраненным данным
        self.auto_login_from_file()
    def _get_auth_file_path(self):
        """Автоматически определяет путь к файлу авторизации на основе текущего пользователя"""
        try:
            # Получаем имя текущего пользователя системы
            current_user = getpass.getuser()
            
            # Определяем ОС и создаем соответствующий путь
            if os.name == 'nt':  # Windows
                # Вариант 1: В папке пользователя (AppData)
                auth_file = Path.home() / "auth_data.txt"
                
                # Или вариант 2: В рабочем столе (для тестирования)
                # auth_file = Path.home() / "Desktop" / "auth_data.txt"
                
            else:  # Linux/Mac
                # Для Unix-подобных систем
                auth_file = Path.home() / "auth_data.txt"
            
            # Создаем директорию если не существует
            auth_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Путь к файлу авторизации: {auth_file}")
            print(f"👤 Текущий пользователь системы: {current_user}")
            
            return str(auth_file)
            
        except Exception as e:
            print(f"⚠️ Не удалось определить путь автоматически: {e}")
            # Возвращаем путь по умолчанию
            return str(Path.home() / "auth_data.txt")
    def auto_login_from_file(self):
        """Пытается авторизоваться по данным из файла"""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Извлекаем логин и пароль из файла
                username = None
                password = None
                
                for line in lines:
                    if line.startswith('login='):
                        username = line.split('=')[1].strip()
                    elif line.startswith('password='):
                        password = line.split('=')[1].strip()
                
                if username and password:
                    print(f"🔍 Найдены сохраненные данные для: {username}")
                    print("🔄 Пытаюсь автоматически авторизоваться...")
                    
                    # Пытаемся войти с этими данными
                    if self._try_login(username, password):
                        print(f"✅ Автоматическая авторизация успешна!")
                        return True
                    else:
                        print("❌ Автоматическая авторизация не удалась")
            
            except Exception as e:
                print(f"⚠️ Ошибка при чтении файла авторизации: {e}")
        
        return False
    
    def login(self, username=None, password=None):
        """Авторизация с возможностью автоматического входа"""
        # Если не переданы логин/пароль, используем сохраненные
        if username is None or password is None:
            if not self.auto_login_from_file():
                print("❌ Нет сохраненных данных для авторизации")
                return False
            return True
        else:
            # Обычная авторизация
            print(f"🔐 Авторизация: {username}")
            
            if self._try_login(username, password):
                # Сохраняем успешные данные в файл
                self._save_to_file(username, password)
                return True
            else:
                return False
    
    def _try_login(self, username, password):
        """Попытка авторизации"""
        self.users_data = db_service.get_data_base(self.oauth_token, self.file_path)
        user_found = self.find_user_by_credentials(username, password)
        
        if user_found:
            self.is_authenticated = True
            self.user = user_found
            print(f"✅ Пользователь {username} авторизован")
            
            # Добавляем информацию об устройстве
            self.add_device_to_user(username)
            return True
        
        return False
    
    def _save_to_file(self, username, password):
        """Сохраняет логин и пароль в файл"""
        try:
            # Создаем папку если не существует
            folder = os.path.dirname(self.auth_file)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)
            
            # Сохраняем данные
            with open(self.auth_file, 'w', encoding='utf-8') as f:
                f.write(f"login={username}\n")
                f.write(f"password={password}\n")
            
            print(f"💾 Данные сохранены в файл: {self.auth_file}")
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
    
    def add_device_to_user(self, username):
        """Добавляет информацию об устройстве"""
        try:
            device_description = detected_device.get_device_description()
            device_id = detected_device.get_device_identifier()
            
            print(f"📱 Устройство: {device_description}")
            
            success = db_service.update_user_device(
                self.oauth_token, 
                self.file_path, 
                username, 
                device_description, 
                device_id
            )
            
            if success:
                print(f"✅ Информация об устройстве добавлена")
                
        except Exception as e:
            print(f"❌ Ошибка при добавлении устройства: {e}")
    
    def logout(self):
        """Выход из системы"""
        self.is_authenticated = False
        self.user = None
        print("👋 Выход из системы")
    
    def delete_auth_file(self):
        """Удаляет файл с данными авторизации"""
        try:
            if os.path.exists(self.auth_file):
                os.remove(self.auth_file)
                print(f"🗑️ Файл авторизации удален: {self.auth_file}")
        except Exception as e:
            print(f"❌ Ошибка при удалении файла: {e}")
    
    def check_auth(self):
        return self.is_authenticated

    def find_user_by_credentials(self, username, password):
        for user in self.users_data:
            if user.get('login') == username and user.get('password') == password:
                return user
        return None

auth_manager = AuthManager()