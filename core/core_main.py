
import asyncio
import undetected_chromedriver as uc  
import logging
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .core_logic import CoreLogic
from emitter import global_emitter

class Core:
    def __init__(self):
        self.emitter = global_emitter
        self.driver = None
        self.is_running = False
        self._stop_requested = False
    
    async def log(self, message, level=logging.INFO):
        self.emitter.emit_log(message, level)
    
    async def run_main_process(self, url="http://localhost:5173/", timeout=0.5, max_retries=3, 
                            classOneClick="MuiTableRow-root", classTwoClick="MuiButtonBase-root", 
                            classModal="MuiPaper-root"):

        self._stop_requested = False
        
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.driver = uc.Chrome(use_subprocess=True)
        self.is_running = True
        
        await self.log("Запуск основного процесса...", logging.INFO)

        try:
            self.driver.get(self.url)
            await self.log("Страница загружена. Ожидаем динамические элементы...", logging.INFO)
            
            coreLogic = CoreLogic(self.driver, self.max_retries, self.timeout, 
                                self.classOneClick, self.classTwoClick, 
                                self.classModal, self.emitter, self)
            
            await coreLogic.monitor_dynamic_elements_simple()
                
        except Exception as e:
            error_msg = f"Критическая ошибка: {e}"
            print(error_msg)
            await self.log(error_msg, logging.ERROR)
        finally:
            await self._safe_quit_driver()
    
    async def _safe_quit_driver(self):
        """Безопасное закрытие драйвера"""
        if self.driver:
            try:
                self.driver.quit()
                await self.log("Браузер закрыт", logging.INFO)
            except Exception as e:
                await self.log(f"Ошибка при закрытии браузера: {e}", logging.WARNING)
            finally:
                self.driver = None
                self.is_running = False
                self._stop_requested = False
        
    async def stop_main_process(self):
        """Остановка процесса - безопасная для вызова из GUI"""
        if not self.is_running:
            await self.log("Процесс не запущен", logging.WARNING)
            return
        
        self._stop_requested = True
        await self.log("Запрошена остановка процесса...", logging.INFO)
        await asyncio.sleep(0.5)