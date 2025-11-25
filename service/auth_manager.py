import os
from config.settings import env_service
from datebase_service import db_service
from detected_device import detected_device

class AuthManager:
    def __init__(self):
        self.is_authenticated = False
        self.user = None

        self.oauth_token = env_service.get_env_var('YANDEX_OAUTH_TOKEN')
        self.file_path = env_service.get_env_var('TABLE_PATH')
        self.users_data = []  
    
    def login(self, username, password):
        print(f"🔐 Авторизация: {username}")
        
        self.users_data = db_service.get_data_base(self.oauth_token, self.file_path)
        user_found = self.find_user_by_credentials(username, password)
        
        if user_found:
            self.is_authenticated = True
            self.user = user_found
            print(f"✅ Пользователь {username} авторизован")
            
            # Автоматически добавляем информацию об устройстве
            self.add_device_to_user(username)
            return True
        else:
            return False
    
    def add_device_to_user(self, username):
        """Добавляет информацию об устройстве для авторизованного пользователя"""
        try:
            device_description = detected_device.get_device_description()
            device_id = detected_device.get_device_identifier()
            
            print(f"📱 Обнаружено устройство: {device_description}")
            print(f"🔑 ID устройства: {device_id}")
            
            # Обновляем информацию в таблице (теперь с повторными попытками)
            success = db_service.update_user_device(
                self.oauth_token, 
                self.file_path, 
                username, 
                device_description, 
                device_id
            )
            
            if success:
                print(f"✅ Информация об устройстве добавлена для пользователя {username}")
            else:
                print(f"⚠️ Не удалось добавить информацию об устройстве после нескольких попыток")
                print(f"💡 Устройство будет автоматически добавлено при следующем входе")
                
        except Exception as e:
            print(f"❌ Ошибка при добавлении устройства: {e}")
    
    def check_auth(self):
        return self.is_authenticated

    def find_user_by_credentials(self, username, password):
        for user in self.users_data:
            if user.get('login') == username and user.get('password') == password:
                return user
        return None

auth_manager = AuthManager()