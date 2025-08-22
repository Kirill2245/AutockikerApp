import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class Core:
    def __init__(self, url, timeout = 3, max_retries = 3, classOneClick = None, classTwoClick = None):
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
            while True:
                await asyncio.sleep(1)  
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
        
