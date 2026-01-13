# core/background_refresher.py
import asyncio
import logging
from selenium.webdriver.support.ui import WebDriverWait

class BackgroundRefresher:
    def __init__(self, driver, logger_func, time_refresh, initial_delay=60):
        """
        Инициализация фонового обновления
        
        Args:
            driver: WebDriver instance
            logger_func: Функция для логирования
            time_refresh: Интервал обновления в секундах
            initial_delay: Задержка перед первым обновлением в секундах
        """
        self.driver = driver
        self.logger = logger_func
        self.time_refresh = time_refresh
        self.initial_delay = initial_delay
        self._stop_requested = False
        self.is_clicking = False
        
    def request_stop(self):
        """Запрашивает остановку обновления"""
        self._stop_requested = True
        print("🛑 Запрошена остановка фонового обновления")
    
    async def start(self):
        """Запускает фоновое обновление страницы"""
        # Ждем перед первым обновлением
        print(f"⏳ Ждем {self.initial_delay} секунд перед началом фонового обновления...")
        await asyncio.sleep(self.initial_delay)
        
        refresh_counter = 0
        self._stop_requested = False
        
        while not self._stop_requested:
            try:
                refresh_counter += 1
                
                # Проверяем, не кликаем ли мы сейчас
                if self.is_clicking:
                    print(f"🔄 Пропускаем обновление #{refresh_counter} - идет процесс кликов")
                    await asyncio.sleep(self.time_refresh)
                    continue
                
                print(f"🔄 Фоновое обновление страницы #{refresh_counter}")
                if self.logger:
                    await self.logger(f"🔄 Фоновое обновление страницы #{refresh_counter}", logging.INFO)
                
                # Сохраняем текущий URL
                current_url = self.driver.current_url
                
                # Обновляем страницу
                self.driver.refresh()
                
                # Ждем загрузки страницы
                await asyncio.sleep(3)
                
                # Проверяем, что мы на той же странице
                if self.driver.current_url != current_url:
                    print(f"⚠️ После обновления URL изменился: {self.driver.current_url}")
                    if self.logger:
                        await self.logger("⚠️ После обновления URL изменился", logging.WARNING)
                
                # Ждем полной загрузки
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                except:
                    pass
                
                print(f"✅ Страница обновлена #{refresh_counter}")
                if self.logger:
                    await self.logger(f"✅ Страница успешно обновлена #{refresh_counter}", logging.INFO)
                
                # Ждем до следующего обновления
                await asyncio.sleep(self.time_refresh)
                
            except Exception as e:
                error_msg = f"❌ Ошибка при фоновом обновлении: {e}"
                print(error_msg)
                if self.logger:
                    await self.logger(error_msg, logging.ERROR)
                await asyncio.sleep(8)
        
        print("✅ Фоновое обновление остановлено")