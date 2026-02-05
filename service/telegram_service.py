# services/telegram_service.py
import asyncio
from telethon import TelegramClient, errors
import logging
from typing import Optional

class TelegramService:
    """Упрощенный сервис для работы с Telegram API"""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.is_connected = False
        self.is_authenticated = False
        self.logger = logging.getLogger(__name__)
        self.api_id: Optional[int] = None
        self.api_hash: Optional[str] = None
        self.phone: Optional[str] = None
        
    def set_credentials(self, api_id: int, api_hash: str, phone: str = None):
        """Устанавливает учетные данные"""
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.logger.info(f"Установлены учетные данные: api_id={api_id}")
        
    async def connect_with_code(self, code: str = None) -> bool:
        """
        Подключается к Telegram с текущими учетными данными
        
        Args:
            code: Код подтверждения из SMS (опционально)
            
        Returns:
            True если подключение успешно, False в противном случае
        """
        if not self.api_id or not self.api_hash:
            self.logger.error("Учетные данные не установлены")
            return False
            
        try:
            self.logger.info("Подключение к Telegram...")
            
            # Создаем клиента
            self.client = TelegramClient(
                'session',  # Простое имя сессии
                self.api_id,
                self.api_hash
            )
            
            # Устанавливаем соединение
            await self.client.connect()
            
            # Проверяем авторизацию
            if not await self.client.is_user_authorized():
                if self.phone:
                    self.logger.info(f"Запрашиваю код для {self.phone}")
                    
                    if not code:
                        self.logger.warning("Требуется код подтверждения")
                        return False
                    
                    try:
                        # Пытаемся войти с кодом
                        await self.client.sign_in(self.phone, code)
                        self.logger.info("Успешный вход с кодом")
                        
                    except errors.PhoneCodeInvalidError:
                        self.logger.error("Неверный код подтверждения")
                        return False
                    except errors.SessionPasswordNeededError:
                        self.logger.error("Требуется двухфакторная аутентификация")
                        return False
                else:
                    self.logger.error("Телефон не указан")
                    return False
            
            self.is_connected = True
            self.is_authenticated = True
            self.logger.info("Успешно подключено к Telegram")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {str(e)}")
            return False
    
    async def send_to_saved_messages(self, message: str) -> bool:
        """
        Отправляет сообщение в Избранное (Saved Messages)
        """
        if not self.is_connected or not self.client:
            self.logger.error("Не подключен к Telegram")
            return False
            
        try:
            self.logger.info(f"Отправка сообщения в Избранное: {message[:50]}...")
            
            # Отправляем сообщение самому себе
            await self.client.send_message('me', message)
            
            self.logger.info("Сообщение успешно отправлено")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {str(e)}")
            return False
    
    async def disconnect(self):
        """Отключается от Telegram"""
        if self.client:
            try:
                await self.client.disconnect()
                self.is_connected = False
                self.is_authenticated = False
                self.logger.info("Отключено от Telegram")
            except Exception as e:
                self.logger.error(f"Ошибка при отключении: {str(e)}")
    
    def is_ready(self) -> bool:
        """Проверяет, готов ли сервис к работе"""
        return self.is_connected and self.is_authenticated