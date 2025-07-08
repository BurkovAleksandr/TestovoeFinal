import json
import os

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URI = os.getenv(
    "DATABASE_URI"
) 
# Интервал проверки новых заявок в секундах
CHECK_INTERVAL_SECONDS = 10
SESSIONS_PATH = "./sessions/"
# Список аккаунтов для мониторинга
# ACCOUNTS = [
#     {
#         "account_name": "Test",  # Имя для отображения в уведомлениях и БД
#         "paylonium_login": "testlogin",
#         "paylonium_password": "testpass",
#         "telegram_user_id": 12345674,  # ID пользователя в Telegram, куда слать уведомления
#     },
# ] ПРИМЕР ПЕРЕМЕННОЙ ОКРУЖЕНИЯ
ACCOUNTS = json.loads(os.getenv("ACCOUNTS"))
