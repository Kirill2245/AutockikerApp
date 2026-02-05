import tkinter as tk
from tkinter import scrolledtext, Toplevel
import logging

class ModalInfo:
    def __init__(self, parent):
        self.parent = parent
        self.info_window = None  # Переименовал для ясности
        
    def open_windowinfo(self):  # Исправил имя метода (было open_window_info)
        # Создаем окно для информации
        self.info_window = Toplevel(self.parent)
        self.info_window.title("Информация")
        self.info_window.geometry("600x700")
        self.info_window.configure(bg="#1E2B3E")
        self.info_window.resizable(False, False)
        
        # Центрируем окно
        self.info_window.transient(self.parent)
        self.info_window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает виджеты окна информации"""
        # Заголовок
        title_label = tk.Label(
            self.info_window,  # Исправил: было self.feedback_window
            text="Информация о приложении",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1E2B3E"
        )
        title_label.pack(pady=15)
        
        # Основной текст информации
        info_frame = tk.Frame(self.info_window, bg="#1E2B3E")  # Исправил здесь тоже
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Текстовая область с информацией
        info_text = scrolledtext.ScrolledText(
            info_frame,
            wrap=tk.WORD,
            width=50,
            height=15,
            bg="#2D4A5D",
            fg="white",
            insertbackground="white",
            font=("Arial", 10),
            relief="flat"
        )
        info_text.pack(fill="both", expand=True, pady=5)
        
        # Заполняем информацией
        info_content = """
**Краткая инструкция по использованию**

1. Основные шаги:
*   Вставьте URL сайта в верхнее поле.
*   Нажмите кнопку «Запуск».

2. Дополнительные настройки:
*   Таймаут (сек): Задержка между действиями для стабильности. Не убирайте и не ставьте в `0`.
*   Кол-во повторов: Сколько раз программа попытается кликнуть, если элемент не найден.
*   Классы элементов: Можно указать свои HTML-классы для кликов и модальных окон (найти их через F12).
*   **Использовать Firefox**: Поставьте галочку для работы с Firefox (по умолчанию используется Chrome).
*   Автоперезагрузка страницы: Включите для автоматической перезагрузки через заданный интервал.

3. Telegram уведомления:
*   Настройте Telegram API для получения уведомлений.
*   Нажмите кнопку «Telegram» в нижней части окна для настройки.

4. Консоль:
*   Следите за процессом и ошибками в консоли внутри программы.
*   Используйте команду `tg status` для проверки статуса Telegram подключения.
*   Используйте команду `tg send [текст]` для отправки сообщений в Telegram.

---

**Как получить API ID и API Hash для Telegram:**

1. Перейдите на сайт https://my.telegram.org
2. Войдите под своим номером телефона Telegram
3. Перейдите в раздел "API Development Tools"
4. Заполните форму:
   - App title: KLIK KLAK (или любое другое название)
   - Short name: klikklak
   - URL: можно оставить пустым или указать свой сайт
   - Platform: Desktop
5. Нажмите "Create application"
6. Сохраните полученные данные:
   - **api_id** - цифровой идентификатор (например: 27633732)
   - **api_hash** - строковый ключ (например: cbb393370515e64097ea2fehad5455e8)
7. Введите эти данные в настройках Telegram в программе

---

**Важные правила и советы**
*   После бетта-тестов у каждого будет свой логин и пароль, нельзя делиться им с другими , а так же использовать прогу на нескольких устройствах , если вы хотите сменить свое устройство на другое , напишите нам . В противном случае выдаем бан аккаунту . 
    **Chrome должен быть версии не меньше 142.0.7444.177, Firefox - Используйте актуальную версию браузера.** 

*   Аккаунт: Не передавайте свой логин и пароль другим. Одно устройство на аккаунт.
*   Браузеры: Используйте актуальные версии Google Chrome или Mozilla Firefox.
*   Проблемы: При ошибках присылайте скриншоты окна программы и консоли.
*   Обновления: Программа будет периодически обновляться и улучшаться.
*   Telegram: Настройте Telegram API для получения важных уведомлений о работе программы.

---

**Полезные функции:**
*   Сохранение конфигурации: Нажмите правой кнопкой мыши на кнопке "Сохранить и Запустить" для сохранения настроек без запуска.
*   История логов: Все действия сохраняются в консоли, можно копировать текст.
*   Обратная связь: Используйте кнопку "Сообщить об ошибке" для связи с разработчиками.
*   Информация: Кнопка "Информация" содержит эту инструкцию и справочные данные.

---

P.S. Так же если есть пожелания по улучшении ПО или проблемы по ПО, пишите в **Обратную связь**.
"""

        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)  # Делаем только для чтения
        
        # Кнопка закрытия
        button_frame = tk.Frame(self.info_window, bg="#1E2B3E")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        close_btn = tk.Button(
            button_frame,
            text="Закрыть",
            command=self.info_window.destroy,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            relief="flat"
        )
        close_btn.pack(pady=10)