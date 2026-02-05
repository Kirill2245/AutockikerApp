# services/telegram_service.py
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.types import InputPeerUser
import logging
from typing import Optional, Dict, List
import sys
import os

class TelegramService:
    
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
        self.logger.info(f"Установлены учетные данные: api_id={api_id}, phone={phone}")
        
    async def connect(self) -> bool:
        """
        Подключается к Telegram с текущими учетными данными
        
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
                'telegram_session',  # Имя файла сессии
                self.api_id,
                self.api_hash
            )
            
            # Устанавливаем соединение
            await self.client.connect()
            
            # Проверяем авторизацию
            if not await self.client.is_user_authorized():
                if self.phone:
                    self.logger.info(f"Запрашиваю код для {self.phone}")
                    await self.client.send_code_request(self.phone)
                    
                    # В GUI приложении нужно показать диалог для ввода кода
                    # Здесь для примера возвращаем False, так как нужен код
                    self.logger.warning("Требуется ввод кода подтверждения")
                    return False
                else:
                    self.logger.error("Телефон не указан для аутентификации")
                    return False
            else:
                self.logger.info("Сессия уже авторизована")
            
            self.is_connected = True
            self.is_authenticated = True
            self.logger.info("Успешно подключено к Telegram")
            return True
            
        except errors.PhoneNumberInvalidError:
            self.logger.error("Неверный номер телефона")
            return False
        except errors.PhoneCodeInvalidError:
            self.logger.error("Неверный код подтверждения")
            return False
        except errors.SessionPasswordNeededError:
            self.logger.error("Требуется двухфакторная аутентификация")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {str(e)}")
            return False
    
    async def send_to_saved_messages(self, message: str) -> bool:
        """
        Отправляет сообщение в Избранное (Saved Messages)
        
        Args:
            message: Текст сообщения
            
        Returns:
            True если отправка успешна, False в противном случае
        """
        if not self.is_connected or not self.client:
            self.logger.error("Не подключен к Telegram")
            return False
            
        try:
            self.logger.info(f"Отправка сообщения в Избранное: {message[:50]}...")
            
            # Отправляем сообщение самому себе (в Saved Messages)
            await self.client.send_message('me', message)
            
            self.logger.info("Сообщение успешно отправлено")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {str(e)}")
            return False
    
    async def send_to_user(self, username: str, message: str) -> bool:
        """
        Отправляет сообщение конкретному пользователю
        
        Args:
            username: Имя пользователя (без @)
            message: Текст сообщения
            
        Returns:
            True если отправка успешна, False в противном случае
        """
        if not self.is_connected or not self.client:
            self.logger.error("Не подключен к Telegram")
            return False
            
        try:
            self.logger.info(f"Отправка сообщения пользователю @{username}")
            
            # Получаем информацию о пользователе
            user = await self.client.get_entity(username)
            
            # Отправляем сообщение
            await self.client.send_message(user, message)
            
            self.logger.info(f"Сообщение успешно отправлено @{username}")
            return True
            
        except errors.UsernameInvalidError:
            self.logger.error(f"Неверное имя пользователя: @{username}")
            return False
        except errors.UsernameNotOccupiedError:
            self.logger.error(f"Пользователь @{username} не найден")
            return False
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
    
    async def verify_code(self, code: str) -> bool:
        """
        Проверяет код подтверждения
        
        Args:
            code: Код из SMS
            
        Returns:
            True если код верный, False в противном случае
        """
        if not self.client or not self.phone:
            return False
            
        try:
            await self.client.sign_in(self.phone, code)
            self.is_authenticated = True
            self.logger.info("Код подтвержден успешно")
            return True
        except errors.PhoneCodeInvalidError:
            self.logger.error("Неверный код подтверждения")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка проверки кода: {str(e)}")
            return False