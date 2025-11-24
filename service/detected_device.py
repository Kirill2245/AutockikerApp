#!/usr/bin/env python3
import platform
import socket
import uuid
import os
import hashlib
class DetectedDevice:
    def __init__(self):
        self
    def get_unique_system_info(self):
        
        machine_id = hashlib.md5(platform.node().encode()).hexdigest()[:16]
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                            for elements in range(0,8*6,8)][::-1])
        
        info = {
            'unique_id': machine_id,
            'mac_address': mac_address,
            'hostname': platform.node(),
            
            'processor': platform.processor(),
            'architecture': f"{platform.machine()}_{platform.architecture()[0]}",
            'platform': platform.platform(),
            
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            
            'username': os.getlogin(),
            'user_home': os.path.expanduser('~'),
            
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'fqdn': socket.getfqdn()
        }
        
        return info

    def print_fingerprint(self,info):
        """Выводит отпечаток устройства"""
        print("🔍 УНИКАЛЬНЫЙ ОТПЕЧАТОК УСТРОЙСТВА")
        print("=" * 50)
        
        print(f"🆔 Уникальный ID: {info['unique_id']}")
        print(f"📡 MAC-адрес: {info['mac_address']}")
        print(f"💻 Хостнейм: {info['hostname']}")
        print(f"🔧 Процессор: {info['processor'][:50]}...")
        print(f"🏗️ Архитектура: {info['architecture']}")
        print(f"⚙️ Платформа: {info['platform']}")
        print(f"🖥️ ОС: {info['system']} {info['release']}")
        print(f"👤 Пользователь: {info['username']}")
        print(f"🌐 IP-адрес: {info['ip_address']}")
        print(f"📂 Домашняя папка: {info['user_home']}")

obj = DetectedDevice()

result = obj.get_unique_system_info()

obj.print_fingerprint(result)