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
ACCOUNTS_FILE="accounts.json"
CHECK_INTERVAL_SECONDS=10
GET_ORDERS_URL="https://profile.paylonium.com/p/getnew"
```

3. Создание файла конфигурационного файла для аккаунтов

```
Скопируйте файл accounts_example.json, переименуйте его в accounts.json и отредактируйте данные внутри
```

4. Запуск бота

```bash
python main.py
```

🛡️ Безопасность

    🔑 Все секреты хранятся в .env

    💾 Сессии сохраняются в ./sessions/ в виде pickle-файлов

    🧠 Повторные заявки не отправляются
