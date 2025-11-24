
import platform
import socket
import uuid
import os
import hashlib

class DetectedDevice:
    def __init__(self):
        pass
    
    def get_unique_system_info(self):
        # Используем комбинацию hostname + MAC для более уникального ID
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                            for elements in range(0,8*6,8)][::-1])
        
        # Создаем уникальный ID на основе hostname + MAC
        unique_string = f"{platform.node()}_{mac_address}"
        machine_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
        
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
    
    def get_device_description(self):
        """Возвращает удобочитаемое описание устройства с MAC"""
        info = self.get_unique_system_info()
        description = f"{info['hostname']} ({info['system']} {info['release']}) MAC:{info['mac_address']}"
        return description
    
    def get_device_identifier(self):
        """Возвращает уникальный идентификатор устройства"""
        info = self.get_unique_system_info()
        return info['unique_id']
    
    def get_mac_address(self):
        """Возвращает MAC адрес"""
        info = self.get_unique_system_info()
        return info['mac_address']

detected_device = DetectedDevice()