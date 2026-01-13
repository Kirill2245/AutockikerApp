# core/core_logic.py
import asyncio
import logging
from .web_helpers import WebHelpers
from core.background_refresher import BackgroundRefresher
from core.element_monitor import ElementMonitor

class CoreLogic:
    def __init__(self, driver, max_retries, timeout, classOneClick, classTwoClick, 
                 classModal, emitter, core_instance=None, is_refresh=True, 
                 time_refresh=20, reset_interval=120):
        self.driver = driver
        self.max_retries = max_retries
        self.timeout = timeout
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        self.emitter = emitter
        self.core_instance = core_instance
        self.is_refresh = is_refresh
        self.time_refresh = time_refresh
        self.reset_interval = reset_interval
        
        # Инициализация компонентов
        self.helpers = WebHelpers()
        
        # Инициализация фонового обновления
        self.refresher = None
        if self.is_refresh:
            self.refresher = BackgroundRefresher(
                driver=self.driver,
                logger_func=self.log,
                time_refresh=self.time_refresh,
                initial_delay=60  # 1 минута
            )
        
        # Инициализация монитора элементов
        self.monitor = ElementMonitor(
            driver=self.driver,
            helpers=self.helpers,
            max_retries=self.max_retries,
            timeout=self.timeout,
            class_one_click=self.classOneClick,
            class_two_click=self.classTwoClick,
            class_modal=self.classModal,
            logger_func=self.log
        )
    
    async def log(self, message, level=logging.INFO):
        """Логирование сообщений"""
        self.emitter.emit_log(message, level)
    
    async def monitor_dynamic_elements_simple(self):
        """Запускает мониторинг элементов"""
        try:
            # Запускаем фоновое обновление если нужно
            if self.refresher:
                # Связываем флаги кликов
                self.refresher.is_clicking = self.monitor.is_clicking
                asyncio.create_task(self.refresher.start())
            
            # Запускаем мониторинг элементов
            await self.monitor.monitor_elements(reset_interval=self.reset_interval)
            
        except Exception as e:
            error_msg = f"❌ Критическая ошибка в мониторинге: {e}"
            print(error_msg)
            await self.log(error_msg, logging.CRITICAL)
            raise
    
    def request_stop(self):
        """Останавливает все процессы"""
        print("🛑 Запрашиваю остановку всех процессов...")
        
        if self.monitor:
            self.monitor.request_stop()
        
        if self.refresher:
            self.refresher.request_stop()
    
    async def stop_all(self):
        """Асинхронная остановка всех процессов"""
        self.request_stop()
        await asyncio.sleep(2)  # Даем время на завершение
        
        print("✅ Все процессы остановлены")