import functools
import os
import pickle
import time
from typing import List
import requests
from bs4 import BeautifulSoup
from collections import namedtuple
import re

from sqlalchemy import true

import config

# URL для входа и для получения заявок
LOGIN_URL = "https://profile.paylonium.com/login"
GET_ORDERS_URL = "https://profile.paylonium.com/p/getnew?serviceId=24"

ParsedOrder = namedtuple(
    "ParsedOrder", ["paylonium_id", "datetime", "bank", "amount", "recipient_details"]
)


class PayloniumParser:
    def __init__(self, login, password, account_name, telegram_id):
        self._login = login
        self._password = password
        self.account_name = account_name
        self.telegram_id = telegram_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "DNT": "1",
                "Host": "profile.paylonium.com",
                "Origin": "https://profile.paylonium.com",
                "Pragma": "no-cache",
                "Referer": "https://profile.paylonium.com/p/getnew",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "TE": "trailers",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            }
        )
        self._is_authenticated = False

    def parse_auth_data(self, response: requests.Response):
        """Парсит ответ запроса авторизации

        Args:
            auth_data (str): HTML страничка ответа

        Raises:
            Exception: Возвращает базовый Exception с текстом "Неверное имя/пароль"

        Returns:
            bool: Возвращает True если все хорошо, и выкидывает исключение если все плохо
        """
        soup = BeautifulSoup(response, "lxml")
        alert = soup.find("div", class_="alert callout")
        if alert and alert.getText().strip() == "Неверное имя/пароль":
            raise Exception("Неверное имя/пароль")
        else:
            return True

    def authenticate(self):
        """Выполняет вход в систему и сохраняет сессию."""
        if self.load_session():
            return

        print(f"Выполняю авторизацию для {self._login}")
        login_data = {
            "username": self._login,
            "password": self._password,
        }

        response = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        response.raise_for_status()  # Если статус не 200 кидает HTTPError
        self.parse_auth_data(
            response.content
        )  # Если в контенте страницы есть ошибка выкидывает Exception
        self._is_authenticated = True
        self.save_session()

    def autentification_required(func):
        """Декоратор проверки авторизации

        Args:
            func (function): Принимает функцию для которой необходима авторизация перед использованием

        Raises:
            Exception: Возвращает базовый Exception с текстом "Autentification required"

        Returns:
            function: Вызов исходной функции если авторизация есть
        """

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._is_authenticated:
                raise Exception("Autentification required")
            else:
                return func(self, *args, **kwargs)

        return wrapper

    def safe_filename(self, name: str) -> str:
        """Удаляет опасные символы из имени файла"""
        return re.sub(r"[^A-Za-z0-9_.-]", "_", name)

    def save_session(self):
        """Сохранение сессии"""
        with open(
            os.path.join(
                config.SESSIONS_PATH, f"{self.safe_filename(self.account_name)}.pkl"
            ),
            "wb",
        ) as f:
            pickle.dump(self.session.cookies, f)

    def load_session(self):
        """Загрузка сессии

        Returns:
            bool: True если успех, False - если провал
        """
        try:
            with open(
                os.path.join(
                    config.SESSIONS_PATH, f"{self.safe_filename(self.account_name)}.pkl"
                ),
                "rb",
            ) as f:
                cookies = pickle.load(f)
                self.session.cookies.update(cookies)
                if self.check_session():
                    print(f"Сессия для {self._login} успешно загружена")
                    self._is_authenticated = True
                    return True

        except FileNotFoundError:
            return False
        print(f"Сессия для {self._login} не валидна")
        return False

    def check_session(self):
        response = self.session.get(GET_ORDERS_URL, allow_redirects=False)
        response.raise_for_status()
        if response.status_code == 200 and "login" not in response.url:
            return True
        return False

    def _parse_orders_data(self, data: str):
        soup = BeautifulSoup(data, "lxml")
        orders = []

        order_rows = (
            soup.find("table", {"class": "report_table p2p_new"})
            .find("tbody")
            .find_all("tr")
        )

        for row in order_rows:
            cols = row.find_all("td")
            if not cols:
                continue
            print(cols)
            pl_id = cols[0].text.strip()
            dt_str = cols[1].text.strip()  # '2025-06-06 18:11:16'
            bank_img = cols[2].find("img")
            bank = bank_img["alt"].strip() if bank_img else cols[2].text.strip()
            amount_str = cols[3].text.replace(",", ".")
            amount = float(amount_str)
            recipient = cols[4].text.strip()

            orders.append(
                ParsedOrder(
                    paylonium_id=pl_id,
                    datetime=dt_str,
                    bank=bank,
                    amount=amount,
                    recipient_details=recipient,
                )
            )
        return orders

    @autentification_required
    def get_new_orders(self) -> List[ParsedOrder]:
        """Получает новые заявки с сайта

        Returns:
            List[ParsedOrder]: Список заявок
        """
        try:
            response = self.session.get(GET_ORDERS_URL)
            response.raise_for_status()
            if "login" in response.url:
                print("Сессия истекла. Повторная аутентификация...")
                self._is_authenticated = False
                self.authenticate()
                response = self.session.get(GET_ORDERS_URL)  # Повторный запрос
            data = response.text
            # with open("test.html", "r", encoding='utf-8') as f:
            #     data = f.read()

            return self._parse_orders_data(data=data)  # Заменить на норм данные

        except requests.RequestException as e:
            print(f"Ошибка сети при получении заявок: {e}")
            return []
        except Exception as e:
            print(f"Ошибка парсинга страницы: {e}")
            with open(f"debug_{time.time()}.html", "w", encoding="utf-8") as f:
                f.write(response.text)  # Сохраним соддержимое страницы для отладки
            return []
