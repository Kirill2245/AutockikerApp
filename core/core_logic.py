import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
class CoreLogic:
    def __init__(self, driver, max_retries, timeout, classOneClick, classTwoClick, classModal, emitter):
        self.driver = driver
        self.max_retries = max_retries
        self.timeout = timeout
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        self.emitter = emitter
    async def wait_for_element(self, driver, by, value, timeout):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            print(f"Элемент не найден: {value}, ошибка: {e}")
            await self.log(f"Элемент не найден: {value}, ошибка: {e}", logging.WARNING)
        return None
    
    async def log(self, message, level=logging.INFO):
        self.emitter.emit_log(message, level)
        
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
                await self.log(f"Попытка {attempt + 1} не удалась: {e}", logging.WARNING)
                await asyncio.sleep(self.timeout // 3)
        return False
    async def monitor_dynamic_elements_simple(self):
        last_count = 0
        while True:
            try:
                blocks = self.driver.find_elements(By.CLASS_NAME, self.classOneClick)
                if not blocks:
                        blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableRow-root")
                if not blocks:  
                        blocks = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                if not blocks:
                    await self.log("Строка таблицы не найденна", logging.CRITICAL)
                current_count = len(blocks)
                
                if current_count > last_count:
                    print(f"Появилось новых элементов: {current_count - last_count}")
                    await self.log(f"Появилось новых элементов: {current_count - last_count}", logging.INFO)
                    for i in range(last_count, current_count):
                        try:
                            block = blocks[i]
                            if await self.click_element(block, self.max_retries):
                                print(f"Кликнули на строку таблицы {i+1}")
                                await self.log(f"Кликнули на строку таблицы{i+1}", logging.INFO)
                            modal = await self.wait_for_element(self.driver, By.CLASS_NAME, self.classModal, self.timeout)
                            if not modal:
                                modal = await self.wait_for_element(self.driver, By.CLASS_NAME, "MuiPaper-root", self.timeout)
                            if not modal:
                                await self.log("Модальное окно не найденно", logging.CRITICAL)    
                            await asyncio.sleep(self.timeout / 2) 
                            
                            if self.classTwoClick:
                                button = await self.wait_for_element(modal, By.CLASS_NAME, self.classTwoClick, self.timeout)
                                if not button:
                                    try:
                                        button = await self.wait_for_element(modal, By.XPATH, "//button[text()='Принять']", self.timeout)
                                    except:
                                        button = await self.wait_for_element(modal, By.TAG_NAME, "button", self.timeout)
                                        print("Кнопка не найденна")
                            else:
                                try:
                                    button = await self.wait_for_element(modal, By.XPATH, "//button[text()='Принять']")
                                except:
                                    button = await self.wait_for_element(modal, By.TAG_NAME, "button", self.timeout)
                                    print("Кнопка не найденна")
                            if not button:
                                await self.log("Кнопка не найденна", logging.CRITICAL)
                            if await self.click_element(button, self.max_retries):
                                print(f"Кликнули на кнопку {i+1}")
                                await self.log(f"Кликнули на кнопку {i+1}", logging.INFO)
                        except Exception as e:
                            print(f"Ошибка с элементом {i+1}: {e}")
                            await self.log(f"Ошибка с элементом {i+1}: {e}", logging.ERROR)
                        await asyncio.sleep(self.timeout / 10)
                    last_count = current_count
                await asyncio.sleep(self.timeout // 3)
            except Exception as e:
                print(f"Ошибка: {e}")
                await self.log(f"Ошибка {e}", logging.ERROR)
                await asyncio.sleep(self.timeout // 3)