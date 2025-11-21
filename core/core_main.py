import asyncio
import undetected_chromedriver as uc  
import logging
import os
import getpass
import time
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .core_logic import CoreLogic
from emitter import global_emitter

class Core:
    def __init__(self):
        self.emitter = global_emitter
        self.driver = None
        self.is_running = False
        self._stop_requested = False
        self._current_task = None
    
    async def log(self, message, level=logging.INFO):
        self.emitter.emit_log(message, level)
    
    def _get_browser_paths(self):
        """Возвращает пути к различным браузерам"""
        username = getpass.getuser()
        
        browser_paths = {
            'yandex': [
                rf"C:\Users\{username}\AppData\Local\Yandex\YandexBrowser\Application\browser.exe",
                r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
                r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
            ],
            'chrome': [
                rf"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            'edge': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
        }
        
        available_browsers = {}
        for browser_name, paths in browser_paths.items():
            for path in paths:
                if os.path.exists(path):
                    available_browsers[browser_name] = path
                    break
        
        return available_browsers
    
    def _create_browser_options(self, browser_type='yandex'):
        """Создает настройки для браузера - УПРОЩЕННАЯ ВЕРСИЯ"""
        options = uc.ChromeOptions()

        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=0")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        return options
    
    async def _create_driver_simple(self, browser_name, browser_path):
        """Простой запуск драйвера без сложных опций"""
        try:
            await self.log(f"Запуск {browser_name}...", logging.INFO)
            
            options = uc.ChromeOptions()
            options.binary_location = browser_path
            
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            
            driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                headless=False
            )
            
            await self.log(f"✅ {browser_name} успешно запущен", logging.INFO)
            return driver
            
        except Exception as e:
            await self.log(f"❌ Ошибка при запуске {browser_name}: {str(e)[:200]}", logging.ERROR)
            return None
    
    async def _create_driver_with_fallback(self, max_retries=2):
        """Создает драйвер с fallback браузерами - УПРОЩЕННАЯ ВЕРСИЯ"""
        available_browsers = self._get_browser_paths()
        
        if not available_browsers:
            raise Exception("Не найдены установленные браузеры")
        
        await self.log(f"Доступные браузеры: {', '.join(available_browsers.keys())}", logging.INFO)
        
        browser_priority = ['yandex', 'chrome', 'edge']
        
        for browser_name in browser_priority:
            if browser_name not in available_browsers:
                continue
                
            browser_path = available_browsers[browser_name]
            
            driver = await self._create_driver_simple(browser_name, browser_path)
            if driver:
                return driver
        
        await self.log("Пробуем запуск без указания браузера...", logging.WARNING)
        try:
            driver = uc.Chrome(headless=False)
            await self.log("✅ Браузер запущен без указания пути", logging.INFO)
            return driver
        except Exception as e:
            await self.log(f"❌ Не удалось запустить браузер: {e}", logging.ERROR)
            raise Exception(f"Не удалось запустить ни один браузер")
    
    async def _load_url_safely(self, url):
        """Безопасная загрузка URL с повторными попытками"""
        for attempt in range(3):
            try:
                await self.log(f"Попытка {attempt + 1} загрузки URL: {url}", logging.INFO)
                
                self.driver.set_page_load_timeout(30)
                
                self.driver.get(url)
                
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                current_url = self.driver.current_url
                await self.log(f"URL успешно загружен: {current_url}", logging.INFO)
                
                return True
                
            except exceptions.TimeoutException:
                await self.log(f"Таймаут загрузки страницы (попытка {attempt + 1})", logging.WARNING)
                if attempt < 2:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                await self.log(f"Ошибка загрузки URL (попытка {attempt + 1}): {e}", logging.WARNING)
                if attempt < 2:
                    await asyncio.sleep(2)
        
        return False
    
    async def run_main_process(self, url="http://localhost:5173/", timeout=0.5, max_retries=3, 
                            classOneClick="MuiTableRow-root", classTwoClick="MuiButtonBase-root", 
                            classModal="MuiPaper-root"):

        if self.is_running:
            await self.log("Процесс уже запущен", logging.WARNING)
            return

        self._stop_requested = False
        
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        

        await self._safe_quit_driver()
        
        try:
            self.driver = await self._create_driver_with_fallback()
            self.is_running = True
            
            await self.log("Драйвер создан, начинаем загрузку URL...", logging.INFO)

            url_loaded = await self._load_url_safely(self.url)
            
            if not url_loaded:
                await self.log("❌ Не удалось загрузить URL", logging.ERROR)
                return
            
            await self.log("✅ Страница успешно загружена. Запускаем основную логику...", logging.INFO)
            

            coreLogic = CoreLogic(self.driver, self.max_retries, self.timeout, 
                                self.classOneClick, self.classTwoClick, 
                                self.classModal, self.emitter, self)
            
            self._current_task = asyncio.create_task(
                coreLogic.monitor_dynamic_elements_simple()
            )
            
            try:
                await self._current_task
            except asyncio.CancelledError:
                await self.log("Задача мониторинга отменена", logging.INFO)
                
        except Exception as e:
            error_msg = f"Критическая ошибка в основном процессе: {e}"
            print(error_msg)
            await self.log(error_msg, logging.ERROR)
            
        finally:
            if not self._stop_requested:
                await self._safe_quit_driver()
    
    async def _safe_quit_driver(self):
        """Безопасное закрытие драйвера с несколькими попытками"""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass
        
        if self.driver:
            for attempt in range(3):
                try:
                    self.driver.quit()
                    await self.log("Браузер закрыт", logging.INFO)
                    break
                except Exception as e:
                    if attempt < 2:
                        await self.log(f"Попытка {attempt + 1} закрыть браузер не удалась, пробую снова...", logging.WARNING)
                        await asyncio.sleep(1)
                    else:
                        await self.log(f"Не удалось корректно закрыть браузер: {e}", logging.ERROR)
                finally:
                    self.driver = None
                    self.is_running = False
                    self._current_task = None
        
    async def stop_main_process(self):
        """Остановка процесса - безопасная для вызова из GUI"""
        if not self.is_running:
            await self.log("Процесс не запущен", logging.WARNING)
            return
        
        self._stop_requested = True
        await self.log("Запрошена остановка процесса...", logging.INFO)
        
        await self._safe_quit_driver()
        await self.log("Процесс остановлен", logging.INFO)
    
    def is_process_running(self):
        """Проверка статуса процесса"""
        return self.is_running and not self._stop_requested