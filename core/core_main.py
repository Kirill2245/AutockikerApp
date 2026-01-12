import asyncio
import undetected_chromedriver as uc  
import logging
import os
import sys
import psutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from emitter import global_emitter

class Core:
    def __init__(self):
        self.emitter = global_emitter
        self.driver = None
        self.is_running = False
        self._stop_requested = False
        self._current_task = None
        
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
    
    def log_sync(self, message, level=logging.INFO):
        """Синхронное логирование"""
        try:
            self.emitter.emit_log(message, level)
        except Exception as e:
            print(f"LOG: {message}")
    
    async def log(self, message, level=logging.INFO):
        """Асинхронное логирование"""
        self.log_sync(message, level)
    
    def _kill_chrome_processes(self):
        """Завершает процессы Chrome и Chromedriver"""
        try:
            processes_to_kill = ['chrome', 'chromedriver']
            
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    process_name = process.info['name'].lower()
                    if any(browser in process_name for browser in processes_to_kill):
                        process.terminate()
                        print(f"Завершен процесс: {process.info['name']} (PID: {process.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            time.sleep(2)  # Даем время для завершения
            
        except Exception as e:
            print(f"Ошибка при завершении процессов: {e}")

    def _kill_firefox_processes(self):
        """Завершает процессы Firefox и Geckodriver"""
        try:
            processes_to_kill = ['firefox', 'geckodriver']
            
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    process_name = process.info['name'].lower()
                    if any(browser in process_name for browser in processes_to_kill):
                        process.terminate()
                        print(f"Завершен процесс: {process.info['name']} (PID: {process.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            time.sleep(2)  # Даем время для завершения
            
        except Exception as e:
            print(f"Ошибка при завершении процессов Firefox: {e}")

    def _create_chrome_driver(self):
        """Создает драйвер Chrome - простой и надежный способ"""
        try:
            print("🔄 Запускаем Chrome...")
            
            # Убиваем старые процессы
            self._kill_chrome_processes()
            
            # Простые настройки для Chrome
            options = uc.ChromeOptions()
            
            # Минимальный набор аргументов для стабильности
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Создаем драйвер с автоподбором версии
            driver = uc.Chrome(
                options=options,
                headless=False
            )
            
            print("✅ Chrome успешно запущен!")
            return driver
            
        except Exception as e:
            print(f"❌ Ошибка запуска Chrome: {e}")
            return None
        
    def _create_fire_fox_driver(self):
        try:
            print("🔄 Запускаем FireFox...")
            self._kill_chrome_processes()
            self._kill_firefox_processes()
            service = Service(GeckoDriverManager().install())
            options = Options()
            driver = webdriver.Firefox(service=service, options=options)
            print("✅ FireFox успешно запущен!")
            return driver
        except Exception as e:
            print(f"❌ Ошибка запуска FireFox: {e}")
            return None
        
    async def run_main_process(self, url="http://localhost:5173/", timeout=0.5, max_retries=3, 
                            classOneClick="css-y6j1my", classTwoClick="css-1xfoprh", 
                            classModal="MuiDrawer-paperAnchorRight", brouser = True):
        """Запуск основного процесса"""
        
        if self.is_running:
            await self.log("⚠️ Процесс уже запущен! Останавливаем предыдущий...")
            await self.stop_main_process()
            await asyncio.sleep(2)

        self._stop_requested = False
        self.is_running = True

        try:
            await self.log("🚀 Начинаем основной процесс...")
            
            if brouser == True:
                self.driver = self._create_chrome_driver()
            else:
                self.driver = self._create_fire_fox_driver()
            if not self.driver:
                await self.log("❌ Не удалось запустить Браузер")
                self.is_running = False
                return
            
            await self.log("🚀 Браузер запущен, загружаем страницу...")

            # Загружаем страницу
            try:
                self.driver.set_page_load_timeout(30)
                self.driver.get(url)
                
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                await self.log("✅ Страница загружена")
                
            except Exception as e:
                await self.log(f"❌ Ошибка загрузки страницы: {e}")
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
                await self.log("Задача мониторинга отменена")
            except Exception as e:
                await self.log(f"❌ Ошибка в задаче мониторинга: {e}")
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка: {e}"
            await self.log(error_msg)
            
        finally:
            if not self._stop_requested:
                await self._safe_quit_driver()
    
    async def _safe_quit_driver(self):
        """Безопасное закрытие драйвера"""
        try:
            # Отменяем задачу
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
                try:
                    await self._current_task
                except (asyncio.CancelledError, Exception):
                    pass
            
            # Закрываем драйвер
            if self.driver:
                try:
                    self.driver.quit()
                    await self.log("✅ Chrome закрыт")
                except Exception as e:
                    await self.log(f"⚠️ Ошибка при закрытии Chrome: {e}")
                self.driver = None
            
            # Убиваем процессы
            self._kill_chrome_processes()
            self._kill_firefox_processes()
            
        except Exception as e:
            await self.log(f"⚠️ Ошибка при закрытии: {e}")
        finally:
            self.is_running = False
            self._stop_requested = False
            self._current_task = None
    
    async def stop_main_process(self):
        """Остановка процесса"""
        if not self.is_running:
            await self.log("Процесс не запущен")
            return
        
        self._stop_requested = True
        await self.log("🛑 Останавливаем процесс...")
        await self._safe_quit_driver()
        await self.log("✅ Процесс остановлен")
    
    def is_process_running(self):
        return self.is_running and not self._stop_requested