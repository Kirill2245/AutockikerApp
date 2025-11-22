# service/auth_manager.py
class AuthManager:
    def __init__(self):
        self.is_authenticated = False
        self.username = None
    
    def login(self, username, password):
        # Для разработки - всегда успешная авторизация
        print(f"🔐 Авторизация: {username}")
        self.is_authenticated = True
        self.username = username
        return True
    
    def logout(self):
        self.is_authenticated = False
        self.username = None
    
    def check_auth(self):
        return self.is_authenticated

# Глобальный экземпляр
auth_manager = AuthManager()