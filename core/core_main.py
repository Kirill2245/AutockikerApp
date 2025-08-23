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
    async def log(self, message, level=logging.INFO):
        self.emitter.emit_log(message, level)
    async def run_main_process(self, url, timeout = 0.5, max_retries = 3, classOneClick = "block", classTwoClick = "MuiButtonBase-root", classModal = "modal"):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        driver = uc.Chrome(use_subprocess=True)
        await self.log("Запуск основного процесса...", logging.INFO)
        try:
            driver.get(self.url)
            print("Страница загружена. Ожидаем динамические элементы...")
            await self.log("Страница загружена. Ожидаем динамические элементы...", logging.INFO)
            coreLogic = CoreLogic(driver, self.max_retries, self.timeout, self.classOneClick, self.classTwoClick, self.classModal, self.emitter)
            await coreLogic.monitor_dynamic_elements_simple()
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            await self.log(f"Критическая ошибка: {e}", logging.ERROR)
        finally:
            driver.quit()
    async def stop_main_process(self):
        driver = uc.Chrome(use_subprocess=True)
        driver.quit()

if __name__ == "__main__":
    core = Core()
    asyncio.run(core.run_main_process("http://localhost:5173/"))
        
