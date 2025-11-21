import asyncio
import undetected_chromedriver as uc  
import logging
import os
import getpass
import time
import sys
import psutil
import tempfile
import subprocess
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from emitter import global_emitter

class Core:
    def __init__(self):
        self.emitter = global_emitter
        self.driver = None
        self.is_running = False
        self._stop_requested = False
        self._browser_processes = []
        self._current_task = None
        
        # Для EXE определяем базовый путь
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Создаем свой event loop для EXE
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def log_sync(self, message, level=logging.INFO):
        """Синхронное логирование"""
        try:
            self.emitter.emit_log(message, level)
        except Exception as e:
            print(f"LOG ERROR: {e} - {message}")
    
    async def log(self, message, level=logging.INFO):
        """Асинхронное логирование"""
        self.log_sync(message, level)
    
    async def emit_log(self, message, level=logging.INFO):
        """Алиас для log для совместимости с CoreLogic"""
        await self.log(message, level)
    
    def _get_system_info(self):
        """Диагностика системы"""
        info = []
        info.append(f"Python: {sys.version}")
        info.append(f"Platform: {sys.platform}")
        info.append(f"Current dir: {os.getcwd()}")
        info.append(f"Username: {getpass.getuser()}")
        info.append(f"Base path: {self.base_path}")
        info.append(f"Frozen: {getattr(sys, 'frozen', False)}")
        return "\n".join(info)
    
    def _get_browser_paths(self):
        """Возвращает пути к различным браузерам"""
        username = getpass.getuser()
        
        browser_paths = {
            'yandex': [
                rf"C:\Users\{username}\AppData\Local\Yandex\YandexBrowser\Application\browser.exe",
                r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
            ],
            'chrome': [
                rf"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
    
    async def _create_driver_simple(self):
        """Простой запуск драйвера для EXE"""
        try:
            await self.log("Пробуем simple запуск...", logging.INFO)
            
            options = uc.ChromeOptions()
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            
            # Для EXE файла важно указать правильную рабочую директорию
            driver = uc.Chrome(
                options=options,
                headless=False,
                use_subprocess=True,  # Для EXE лучше True
                version_main=None
            )
            
            await self.log("✅ Simple драйвер запущен", logging.INFO)
            return driver
            
        except Exception as e:
            await self.log(f"❌ Simple не сработал: {e}", logging.WARNING)
            return None
    
    async def _create_driver_with_diagnostic(self):
        """Создает драйвер с диагностикой"""
        try:
            # Диагностика системы
            system_info = self._get_system_info()
            await self.log(f"Диагностика системы:\n{system_info}", logging.INFO)
            
            # Получаем браузеры
            available_browsers = self._get_browser_paths()
            
            await self.log("Доступные браузеры:", logging.INFO)
            for browser, path in available_browsers.items():
                await self.log(f"  {browser}: {path}", logging.INFO)
            
            if not available_browsers:
                await self.log("❌ Не найдены установленные браузеры", logging.ERROR)
                raise Exception("Не найдены установленные браузеры")
            
            # Пробуем простой запуск
            driver = await self._create_driver_simple()
            if driver:
                return driver
            
            # Пробуем конкретные браузеры
            for browser_name, browser_path in available_browsers.items():
                try:
                    await self.log(f"Пробуем запустить {browser_name}...", logging.INFO)
                    
                    options = uc.ChromeOptions()
                    options.binary_location = browser_path
                    options.add_argument("--no-first-run")
                    options.add_argument("--no-default-browser-check")
                    
                    driver = uc.Chrome(
                        options=options,
                        headless=False,
                        use_subprocess=True,
                        version_main=None
                    )
                    
                    await self.log(f"✅ {browser_name} запущен", logging.INFO)
                    return driver
                    
                except Exception as e:
                    await self.log(f"❌ {browser_name} не сработал: {str(e)[:100]}", logging.WARNING)
                    continue
            
            # Последняя попытка - без указания браузера
            await self.log("Пробуем запуск без указания браузера...", logging.WARNING)
            try:
                driver = uc.Chrome(headless=False, use_subprocess=True)
                await self.log("✅ Браузер запущен без указания пути", logging.INFO)
                return driver
            except Exception as e:
                await self.log(f"❌ Не удалось запустить браузер: {e}", logging.ERROR)
                raise
                
        except Exception as e:
            await self.log(f"❌ Критическая ошибка в диагностике: {e}", logging.ERROR)
            raise
    
    def _track_browser_process(self):
        """Отслеживает процессы браузера"""
        try:
            if self.driver and hasattr(self.driver, 'service'):
                service = self.driver.service
                if hasattr(service, 'process') and service.process:
                    self._browser_processes.append(service.process.pid)
        except:
            pass
    
    async def _kill_browser_processes(self):
        """Завершает процессы браузера"""
        browsers_to_kill = ['chrome', 'chromedriver', 'msedge', 'yandex']
        
        for process in psutil.process_iter(['pid', 'name']):
            try:
                process_name = process.info['name'].lower()
                if any(browser in process_name for browser in browsers_to_kill):
                    process.terminate()
                    await asyncio.sleep(0.1)
                    self.log_sync(f"Завершен процесс: {process.info['name']} (PID: {process.info['pid']})", logging.INFO)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self._browser_processes.clear()
    
    async def _create_driver_safe(self):
        """Безопасное создание драйвера"""
        try:
            await self._kill_browser_processes()
            await asyncio.sleep(1)
            
            driver = await self._create_driver_with_diagnostic()
            self._track_browser_process()
            
            return driver
            
        except Exception as e:
            await self.log(f"❌ Ошибка создания драйвера: {e}", logging.ERROR)
            await self._kill_browser_processes()
            raise
    
    async def run_main_process(self, url="http://localhost:5173/", timeout=0.5, max_retries=3, 
                            classOneClick="MuiTableRow-root", classTwoClick="MuiButtonBase-root", 
                            classModal="MuiPaper-root"):
        """Запуск основного процесса"""
        
        if self.is_running:
            await self.log("⚠️ Процесс уже запущен! Останавливаем предыдущий...", logging.WARNING)
            await self.stop_main_process()
            await asyncio.sleep(2)

        self._stop_requested = False
        self.is_running = True

        try:
            # Создаем драйвер
            self.driver = await self._create_driver_safe()
            
            await self.log("🚀 Драйвер создан, загружаем URL...", logging.INFO)

            # Загружаем страницу
            try:
                self.driver.set_page_load_timeout(30)
                self.driver.get(url)
                
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                await self.log("✅ Страница загружена", logging.INFO)
                
            except Exception as e:
                await self.log(f"❌ Ошибка загрузки URL: {e}", logging.ERROR)
                await self._safe_quit_driver()
                return
            
            # Запускаем основную логику
            from core.core_logic import CoreLogic
            coreLogic = CoreLogic(
                driver=self.driver, 
                max_retries=max_retries, 
                timeout=timeout, 
                classOneClick=classOneClick, 
                classTwoClick=classTwoClick, 
                classModal=classModal, 
                emitter=self.emitter,
                core_instance=self
            )
            
            # Запускаем мониторинг
            self._current_task = asyncio.create_task(
                coreLogic.monitor_dynamic_elements_simple()
            )
            
            try:
                await self._current_task
            except asyncio.CancelledError:
                await self.log("Задача мониторинга отменена", logging.INFO)
                
        except Exception as e:
            error_msg = f"❌ Ошибка в основном процессе: {e}"
            await self.log(error_msg, logging.ERROR)
            
        finally:
            if not self._stop_requested:
                await self._safe_quit_driver()
    
    async def _safe_quit_driver(self):
        """Безопасное закрытие драйвера"""
        # Отменяем задачу
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass
        
        # Закрываем драйвер
        if self.driver:
            try:
                self.driver.quit()
                await self.log("✅ Браузер закрыт", logging.INFO)
            except Exception as e:
                await self.log(f"⚠️ Ошибка при закрытии браузера: {e}", logging.WARNING)
            
            self.driver = None
        
        # Убиваем процессы
        await self._kill_browser_processes()
        
        self.is_running = False
        self._stop_requested = False
        self._current_task = None
    
    async def stop_main_process(self):
        """Остановка процесса"""
        if not self.is_running:
            await self.log("Процесс не запущен", logging.WARNING)
            return
        
        self._stop_requested = True
        await self.log("🛑 Запрошена остановка процесса...", logging.INFO)
        await self._safe_quit_driver()
        await self.log("✅ Процесс остановлен", logging.INFO)
    
    def is_process_running(self):
        return self.is_running and not self._stop_requested