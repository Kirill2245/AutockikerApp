# core/element_monitor.py
import asyncio
import logging
from selenium.webdriver.common.by import By
from .web_helpers import WebHelpers

class ElementMonitor:
    def __init__(self, driver, helpers, max_retries, timeout, 
                 class_one_click, class_two_click, class_modal, logger_func):
        """
        Инициализация монитора элементов
        
        Args:
            driver: WebDriver instance
            helpers: Экземпляр WebHelpers
            max_retries: Максимальное количество попыток
            timeout: Таймаут ожидания
            class_one_click: CSS класс для первого клика
            class_two_click: CSS класс для второго клика
            class_modal: CSS класс для модального окна
            logger_func: Функция для логирования
        """
        self.driver = driver
        self.helpers = helpers
        self.max_retries = max_retries
        self.timeout = timeout
        self.class_one_click = class_one_click
        self.class_two_click = class_two_click
        self.class_modal = class_modal
        self.logger = logger_func
        
        self._stop_requested = False
        self.is_clicking = False
        self.last_count = 0
        self.processed_count = 0
        self.last_reset_time = None
        
    def request_stop(self):
        """Запрашивает остановку мониторинга"""
        self._stop_requested = True
        print("🛑 Запрошена остановка мониторинга элементов")
    
    def reset_counters(self):
        """Сбрасывает счетчики"""
        self.last_count = 0
        self.processed_count = 0
        self.last_reset_time = asyncio.get_event_loop().time()
        print("🔄 Счетчики сброшены")
    
    def check_reset_timer(self, interval):
        """Проверяет, не прошло ли время для сброса счетчиков"""
        if self.last_reset_time is None:
            self.last_reset_time = asyncio.get_event_loop().time()
            return False
            
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_reset_time >= interval:
            print(f"⏰ Прошло {interval} секунд, сбрасываем счетчики")
            self.reset_counters()
            return True
        return False
    
    async def process_table_row(self, row, row_index):
        """Обрабатывает одну строку таблицы"""
        try:
            self.is_clicking = True
            
            row_info = self.helpers.get_element_info(row)
            
            if not row.is_displayed() or not row.is_enabled():
                print(f"⚠️ Строка {row_index+1} не доступна для клика, пропускаем")
                return False
            
            # Проверяем, нет ли открытых модальных окон
            await self.close_open_modals()
            
            # Кликаем на строку
            if await self.helpers.click_element(
                self.driver, row, self.max_retries, self.timeout,
                self.logger, "строке таблицы"
            ):
                print(f"✅ Кликнули на строку таблицы {row_index+1}")
                if self.logger:
                    await self.logger(f"✅ Кликнули на строку таблицы {row_index+1}: {row_info}", logging.INFO)
                
                # Обрабатываем модальное окно
                result = await self.process_modal_window(row_index)
                
                self.is_clicking = False
                return result
                
        except Exception as e:
            print(f"❌ Ошибка обработки строки {row_index+1}: {e}")
            if self.logger:
                await self.logger(f"❌ Ошибка обработки строки {row_index+1}: {e}", logging.ERROR)
        
        self.is_clicking = False
        return False
    
    async def close_open_modals(self):
        """Закрывает открытые модальные окна"""
        try:
            open_modals = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".MuiDrawer-paper, .MuiModal-root, [role='dialog']"
            )
            for modal in open_modals:
                try:
                    if modal.is_displayed():
                        print("⚠️ Найдено открытое модальное окно, закрываем")
                        close_btns = modal.find_elements(
                            By.CSS_SELECTOR,
                            "button, [aria-label='close']"
                        )
                        for close_btn in close_btns:
                            if close_btn.is_displayed():
                                self.driver.execute_script("arguments[0].click();", close_btn)
                                await asyncio.sleep(self.timeout)
                                break
                except:
                    continue
        except:
            pass
    
    async def process_modal_window(self, row_index):
        """Обрабатывает модальное окно"""
        # Ищем модальное окно
        modal = self.helpers.wait_for_element_by_css(
            self.driver, ".MuiDrawer-paperAnchorRight", self.timeout
        )
        
        if not modal:
            all_elements = self.driver.find_elements(By.CLASS_NAME, "MuiDrawer-paperAnchorRight")
            for elem in all_elements:
                try:
                    classes = elem.get_attribute("class")
                    if "MuiDrawer-paperAnchorRight" in classes and elem.is_displayed():
                        modal = elem
                        break
                except:
                    continue
        
        if not modal:
            if self.logger:
                await self.logger("❌ Модальное окно не найдено", logging.CRITICAL)
            return False
        
        # Проверяем, что это правая модалка
        modal_classes = modal.get_attribute("class")
        if "MuiDrawer-paperAnchorLeft" in modal_classes:
            if self.logger:
                await self.logger(f"❌ Найдена левая модалка вместо правой: {modal_classes}", logging.WARNING)
            return False
        
        modal_info = self.helpers.get_element_info(modal)
        if self.logger:
            await self.logger(f"✅ Найдено правильное модальное окно: {modal_info}", logging.INFO)
        
        await asyncio.sleep(self.timeout / 2)
        
        # Ищем кнопку "Принять"
        button = self.helpers.wait_for_element(
            modal, By.XPATH, ".//button[text()='Принять']", self.timeout
        )
        
        if not button:
            if self.logger:
                await self.logger("❌ Кнопка 'Принять' не найдена в модальном окне", logging.WARNING)
            return False
        
        button_text = button.text.strip()
        if button_text != "Принять":
            if self.logger:
                await self.logger(f"❌ Найдена кнопка с другим текстом: '{button_text}', пропускаем", logging.WARNING)
            return False
        
        button_info = self.helpers.get_element_info(button)
        if self.logger:
            await self.logger(f"🔘 Найдена кнопка 'Принять': {button_info}", logging.INFO)
        
        # Кликаем на кнопку "Принять"
        if await self.helpers.click_element(
            self.driver, button, self.max_retries, self.timeout,
            self.logger, "кнопке 'Принять'"
        ):
            print(f"✅ Кликнули на кнопку 'Принять' {row_index+1}")
            if self.logger:
                await self.logger(f"✅ Кликнули на кнопку 'Принять' {row_index+1}: {button_info}", logging.INFO)
            
            # Даем время на обработку
            await asyncio.sleep(self.timeout * 2)
            
            # Проверяем, закрылась ли модалка
            await self.ensure_modal_closed(modal)
            
            return True
        
        return False
    
    async def ensure_modal_closed(self, modal):
        """Убеждается, что модальное окно закрыто"""
        try:
            if modal.is_displayed():
                print("⚠️ Модальное окно не закрылось автоматически")
                close_btns = modal.find_elements(
                    By.CSS_SELECTOR,
                    "button, [aria-label='close'], svg"
                )
                for close_btn in close_btns:
                    if close_btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", close_btn)
                        await asyncio.sleep(1)
                        break
        except:
            pass
    
    def find_table_rows(self):
        """Находит строки таблицы"""
        blocks = self.driver.find_elements(By.CLASS_NAME, self.class_one_click)
        if not blocks:
            blocks = self.driver.find_elements(By.CLASS_NAME, "MuiTableRow-root")
        if not blocks:  
            blocks = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        return blocks
    
    async def monitor_elements(self, reset_interval):
        """Основной метод мониторинга элементов"""
        self.reset_counters()
        
        while not self._stop_requested:
            try:
                # Проверяем таймер сброса
                self.check_reset_timer(reset_interval)
                
                # Находим строки таблицы
                blocks = self.find_table_rows()
                if not blocks:
                    if self.logger:
                        await self.logger("Строка таблицы не найдена", logging.CRITICAL)
                    await asyncio.sleep(self.timeout // 3)
                    continue
                
                current_count = len(blocks)
                
                # Если количество элементов уменьшилось - начинаем сначала
                if current_count < self.last_count:
                    print(f"🔁 Количество элементов уменьшилось с {self.last_count} до {current_count}. Начинаем сначала!")
                    if self.logger:
                        await self.logger(f"🔁 Количество элементов уменьшилось с {self.last_count} до {current_count}. Начинаем сначала!", logging.INFO)
                    self.reset_counters()
                    continue
                
                # Если появились новые элементы или мы еще не обработали все
                if current_count > self.processed_count:
                    start_index = self.processed_count
                    
                    print(f"🔄 Продолжаем кликать элементы с {start_index + 1} по {current_count}")
                    if self.logger:
                        await self.logger(f"🔄 Продолжаем кликать элементы с {start_index + 1} по {current_count}", logging.INFO)
                    
                    for i in range(start_index, current_count):
                        if self._stop_requested:
                            break
                        
                        # Перепроверяем элементы
                        current_blocks = self.find_table_rows()
                        if i >= len(current_blocks):
                            print(f"⚠️ Элемент {i+1} пропал, начинаем сначала")
                            self.reset_counters()
                            break
                        
                        row = current_blocks[i]
                        await self.process_table_row(row, i)
                        
                        self.processed_count += 1
                        
                        # Пауза между обработкой строк
                        await asyncio.sleep(self.timeout * 2)
                    
                    self.last_count = current_count
                    print(f"📊 Обработано элементов: {self.processed_count}/{current_count}")
                
                await asyncio.sleep(self.timeout // 3)
                
            except Exception as e:
                print(f"❌ Общая ошибка мониторинга: {e}")
                if self.logger:
                    await self.logger(f"❌ Общая ошибка мониторинга: {e}", logging.ERROR)
                await asyncio.sleep(self.timeout // 3)
        
        if self.logger:
            await self.logger("🛑 Мониторинг остановлен по запросу", logging.INFO)