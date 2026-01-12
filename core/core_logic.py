import asyncio
import undetected_chromedriver as uc  
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

class CoreLogic:
    def __init__(self, driver, max_retries, timeout, classOneClick, classTwoClick, classModal, emitter, core_instance=None, is_refresh_page = True):
        self.driver = driver
        self.max_retries = max_retries
        self.timeout = timeout
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        self.emitter = emitter
        self.core_instance = core_instance
        self.is_refresh_page = is_refresh_page
        self.refresh_task = None  
        
    async def start_page_refresh(self):
        """Запускает периодическое обновление страницы"""
        self.refresh_task = asyncio.create_task(self._refresh_page_periodically())
        
    async def stop_page_refresh(self):
        """Останавливает обновление страницы"""
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
            self.refresh_task = None
            print("🛑 Обновление страницы остановлено")
    
    async def _refresh_page_periodically(self):
        """Обновляет страницу каждые 8 секунд"""
        refresh_interval = 8  # Секунды
        
        try:
            while self.core_instance is None or not self.core_instance._stop_requested:
                await asyncio.sleep(refresh_interval)
                
                if self.core_instance and self.core_instance._stop_requested:
                    break
                    
                try:
                    print("🔄 Обновляю страницу...")
                    await self.log(f"🔄 Обновляю страницу (интервал: {refresh_interval} сек)", logging.INFO)
                    
                    # Сохраняем текущий URL перед обновлением
                    current_url = self.driver.current_url
                    
                    # Обновляем страницу
                    self.driver.refresh()
                    
                    # Ждем загрузки страницы
                    await asyncio.sleep(2)
                    
                    print(f"✅ Страница обновлена. URL: {current_url}")
                    await self.log(f"✅ Страница успешно обновлена", logging.INFO)
                    
                except Exception as e:
                    print(f"❌ Ошибка при обновлении страницы: {e}")
                    await self.log(f"❌ Ошибка при обновлении страницы: {e}", logging.ERROR)
                    
        except asyncio.CancelledError:
            print("🛑 Задача обновления страницы отменена")
            raise
            
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
        # Запускаем обновление страницы перед началом мониторинга
        if self.is_refresh_page == True:
            await self.start_page_refresh()
        
        last_count = 0
        processed_count = 0  # Счетчик обработанных элементов
        
        while self.core_instance is None or not self.core_instance._stop_requested:
            try:
                blocks = self.driver.find_elements(By.CLASS_NAME, self.classOneClick)
                if not blocks:
                    blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableRow-root")
                if not blocks:  
                    blocks = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                if not blocks:
                    await self.log("Строка таблицы не найдена", logging.CRITICAL)
                    await asyncio.sleep(self.timeout // 3)
                    continue
                
                current_count = len(blocks)
                
                # Если количество элементов уменьшилось - начинаем сначала
                if current_count < last_count:
                    print(f"🔁 Количество элементов уменьшилось с {last_count} до {current_count}. Начинаем сначала!")
                    await self.log(f"🔁 Количество элементов уменьшилось с {last_count} до {current_count}. Начинаем сначала!", logging.INFO)
                    last_count = 0
                    processed_count = 0
                    continue
                
                # Если появились новые элементы или мы еще не обработали все
                if current_count > processed_count:
                    # Начинаем с первого необработанного элемента
                    start_index = processed_count
                    
                    print(f"🔄 Продолжаем кликать элементы с {start_index + 1} по {current_count}")
                    await self.log(f"🔄 Продолжаем кликать элементы с {start_index + 1} по {current_count}", logging.INFO)
                    
                    for i in range(start_index, current_count):
                        # Перепроверяем элементы на каждой итерации
                        current_blocks = self.driver.find_elements(By.CLASS_NAME, self.classOneClick)
                        if not current_blocks:
                            current_blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableRow-root")
                        if not current_blocks:  
                            current_blocks = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                        
                        # Если элемент пропал - начинаем сначала
                        if i >= len(current_blocks):
                            print(f"⚠️ Элемент {i+1} пропал, начинаем сначала")
                            last_count = 0
                            processed_count = 0
                            break
                        
                        try:
                            block = current_blocks[i]
                            block_info = self._get_element_info(block)
                            
                            if not block.is_displayed() or not block.is_enabled():
                                print(f"⚠️ Элемент {i+1} не доступен для клика, пропускаем")
                                processed_count += 1  # Все равно считаем обработанным
                                continue
                            
                            if await self.click_element(block, self.max_retries, "строке таблицы"):
                                print(f"✅ Кликнули на строку таблицы {i+1}")
                                await self.log(f"✅ Кликнули на строку таблицы {i+1}: {block_info}", logging.INFO)
                                
                                modal = await self.wait_for_element_by_css(
                                    self.driver, 
                                    ".MuiDrawer-paperAnchorRight",
                                    self.timeout
                                )
                                
                                if not modal:
                                    all_elements = self.driver.find_elements(By.CLASS_NAME, "MuiDrawer-paperAnchorRight")
                                    for elem in all_elements:
                                        classes = elem.get_attribute("class")
                                        if "MuiDrawer-paperAnchorRight" in classes:
                                            modal = elem
                                            break
                                
                                if not modal:
                                    await self.log("❌ Модальное окно с классом MuiDrawer-paperAnchorRight не найдено", logging.CRITICAL)
                                    processed_count += 1  # Считаем обработанным даже при ошибке
                                    continue
                                
                                modal_classes = modal.get_attribute("class")
                                if "MuiDrawer-paperAnchorLeft" in modal_classes:
                                    await self.log(f"❌ Найдена левая модалка вместо правой: {modal_classes}", logging.WARNING)
                                    processed_count += 1  # Считаем обработанным
                                    continue
                                
                                modal_info = self._get_element_info(modal)
                                await self.log(f"✅ Найдено правильное модальное окно: {modal_info}", logging.INFO)
                                
                                await asyncio.sleep(self.timeout / 2) 
                                
                                button = await self.wait_for_element(modal, By.XPATH, ".//button[text()='Принять']", self.timeout)
                                
                                if not button:
                                    await self.log("❌ Кнопка 'Принять' не найдена в модальном окне", logging.WARNING)
                                    processed_count += 1  # Считаем обработанным
                                    continue
                                
                                button_text = button.text.strip()
                                if button_text != "Принять":
                                    await self.log(f"❌ Найдена кнопка с другим текстом: '{button_text}', пропускаем", logging.WARNING)
                                    processed_count += 1  # Считаем обработанным
                                    continue
                                
                                button_info = self._get_element_info(button)
                                await self.log(f"🔘 Найдена кнопка 'Принять': {button_info}", logging.INFO)
                                
                                if await self.click_element(button, self.max_retries, "кнопке 'Принять'"):
                                    print(f"✅ Кликнули на кнопку 'Принять' {i+1}")
                                    await self.log(f"✅ Кликнули на кнопку 'Принять' {i+1}: {button_info}", logging.INFO)
                                else:
                                    await self.log(f"❌ Не удалось кликнуть на кнопку 'Принять' {i+1}", logging.ERROR)
                                
                                # Увеличиваем счетчик обработанных элементов
                                processed_count += 1
                                    
                            else:
                                # Если не удалось кликнуть на строку, все равно считаем обработанным
                                processed_count += 1
                                    
                        except Exception as e:
                            print(f"❌ Ошибка с элементом {i+1}: {e}")
                            await self.log(f"❌ Ошибка с элементом {i+1}: {e}", logging.ERROR)
                            processed_count += 1  # Считаем обработанным даже при ошибке
                        
                        await asyncio.sleep(self.timeout / 10)
                    
                    # Обновляем общий счетчик
                    last_count = current_count
                    print(f"📊 Обработано элементов: {processed_count}/{current_count}")
                
                await asyncio.sleep(self.timeout // 3)
                
            except Exception as e:
                print(f"❌ Общая ошибка мониторинга: {e}")
                await self.log(f"❌ Общая ошибка мониторинга: {e}", logging.ERROR)
                await asyncio.sleep(self.timeout // 3)
        
        # Останавливаем обновление страницы при остановке мониторинга
        await self.stop_page_refresh()
        await self.log("🛑 Мониторинг остановлен по запросу", logging.INFO)