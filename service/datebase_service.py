from detected_device import detected_device
import requests
import json
import pandas as pd
from io import BytesIO
import os
import re
import tempfile
import time  

class DateBaseService:
    def __init__(self):
        pass

    def df_to_objects_list(self, df):
        if df is None or df.empty:
            print("⚠️ DataFrame пуст или не существует")
            return []
        objects_list = df.to_dict('records')
        return objects_list
    
    def read_yandex_table_simple(self, oauth_token: str, file_path: str):
        headers = {
            'Authorization': f'OAuth {oauth_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
            params = {'path': file_path}
            
            response = requests.get(download_url, headers=headers, params=params)
            response.raise_for_status()
            
            download_info = response.json()
            file_url = download_info['href']
            
            file_response = requests.get(file_url)
            file_response.raise_for_status()
            
            excel_data = BytesIO(file_response.content)
            
            df = pd.read_excel(
                excel_data,
                dtype=str,  
                na_filter=False,  
                keep_default_na=False  
            )
            
            df = df.fillna('')
            return df
            
        except Exception as e:
            print(f"❌ Ошибка чтения таблицы: {e}")
            return None
    
    def extract_device_id_from_description(self, device_description):
        """Извлекает device_id из описания устройства"""
        # Ищем MAC адрес в описании
        mac_pattern = r'MAC:([0-9a-fA-F:]+)'
        match = re.search(mac_pattern, device_description)
        if match:
            return match.group(1)
        return None
    
    def is_device_already_registered(self, devices_list, device_id, mac_address):
        """Проверяет, зарегистрировано ли устройство по ID или MAC"""
        for device in devices_list:
            # Извлекаем MAC из существующего описания
            existing_mac = self.extract_device_id_from_description(device)
            if existing_mac and existing_mac.lower() == mac_address.lower():
                return True
            # Также проверяем по device_id если он есть в описании
            if device_id in device:
                return True
        return False
    
    def update_user_device(self, oauth_token: str, file_path: str, user_login: str, device_description: str, device_id: str):
        """
        Обновляет информацию об устройстве пользователя с повторными попытками
        """
        max_retries = 3  # Количество попыток
        retry_delay = 2  # Задержка между попытками в секундах
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Попытка {attempt + 1}/{max_retries} обновления устройства...")
                
                # Читаем текущую таблицу
                df = self.read_yandex_table_simple(oauth_token, file_path)
                if df is None:
                    print("❌ Не удалось прочитать таблицу для обновления")
                    continue  # Пробуем снова
                
                # Находим пользователя
                user_mask = df['login'] == user_login
                if not user_mask.any():
                    print(f"❌ Пользователь {user_login} не найден в таблице")
                    return False
                
                # Получаем текущее значение devices
                current_devices = df.loc[user_mask, 'device'].iloc[0]
                
                # Получаем MAC адрес для проверки
                mac_address = detected_device.get_mac_address()
                
                # Проверяем, есть ли уже это устройство
                if current_devices and current_devices.strip():
                    devices_list = [d.strip() for d in current_devices.split(',')]
                    
                    # Проверяем по MAC адресу (более надежно чем по device_id)
                    device_exists = self.is_device_already_registered(devices_list, device_id, mac_address)
                    
                    if not device_exists:
                        # Добавляем новое устройство с номером
                        device_number = len(devices_list) + 1
                        new_device = f"Устройство {device_number} [{device_description}]"
                        devices_list.append(new_device)
                        new_devices_value = ', '.join(devices_list)
                        print(f"✅ Добавлено новое устройство: {device_description}")
                    else:
                        print(f"ℹ️ Устройство уже зарегистрировано для пользователя {user_login}")
                        return True
                else:
                    # Первое устройство
                    new_devices_value = f"Устройство 1 [{device_description}]"
                    print(f"✅ Добавлено первое устройство: {device_description}")
                
                # Обновляем значение
                df.loc[user_mask, 'device'] = new_devices_value
                
                # Сохраняем обратно в Яндекс Диск
                success = self.save_dataframe_to_yandex(df, oauth_token, file_path)
                
                if success:
                    return True
                else:
                    print(f"❌ Попытка {attempt + 1} не удалась")
                    if attempt < max_retries - 1:
                        print(f"⏳ Ждем {retry_delay} секунд перед повторной попыткой...")
                        time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"❌ Ошибка в попытке {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        print("❌ Все попытки обновления устройства не удались")
        return False
    
    def save_dataframe_to_yandex(self, df, oauth_token: str, file_path: str):
        """
        Сохраняет DataFrame обратно в Яндекс Диск
        """
        temp_file = None
        try:
            # Создаем временный файл в системной временной директории
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"temp_table_{os.getpid()}.xlsx")
            
            df.to_excel(temp_file, index=False)
            
            # Получаем URL для загрузки
            headers = {
                'Authorization': f'OAuth {oauth_token}',
                'Content-Type': 'application/json'
            }
            
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {
                'path': file_path,
                'overwrite': 'true'
            }
            
            response = requests.get(upload_url, headers=headers, params=params)
            
            if response.status_code == 423:
                print("⚠️ Файл заблокирован для редактирования. Информация об устройстве не сохранена.")
                return False
                
            response.raise_for_status()
            
            upload_info = response.json()
            upload_url = upload_info['href']
            
            # Загружаем файл
            with open(temp_file, 'rb') as f:
                upload_response = requests.put(upload_url, files={'file': f})
                upload_response.raise_for_status()
            
            print("✅ Информация об устройстве успешно обновлена в таблице")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения таблицы: {e}")
            return False
        finally:
            # Всегда пытаемся удалить временный файл
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def get_user_devices_count(self, oauth_token: str, file_path: str, user_login: str):
        """
        Возвращает количество зарегистрированных устройств пользователя
        """
        try:
            df = self.read_yandex_table_simple(oauth_token, file_path)
            if df is None:
                return 0
            
            user_mask = df['login'] == user_login
            if not user_mask.any():
                return 0
            
            current_devices = df.loc[user_mask, 'device'].iloc[0]
            if not current_devices or not current_devices.strip():
                return 0
            
            devices_list = [d.strip() for d in current_devices.split(',')]
            return len(devices_list)
            
        except Exception as e:
            print(f"❌ Ошибка получения количества устройств: {e}")
            return 0
    
    def get_data_base(self, oauth_token: str, file_path: str):
        df = self.read_yandex_table_simple(oauth_token, file_path)
        if df is not None:
            return self.df_to_objects_list(df)
        return []

db_service = DateBaseService()