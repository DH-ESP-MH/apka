import telebot
from telebot import types
from config import BOT_TOKEN, logger

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}
user_carts = {}

def init_bot_data():
    logger.info("Ініціалізація даних бота...")
    print("Ініціалізація даних бота...")  # Додаємо вивід у консоль
    user_states.clear()
    user_carts.clear()
    try:
        bot_info = bot.get_me()
        logger.info(f"Бот успішно ініціалізований. Ім'я бота: {bot_info.username}")
        print(f"Бот успішно ініціалізований. Ім'я бота: {bot_info.username}")
    except Exception as e:
        logger.error(f"Помилка при ініціалізації бота: {e}")
        print(f"Помилка при ініціалізації бота: {e}")
        raise