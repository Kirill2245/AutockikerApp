import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CoreLogic:
    def __init__(self, driver, max_retries, timeout, classOneClick, classTwoClick):
        self.driver = driver
        self.max_retries = max_retries
        self.timeout = timeout
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
    async def wait_for_element(self, driver, by, value, timeout):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            print(f"Элемент не найден: {value}, ошибка: {e}")
        return None
    
    async def click_element(self, elem, max_retries):
        for attempt in range(max_retries):
            try:
                if elem:
                    elem.click()
                    print(f"Успешный клик")
                    return True
                await asyncio.sleep(5)  
            except Exception as e:
                print(f"Попытка {attempt + 1} не удалась: {e}")
                await asyncio.sleep(1)
        return False
    