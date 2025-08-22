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
                await asyncio.sleep(self.timeout)  
            except Exception as e:
                print(f"Попытка {attempt + 1} не удалась: {e}")
                await asyncio.sleep(self.timeout // 3)
        return False
    async def monitor_dynamic_elements_simple(self):
        last_count = 0
        while True:
            try:
                blocks = self.driver.find_elements(By.CLASS_NAME, self.classOneClick)
                if not blocks:  
                    blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableBody-root")
                current_count = len(blocks)
                
                if current_count > last_count:
                    print(f"Появилось новых элементов: {current_count - last_count}")
                    
                    for i in range(last_count, current_count):
                        try:
                            block = blocks[i]
                            if await self.click_element(block, self.max_retries):
                                print(f"Кликнули на элемент {i+1}")
                            modal = await self.wait_for_element(self.driver, By.CLASS_NAME, "modal", self.timeout)
                            await asyncio.sleep(self.timeout / 2) 
                            if self.classTwoClick:
                                button = await self.wait_for_element(modal, By.CLASS_NAME, self.classTwoClick, self.timeout)
                            else:
                                button = await self.wait_for_element(modal, By.TAG_NAME, "button", self.timeout)
                            if not button:
                                print("Кнопка не найдена ни по классу, ни по тегу")
                            if await self.click_element(button, self.max_retries):
                                print(f"Кликнули на кнопку {i+1}")
                                
                        except Exception as e:
                            print(f"Ошибка с элементом {i+1}: {e}")
                        await asyncio.sleep(self.timeout / 10)
                    last_count = current_count
                await asyncio.sleep(self.timeout // 3)
            except Exception as e:
                print(f"Ошибка: {e}")
                await asyncio.sleep(self.timeout // 3)