from config import logger
from database import init_db
from bot_init import bot, init_bot_data

init_db()
init_bot_data()

import handlers.user_handlers
import handlers.admin_handlers
import handlers.cart_handlers
import handlers.callback_handlers

def main():
    logger.info("Запуск бота...")
    print("Запуск бота...")  
    try:
        bot.polling(none_stop=True, interval=0)
        logger.info("bot.polling() завершився")
        print("bot.polling() завершився")
    except Exception as e:
        logger.error(f"Помилка в головному циклі: {e}")
        print(f"Помилка в головному циклі: {e}")
    finally:
        logger.info("Програма завершує роботу")
        print("Програма завершує роботу")

if __name__ == "__main__":
    main()