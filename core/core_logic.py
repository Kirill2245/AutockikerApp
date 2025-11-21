import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

class CoreLogic:
    def __init__(self, driver, max_retries, timeout, classOneClick, classTwoClick, classModal, emitter, core_instance=None):
        self.driver = driver
        self.max_retries = max_retries
        self.timeout = timeout
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        self.emitter = emitter
        self.core_instance = core_instance
    
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
    
    def _get_element_info(self, elem):
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
        
    async def click_element(self, elem, max_retries, element_type="элемент"):
        element_info = self._get_element_info(elem)
        print(f'Клик по {element_type}: {element_info}')
        
        for attempt in range(max_retries):
            try:
                if elem:
                    # Логируем информацию об элементе перед кликом
                    await self.log(f"Кликаем по {element_type}: {element_info}", logging.INFO)
                    
                    elem.click()
                    print(f"Успешный клик по {element_type}")
                    await self.log(f"✅ Успешный клик по {element_type}: {element_info}", logging.INFO)
                    return True
                await asyncio.sleep(self.timeout)  
            except Exception as e:
                print(f"Попытка {attempt + 1} не удалась для {element_type}: {e}")
                await self.log(f"Попытка {attempt + 1} не удалась для {element_type}: {e}", logging.WARNING)
                await asyncio.sleep(self.timeout // 3)
        return False
    
    async def wait_for_element_by_css(self, driver, css_selector, timeout):
        """Ожидание элемента по CSS селектору"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            return element
        except Exception as e:
            print(f"Элемент не найден по CSS: {css_selector}, ошибка: {e}")
            await self.log(f"Элемент не найден по CSS: {css_selector}, ошибка: {e}", logging.WARNING)
        return None
    async def monitor_dynamic_elements_simple(self):
        last_count = 0
        while self.core_instance is None or not self.core_instance._stop_requested:
            try:
                blocks = self.driver.find_elements(By.CLASS_NAME, self.classOneClick)
                if not blocks:
                    blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableRow-root")
                if not blocks:  
                    blocks = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                if not blocks:
                    await self.log("Строка таблицы не найдена", logging.CRITICAL)
                
                current_count = len(blocks)
                
                if current_count > last_count:
                    new_elements_count = current_count - last_count
                    print(f"Появилось новых элементов: {new_elements_count}")
                    await self.log(f"📊 Появилось новых элементов: {new_elements_count}", logging.INFO)
                    
                    for i in range(last_count, current_count):
                        try:
                            block = blocks[i]
                            block_info = self._get_element_info(block)
                            
                            if await self.click_element(block, self.max_retries, "строке таблицы"):
                                print(f"✅ Кликнули на строку таблицы {i+1}")
                                await self.log(f"✅ Кликнули на строку таблицы {i+1}: {block_info}", logging.INFO)
                                
                                # Ждем ПРАВИЛЬНОЕ модальное окно
                                modal = None
                                
                                # Способ 1: Поиск по CSS селектору с классом MuiDrawer-paperAnchorRight
                                modal = await self.wait_for_element_by_css(
                                    self.driver, 
                                    ".MuiDrawer-paperAnchorRight",  # Точка в начале для класса
                                    self.timeout
                                )
                                
                                # Способ 2: Если не нашли, пробуем найти любой элемент с нужным классом
                                if not modal:
                                    all_elements = self.driver.find_elements(By.CLASS_NAME, "MuiDrawer-paperAnchorRight")
                                    for elem in all_elements:
                                        # Проверяем, что это действительно нужная модалка
                                        classes = elem.get_attribute("class")
                                        if "MuiDrawer-paperAnchorRight" in classes:
                                            modal = elem
                                            break
                                
                                if not modal:
                                    await self.log("❌ Модальное окно с классом MuiDrawer-paperAnchorRight не найдено", logging.CRITICAL)
                                    continue  # Переходим к следующему элементу
                                
                                # Проверяем, что нашли правильную модалку
                                modal_classes = modal.get_attribute("class")
                                if "MuiDrawer-paperAnchorLeft" in modal_classes:
                                    await self.log(f"❌ Найдена левая модалка вместо правой: {modal_classes}", logging.WARNING)
                                    continue  # Пропускаем если нашли левую модалку
                                
                                # Модальное окно найдено и проверено
                                modal_info = self._get_element_info(modal)
                                await self.log(f"✅ Найдено правильное модальное окно: {modal_info}", logging.INFO)
                                
                                await asyncio.sleep(self.timeout / 2) 
                                
                                # Ищем кнопку "Принять" в правильной модалке
                                button = await self.wait_for_element(modal, By.XPATH, ".//button[text()='Принять']", self.timeout)
                                
                                if not button:
                                    await self.log("❌ Кнопка 'Принять' не найдена в модальном окне", logging.WARNING)
                                    continue
                                
                                # Проверяем текст кнопки
                                button_text = button.text.strip()
                                if button_text != "Принять":
                                    await self.log(f"❌ Найдена кнопка с другим текстом: '{button_text}', пропускаем", logging.WARNING)
                                    continue
                                
                                # Кликаем на кнопку
                                button_info = self._get_element_info(button)
                                await self.log(f"🔘 Найдена кнопка 'Принять': {button_info}", logging.INFO)
                                
                                if await self.click_element(button, self.max_retries, "кнопке 'Принять'"):
                                    print(f"✅ Кликнули на кнопку 'Принять' {i+1}")
                                    await self.log(f"✅ Кликнули на кнопку 'Принять' {i+1}: {button_info}", logging.INFO)
                                else:
                                    await self.log(f"❌ Не удалось кликнуть на кнопку 'Принять' {i+1}", logging.ERROR)
                                    
                        except Exception as e:
                            print(f"❌ Ошибка с элементом {i+1}: {e}")
                            await self.log(f"❌ Ошибка с элементом {i+1}: {e}", logging.ERROR)
                        
                        await asyncio.sleep(self.timeout / 10)
                    
                    last_count = current_count
                
                await asyncio.sleep(self.timeout // 3)
                
            except Exception as e:
                print(f"❌ Общая ошибка мониторинга: {e}")
                await self.log(f"❌ Общая ошибка мониторинга: {e}", logging.ERROR)
                await asyncio.sleep(self.timeout // 3)
        
        await self.log("🛑 Мониторинг остановлен по запросу", logging.INFO)