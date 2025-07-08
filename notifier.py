import telebot
import accounts_container
import config
from telebot.types import Message

from parser import PayloniumParser


bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


def send_notification(user_id: int, order_data: dict):
    """Форматирует и отправляет сообщение в Telegram."""
    message = (
        f"Новая заявка\n\n"
        f"<b>Кабинет:</b> {order_data['account_name']}\n"
        f"<b>Дата и время:</b> {order_data['datetime']}\n"
        f"<b>Банк:</b> {order_data['bank']}\n"
        f"<b>Сумма:</b> {order_data['amount']:,} RUB".replace(",", " ")
    )
    try:
        bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        print(f"Уведомление отправлено пользователю {user_id}")
    except Exception as e:
        print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")


@bot.message_handler(commands=["start"])
def send_welcome(message: Message):
    valid_sessions = {
        acc._login: acc.check_session()
        for acc in accounts_container.accounts
        if acc.telegram_id == message.chat.id
    }
    res_message = f"Бот для мониторинга PayLonium активен. Ваш ID: {message.chat.id}\n"
    for item in valid_sessions.items():
        acc_name, valid = item
        res_message += f"{acc_name}: {"🟢" if valid else "🔴"}\n"
    bot.reply_to(message, res_message)


def start_bot_polling():
    """Запускает polling бота в отдельном потоке, чтобы не блокировать основной цикл."""
    import threading

    t = threading.Thread(target=bot.polling, kwargs={"none_stop": True})
    t.daemon = True
    t.start()
    print("Telegram бот запущен в фоновом режиме.")
