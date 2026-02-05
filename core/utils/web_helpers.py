# utils/web_helpers.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
class WebHelpers:
    @staticmethod
    def get_element_info(elem):
        """Получает информацию об элементе для логирования"""
        try:
            element_info = []
            
            # Получаем класс элемента
            class_name = elem.get_attribute("class")
            if class_name:
                element_info.append(f"class: {class_name}")
            
            # Получаем текст элемента
            text = elem.text.strip()
            if text:
                element_info.append(f"text: '{text}'")
            
            # Получаем тип элемента (tag name)
            tag_name = elem.tag_name
            element_info.append(f"tag: {tag_name}")
            
            # Получаем другие атрибуты
            element_id = elem.get_attribute("id")
            if element_id:
                element_info.append(f"id: {element_id}")
            
            return ", ".join(element_info)
        except Exception as e:
            return f"не удалось получить информацию: {e}"
    
    @staticmethod
    def wait_for_element(driver, by, value, timeout):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            print(f"Элемент не найден: {value}, ошибка: {e}")
            return None
    
    @staticmethod
    def wait_for_element_by_css(driver, css_selector, timeout):
        """Ожидание элемента по CSS селектору"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            return element
        except Exception as e:
            print(f"Элемент не найден по CSS: {css_selector}, ошибка: {e}")
            return None
    
    @staticmethod
    async def click_element(driver, elem, max_retries, timeout, logger_func, 
                           element_type="элемент", get_info_func=None):
        """Кликает на элемент с повторными попытками"""
        if get_info_func is None:
            get_info_func = WebHelpers.get_element_info
            
        element_info = get_info_func(elem)
        print(f'Клик по {element_type}')
        
        for attempt in range(max_retries):
            try:
                if elem:
                    # Логируем информацию об элементе перед кликом
                    if logger_func:
                        await logger_func(f"Кликаем по {element_type}", logging.INFO)
                    
                    try:
                        # Пробуем обычный клик
                        elem.click()
                    except Exception as click_error:
                        print(f"Обычный клик не сработал, пробуем JavaScript: {click_error}")
                        # Fallback: JavaScript клик
                        driver.execute_script("arguments[0].click();", elem)
                    
                    print(f"Успешный клик по {element_type}")
                    if logger_func:
                        await logger_func(f"✅ Успешный клик по {element_type}: {element_info}", logging.INFO)
                    return True
                await asyncio.sleep(timeout)  
            except Exception as e:
                print(f"Попытка {attempt + 1} не удалась для {element_type}: {e}")
                if logger_func:
                    await logger_func(f"Попытка {attempt + 1} не удалась для {element_type}: {e}", logging.WARNING)
                await asyncio.sleep(timeout // 3)
        return False