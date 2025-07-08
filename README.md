# 📡 Paylonium Order Watcher Bot

Бот для отслеживания новых заявок в системе **Paylonium** и отправки уведомлений в Telegram.

---

## ⚙️ Возможности

- 🔐 Авторизация по логину и паролю
- 🔁 Периодический опрос страницы `/p/getnew`
- 📥 Парсинг ID, даты, банка, суммы, получателя и назначения
- 💾 Сохранение уникальных заявок в SQLite
- 📲 Telegram-уведомления о новых заявках
- 🧠 Исключение повторной отправки

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

2. Создание .env файла

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URI=sqlite:///orders.db
CHECK_INTERVAL_SECONDS=10
ACCOUNTS=[{"account_name": "Test", "paylonium_login": "your_login", "paylonium_password": "your_password", "telegram_user_id": 123456789}]
```

3. Запуск бота

```bash
python main.py
```

🛡️ Безопасность

    🔑 Все секреты хранятся в .env

    💾 Сессии сохраняются в ./sessions/ в виде pickle-файлов

    🧠 Повторные заявки не отправляются
