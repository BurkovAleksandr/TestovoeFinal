import telebot
import config
from telebot.types import Message

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
    bot.reply_to(
        message, f"Бот для мониторинга PayLonium активен. Ваш ID: {message.chat.id}"
    )


def start_bot_polling():
    """Запускает polling бота в отдельном потоке, чтобы не блокировать основной цикл."""
    import threading

    t = threading.Thread(target=bot.polling, kwargs={"none_stop": True})
    t.daemon = True
    t.start()
    print("Telegram бот запущен в фоновом режиме.")
