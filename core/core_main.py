import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core_logic import CoreLogic
class Core:
    def __init__(self, url, timeout = 1, max_retries = 3, classOneClick = "block", classTwoClick = None):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick

    async def run_main_process(self):
        driver = uc.Chrome(use_subprocess=True)
        try:
            driver.get(self.url)
            print("Страница загружена. Ожидаем динамические элементы...")
            coreLogic = CoreLogic(driver, self.max_retries, self.timeout, self.classOneClick, self.classTwoClick)
            await coreLogic.monitor_dynamic_elements_simple()
        except Exception as e:
            print(f"Критическая ошибка: {e}")
        finally:
            driver.quit()
    async def stop_main_process(self):
        driver = uc.Chrome(use_subprocess=True)
        driver.quit()

if __name__ == "__main__":
    core = Core("http://localhost:5173/")
    asyncio.run(core.run_main_process())
        
