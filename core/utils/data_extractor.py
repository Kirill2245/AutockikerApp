from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import re

class DataExtractor:
    def __init__(self, driver=None):
        self.driver = driver
        
    def extract_payment_data(self, context=None, timeout=5):
        """
        Извлекает полные данные платежа из строки таблицы.
        Включает: данные клиента, сумму, курс, ID транзакции.
        """
        try:
            # Определяем контекст для поиска
            search_context = self._get_search_context(context)
            if not search_context:
                print("❌ Контекст для поиска не определен")
                return None
            
            # Инициализируем результат
            result = {
                # Данные клиента (из 4-й ячейки)
                'name': None,
                'organization': None,
                'bank': None,
                'phone': None,
                'email': None,
                # Финансовые данные
                'amount': None,           # 10 000 ₽ (из 3-й ячейки)
                'amount_currency': '₽',
                'exchange_rate': None,    # 76,94335 ₽ (из 2-й ячейки)
                'exchange_currency': '₽',
                'usdt_amount': None,      # 129,96574 USD₮ (из 3-й ячейки)
                'usdt_currency': 'USD₮',
                # Техническая информация (из 1-й ячейки)
                'transaction_id': None,
                'date': None,
                # Дополнительно
                'additional_info': None,
                'raw_text': None
            }
            
            # Если контекст - строка таблицы
            if search_context.tag_name.lower() == 'tr':
                result.update(self._extract_from_table_row(search_context))
            else:
                # Ищем в переданном элементе
                result.update(self._extract_from_element(search_context))
            
            # Очищаем результат от None значений
            cleaned_result = {k: v for k, v in result.items() if v is not None}
            
            if cleaned_result:
                return cleaned_result
            return None
            
        except Exception as e:
            print(f"Ошибка при извлечении данных: {e}")
            return None
    
    def _get_search_context(self, context):
        """
        Определяет контекст для поиска элементов.
        """
        if context is None:
            return self.driver
        elif isinstance(context, WebElement):
            return context
        elif isinstance(context, str):
            # Если передали CSS селектор
            try:
                return self.driver.find_element(By.CSS_SELECTOR, context)
            except:
                return None
        else:
            return None
    
    def _extract_from_table_row(self, row):
        """
        Извлекает данные из строки таблицы.
        """
        result = {}
        
        try:
            # Получаем все ячейки строки
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 4:
                # 1. Извлекаем данные из 1-й ячейки (ID транзакции и дата)
                result.update(self._extract_transaction_data(cells[0]))
                
                # 2. Извлекаем данные из 2-й ячейки (курс)
                result.update(self._extract_exchange_rate(cells[1]))
                
                # 3. Извлекаем данные из 3-й ячейки (сумма и USDT)
                result.update(self._extract_amount_data(cells[2]))
                
                # 4. Извлекаем данные из 4-й ячейки (данные клиента)
                result.update(self._extract_client_data(cells[3]))
            
            return result
            
        except Exception as e:
            print(f"Ошибка при извлечении из строки таблицы: {e}")
            return result
    
    def _extract_transaction_data(self, cell):
        """
        Извлекает ID транзакции и дату из 1-й ячейки.
        """
        result = {}
        
        try:
            # ID транзакции
            try:
                id_element = cell.find_element(By.CSS_SELECTOR, "p.MuiTypography-body1.css-cocz22")
                if id_element and id_element.text:
                    result['transaction_id'] = id_element.text.strip()
            except:
                pass
            
            # Дата
            try:
                date_element = cell.find_element(By.CSS_SELECTOR, "div.css-v9bpfw")
                if date_element and date_element.text:
                    result['date'] = date_element.text.strip()
            except:
                pass
            
        except Exception as e:
            print(f"Ошибка при извлечении данных транзакции: {e}")
        
        return result
    
    def _extract_exchange_rate(self, cell):
        """
        Извлекает курс из 2-й ячейки.
        Пример: "76,94335 ₽"
        """
        result = {}
        
        try:
            text = cell.text.strip()
            if text:
                # Ищем число с запятой как разделителем десятичных
                match = re.search(r'([\d,]+)\s*₽', text)
                if match:
                    # Заменяем запятую на точку для числового значения
                    rate = match.group(1).replace(',', '.')
                    try:
                        result['exchange_rate'] = float(rate)
                        result['exchange_currency'] = '₽'
                    except:
                        result['exchange_rate'] = rate
                        result['exchange_currency'] = '₽'
        
        except Exception as e:
            print(f"Ошибка при извлечении курса: {e}")
        
        return result
    
    def _extract_amount_data(self, cell):
        """
        Извлекает сумму и USDT из 3-й ячейки.
        Содержит: "10 000 ₽" и "129,96574 USD₮"
        """
        result = {}
        
        try:
            text = cell.text.strip()
            if text:
                # Ищем сумму в рублях
                rub_match = re.search(r'([\d\s]+)\s*₽', text)
                if rub_match:
                    amount_str = rub_match.group(1).replace(' ', '').replace('\xa0', '')
                    try:
                        result['amount'] = float(amount_str)
                        result['amount_currency'] = '₽'
                    except:
                        result['amount'] = amount_str
                        result['amount_currency'] = '₽'
                
                # Ищем сумму в USDT
                usdt_match = re.search(r'([\d,]+)\s*USD₮', text)
                if usdt_match:
                    usdt_str = usdt_match.group(1).replace(',', '.')
                    try:
                        result['usdt_amount'] = float(usdt_str)
                        result['usdt_currency'] = 'USD₮'
                    except:
                        result['usdt_amount'] = usdt_str
                        result['usdt_currency'] = 'USD₮'
        
        except Exception as e:
            print(f"Ошибка при извлечении суммы: {e}")
        
        return result
    
    def _extract_client_data(self, cell):
        """
        Извлекает данные клиента из 4-й ячейки.
        """
        result = {}
        
        try:
            # Ищем контейнер с данными клиента
            container = cell.find_element(By.CSS_SELECTOR, "div.tw-flex.tw-flex-col")
            
            if container:
                # Имя
                try:
                    name_elem = container.find_element(By.CSS_SELECTOR, "span.tw-text-sm.tw-font-semibold")
                    if name_elem and name_elem.text:
                        result['name'] = name_elem.text.strip()
                except:
                    pass
                
                # Организация (СБП)
                try:
                    spans = container.find_elements(By.TAG_NAME, "span")
                    for span in spans:
                        text = span.text.strip()
                        if text in ['СБП', 'СБ']:
                            result['organization'] = text
                            break
                except:
                    pass
                
                # Банк
                try:
                    bank_elem = container.find_element(By.CSS_SELECTOR, "span.css-1ezgv1")
                    if bank_elem and bank_elem.text:
                        result['bank'] = bank_elem.text.strip()
                except:
                    pass
                
                # Телефон
                try:
                    # Ищем все элементы с телефонами
                    phone_elements = container.find_elements(By.CSS_SELECTOR, "p.MuiTypography-body1.css-sb14iu")
                    for elem in phone_elements:
                        text = elem.text.strip()
                        if text and text.startswith('+') and any(c.isdigit() for c in text[1:]):
                            result['phone'] = text
                            break
                except:
                    pass
                
                # Email
                try:
                    email_elements = container.find_elements(By.CSS_SELECTOR, "p.MuiTypography-body1.css-sb14iu")
                    for elem in email_elements:
                        text = elem.text.strip()
                        if text and '@' in text:
                            result['email'] = text
                            break
                except:
                    pass
                
                # Дополнительная информация (дублированное имя в последнем div)
                try:
                    last_div = container.find_elements(By.TAG_NAME, "div")[-1]
                    if last_div:
                        text = last_div.text.strip()
                        if text and text != result.get('name'):
                            result['additional_info'] = text
                except:
                    pass
        
        except NoSuchElementException:
            # Если нет контейнера, пытаемся извлечь из текста ячейки
            text = cell.text.strip()
            if text:
                result['raw_text'] = text
        except Exception as e:
            print(f"Ошибка при извлечении данных клиента: {e}")
        
        return result
    
    def _extract_from_element(self, element):
        """
        Извлекает данные из произвольного элемента.
        """
        result = {}
        
        try:
            if "tw-flex tw-flex-col" in element.get_attribute("class") or \
               element.find_elements(By.CSS_SELECTOR, "div.tw-flex.tw-flex-col"):
                
                result.update(self._extract_client_data(element))
            
            elif "MuiTableCell-body" in element.get_attribute("class"):
                text = element.text.strip()
                if '₽' in text and 'USD₮' not in text:
                    # Вероятно, это курс
                    result.update(self._extract_exchange_rate(element))
                elif '₽' in text or 'USD₮' in text:
                    # Вероятно, это сумма
                    result.update(self._extract_amount_data(element))
            
            return result
            
        except Exception as e:
            print(f"Ошибка при извлечении из элемента: {e}")
            return result
    
    def extract_payment_data_simple(self, row):
        try:
            data = self.extract_payment_data(context=row)
            if data:
                # Форматируем результат для вывода
                return {
                    'Клиент': data.get('name'),
                    'Телефон': data.get('phone'),
                    'Email': data.get('email'),
                    'Банк': data.get('bank'),
                    'Сумма': f"{data.get('amount', '')} {data.get('amount_currency', '')}",
                    'Курс': f"{data.get('exchange_rate', '')} {data.get('exchange_currency', '')}",
                    'USDT': f"{data.get('usdt_amount', '')} {data.get('usdt_currency', '')}",
                    'ID': data.get('transaction_id'),
                    'Дата': data.get('date')
                }
            return None
        except Exception as e:
            print(f"Ошибка в упрощенном методе: {e}")
            return None