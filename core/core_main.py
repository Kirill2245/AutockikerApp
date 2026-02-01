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
from webdriver_manager.chrome import ChromeDriverManager
from emitter import global_emitter
import pickle
import zipfile
import requests
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

            # options.add_argument("--disable-dev-shm-usage") 
            # Создаем драйвер с автоподбором версии
            driver = uc.Chrome(
                options=options,
                headless=False,
                version_main=144
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
        
    async def run_main_process(self,email_user, password_user, 
                               url="https://thejwibvoknwefg.org/", timeout=0.5, max_retries=3,classOneClick="css-y6j1my", classTwoClick="css-1xfoprh", 
                            classModal="MuiDrawer-paperAnchorRight",
                             is_browser = True, is_refresh = True , time_refresh = 20):
        """Запуск основного процесса"""
        
        if self.is_running:
            await self.log("⚠️ Процесс уже запущен! Останавливаем предыдущий...")
            await self.stop_main_process()
            await asyncio.sleep(2)

        self._stop_requested = False
        self.is_running = True

        try:
            await self.log("🚀 Начинаем основной процесс...")
            
            if is_browser:
                self.driver = self._create_fire_fox_driver()  # is_browser = True → Firefox
            else:
                self.driver = self._create_chrome_driver()    # is_browser = False → Chrome
            if not self.driver:
                await self.log("❌ Не удалось запустить Браузер")
                self.is_running = False
                return
            
            await self.log("🚀 Браузер запущен, загружаем страницу...")

            # Загружаем страницу
            try:
                self.driver.set_page_load_timeout(30)
                self.driver.delete_all_cookies()
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                await self.log("✅ Страница загружена")
                await self._fill_login_form(email_user, password_user)
                
                # Кликаем на кнопку "Войти"
                await self._click_login_button()
                await asyncio.sleep(3)
            except Exception as e:
                await self.log(f"❌ Ошибка загрузки страницы: {e}")
                await self._safe_quit_driver()
                return
            
            # Запускаем основную логику
            from core.core_logic import CoreLogic
            await asyncio.sleep(2)
            coreLogic = CoreLogic(
                driver=self.driver, 
                max_retries=max_retries, 
                timeout=timeout, 
                classOneClick=classOneClick, 
                classTwoClick=classTwoClick, 
                classModal=classModal, 
                emitter=self.emitter,
                core_instance=self,
                is_refresh = is_refresh,
                time_refresh=time_refresh
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
    async def _fill_login_form(self, email , password):
        """Заполнение формы логина"""
        try:
            
            await self.log("🔍 Ищем поля формы...")
            
            # Ждем появления полей
            email_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "email"))
            )
            
            password_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "password"))
            )
            
            await self.log("✅ Поля формы найдены")
            
            # Заполняем email
            email_field.click()
            email_field.clear()
            await self.log("📧 Ввожу email...")
            
            email_text = email
            for char in email_text:
                email_field.send_keys(char)
                await asyncio.sleep(0.03)  # Имитация печати
            
            # Заполняем пароль
            password_field.click()
            password_field.clear()
            await self.log("🔒 Ввожу пароль...")
            
            password_text = password
            for char in password_text:
                password_field.send_keys(char)
                await asyncio.sleep(0.03)
            
            # Триггерим дополнительные события для React
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                arguments[1].dispatchEvent(new Event('blur', { bubbles: true }));
            """, email_field, password_field)
            
            await self.log("✅ Форма заполнена")
            
            # Проверка значений
            email_value = email_field.get_attribute("value")
            password_value = password_field.get_attribute("value")
            
            if email_value == email_text and password_value == password_text:
                await self.log("✅ Значения корректно установлены")
            else:
                await self.log(f"⚠️ Проверка значений: email={email_value}, password={password_value}")
                
            return True
            
        except Exception as e:
            await self.log(f"❌ Ошибка заполнения формы: {e}")
            return False


    async def _click_login_button(self):
        """Клик на кнопку 'Войти'"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            await self.log("🔍 Ищу кнопку 'Войти'...")
            
            # Ищем кнопку по тексту или классу
            try:
                # Сначала попробуем найти по тексту
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Войти')]"))
                )
            except:
                # Если не нашли по тексту, ищем по классу
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
            
            # Проверяем, что кнопка доступна
            if login_button.is_enabled():
                await self.log("✅ Кнопка 'Войти' найдена и доступна")
                
                
                # Кликаем
                login_button.click()
                await self.log("✅ Кликнул на кнопку 'Войти'")
                
                # Ждем немного после клика
                await asyncio.sleep(2)
                
                return True
            else:
                await self.log("❌ Кнопка 'Войти' недоступна")
                return False
                
        except Exception as e:
            await self.log(f"❌ Ошибка при клике на кнопку 'Войти': {e}")
            return False
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
            
            if self.driver:
                try:
                    # pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
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