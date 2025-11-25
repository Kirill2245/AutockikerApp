import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from config.settings import env_service
class EmailService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.LOGIN = env_service.get_env_var('LOGIN')
        self.PASSWORD = env_service.get_env_var('PASSWORD')

    def send_feedback_email(self, subject, body, attached_files=None, recipient="rzovliev@gmail.com"):
        """Отправляет письмо с обратной связью и прикрепленными файлами"""
        if attached_files is None:
            attached_files = []
        
        try:
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.LOGIN
            msg['To'] = recipient
            
            # Форматируем тело письма
            formatted_body = f"""
            Сообщение от пользователя KLIK KLAK:

            {body}

            ---
            Отправлено из приложения KLIK KLAK
            """
            
            msg.attach(MIMEText(formatted_body, 'plain', 'utf-8'))
            
            # Прикрепляем файлы
            for file_path in attached_files:
                try:
                    with open(file_path, "rb") as file:
                        # Создаем MIME часть для файла
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        
                    # Кодируем файл в base64
                    encoders.encode_base64(part)
                    
                    # Добавляем заголовки
                    file_name = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{file_name}"'
                    )
                    
                    # Добавляем файл к сообщению
                    msg.attach(part)
                    
                except Exception as file_error:
                    self.logger.error(f"Не удалось прикрепить файл {file_path}: {file_error}")
                    raise Exception(f"Не удалось прикрепить файл {file_path}: {file_error}")
            
            # Пробуем разные способы подключения к SMTP
            smtp_success = False
            smtp_errors = []
            
            # Вариант 1: Gmail с портом 587 (STARTTLS)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
                server.starttls()
                server.login(self.LOGIN, self.PASSWORD)
                server.send_message(msg)
                server.quit()
                smtp_success = True
                self.logger.info("✅ Письмо отправлено через порт 587")
            except Exception as e1:
                smtp_errors.append(f"Порт 587: {e1}")
            
            # Вариант 2: Gmail с портом 465 (SSL) - если первый не сработал
            if not smtp_success:
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
                    server.login(self.LOGIN, self.PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    smtp_success = True
                    self.logger.info("✅ Письмо отправлено через порт 465")
                except Exception as e2:
                    smtp_errors.append(f"Порт 465: {e2}")
            
            # Вариант 3: Yandex - альтернативный почтовый сервис
            if not smtp_success and 'yandex' in self.LOGIN.lower():
                try:
                    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=10)
                    server.login(self.LOGIN, self.PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    smtp_success = True
                    self.logger.info("✅ Письмо отправлено через Yandex")
                except Exception as e3:
                    smtp_errors.append(f"Yandex: {e3}")
            
            if not smtp_success:
                # Если все способы не сработали, показываем ошибку
                error_msg = "Не удалось отправить письмо. Возможные причины:\n"
                error_msg += "\n".join(smtp_errors)
                error_msg += "\n\nПроверьте:\n- Интернет-соединение\n- Настройки брандмауэра\n- Корректность логина/пароля"
                raise Exception(error_msg)
            
            return True, f"Письмо отправлено с {len(attached_files)} прикрепленными файлом(ами)"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "❌ Ошибка авторизации. Проверьте настройки почты."
            self.logger.error("❌ Ошибка авторизации при отправке письма")
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Не удалось отправить письмо: {e}"
            self.logger.error(f"❌ Ошибка отправки письма: {e}")
            return False, error_msg