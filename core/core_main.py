import asyncio
import undetected_chromedriver as uc  
import logging
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core_logic import CoreLogic
from emitter import global_emitter

class Core:
    def __init__(self):
        self.emitter = global_emitter
        self.driver = None
        self.is_running = False
        self._stop_requested = False
        self.current_task = None
    
    async def log(self, message, level=logging.INFO):
        self.emitter.emit_log(message, level)
    
    async def run_main_process(self, url, timeout=0.5, max_retries=3, 
                            classOneClick="block", classTwoClick="MuiButtonBase-root", 
                            classModal="modal"):
        self._stop_requested = False
        
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.classOneClick = classOneClick
        self.classTwoClick = classTwoClick
        self.classModal = classModal
        
        self.driver = uc.Chrome(use_subprocess=True)
        self.is_running = True
        
        await self.log("Запуск основного процесса...", logging.INFO)
        
        try:
            self.driver.get(self.url)
            await self.log("Страница загружена. Ожидаем динамические элементы...", logging.INFO)
            
            coreLogic = CoreLogic(self.driver, self.max_retries, self.timeout, 
                                self.classOneClick, self.classTwoClick, 
                                self.classModal, self.emitter)
            
            await self._run_with_stop_check(coreLogic)
            
        except Exception as e:
            error_msg = f"Критическая ошибка: {e}"
            print(error_msg)
            await self.log(error_msg, logging.ERROR)
        finally:
            await self._safe_quit_driver()
    
    async def _run_with_stop_check(self, coreLogic):
        while not self._stop_requested:
            try:
                task = asyncio.create_task(
                    coreLogic.monitor_dynamic_elements_simple()
                )
                self.current_task = task
                done, pending = await asyncio.wait(
                    [task],
                    timeout=1.0,  
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                if self._stop_requested:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    break
                    
            except asyncio.CancelledError:
                await self.log("Мониторинг прерван", logging.INFO)
                break
            except Exception as e:
                await self.log(f"Ошибка в мониторинге: {e}", logging.ERROR)
                await asyncio.sleep(2)  
    
    async def _safe_quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                await self.log("Браузер закрыт", logging.INFO)
            except Exception as e:
                await self.log(f"Ошибка при закрытии браузера: {e}", logging.WARNING)
            finally:
                self.driver = None
                self.is_running = False
                self._stop_requested = False
                self.current_task = None
    
    async def stop_main_process(self):
        if not self.is_running:
            await self.log("Процесс не запущен", logging.WARNING)
            return
        
        self._stop_requested = True
        await self.log("Запрошена остановка процесса...", logging.INFO)
        

        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        
        await asyncio.sleep(0.5)
    
    def stop_main_process_sync(self):
        if not self.is_running:
            return
        
        self._stop_requested = True
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.stop_main_process())
        except:
            asyncio.run(self.stop_main_process())
    
    def force_stop(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
                self.is_running = False
                self._stop_requested = False
                if self.current_task:
                    self.current_task.cancel()
                    self.current_task = None
