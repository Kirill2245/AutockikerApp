import os
from config.settings import env_service
from datebase_service import db_service

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
        self.is_authenticated = True
        if self.find_user_by_credentials(username, password):
            print(f"✅ Пользователь {username, password} авторизован")
            return True
        else:
            False

    def check_auth(self):
        return self.is_authenticated

    def find_user_by_credentials(self, username, password):
        for user in self.users_data:
            if user.get('login') == username and user.get('password') == password:
                self.user = user
                print(user,'find_user_by_credentials')
                return True
        return False


auth_manager = AuthManager()