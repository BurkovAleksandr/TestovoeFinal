import time
from typing import List
import schedule
import accounts_container
from database import SessionLocal, init_db, add_order, order_exists
from parser import ParsedOrder, PayloniumParser
from notifier import send_notification, start_bot_polling
import config


def account_fabric():
    """Возвращает список с парсерами"""
    parsers_list = []
    for account in config.ACCOUNTS:
        print(f"--- Проверяю аккаунт: {account['account_name']} ---")

        # Для каждого аккаунта создаем свой экземпляр парсера
        parser = PayloniumParser(
            login=account["paylonium_login"],
            password=account["paylonium_password"],
            telegram_id=account["telegram_user_id"],
            account_name=account["account_name"],
        )
        parser.authenticate()
        parsers_list.append(parser)
    return parsers_list


def check_for_new_orders(accounts: List[PayloniumParser]):
    """Основная функция, выполняющая проверку для всех аккаунтов."""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Запускаю проверку...")
    db_session = SessionLocal()
    for parser in accounts:
        print(f"--- Проверяю аккаунт: {parser._login} ---")
        
        # Получаем список заявок
        new_orders: list[ParsedOrder] = parser.get_new_orders()

        if not new_orders:
            print("Новых заявок не найдено.")
            continue

        print(f"Найдено {len(new_orders)} заявок на странице. Проверяю с БД...")
        for order in new_orders:

            if not order_exists(db_session, order.paylonium_id):
                print(f"НАЙДЕНА НОВАЯ ЗАЯВКА: ID {order.paylonium_id}")

                order_data_for_db_and_tg = {
                    "account_name": parser._login,
                    "datetime": order.datetime,
                    "bank": order.bank,
                    "amount": order.amount,
                    "recipient_details": order.recipient_details,
                    "paylonium_id": order.paylonium_id,
                }

                # Сохраняем в БД
                add_order(db_session, order_data_for_db_and_tg)

                # Отправляем уведомление в Telegram
                send_notification(parser.telegram_id, order_data_for_db_and_tg)

    db_session.close()


if __name__ == "__main__":
    print("Инициализация...")
    init_db()  # Создаем таблицы в бд
    accounts_container.accounts = account_fabric()
    start_bot_polling()  # Запускаем бота в отдельном потоке

    schedule.every(config.CHECK_INTERVAL_SECONDS).seconds.do(
        check_for_new_orders, accounts=accounts_container.accounts
    )  # Создаем планировщика

    print(
        f"Планировщик настроен. Первая проверка начнется через {config.CHECK_INTERVAL_SECONDS} секунд..."
    )
    while True:
        schedule.run_pending()  # Запускаем планировщика
        time.sleep(1)
