import logging
import os
import json  # Для обробки списку ADMIN_IDS

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS")
ADMIN_IDS = json.loads(ADMIN_IDS_STR) if ADMIN_IDS_STR else []
DB_PATH = "stationery_shop.db"

logger = logging.getLogger('StationeryBot')
logger.setLevel(logging.INFO)

log_handler = logging.FileHandler('bot_log.log')
log_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s (%(name)s) %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Перевірка наявності токена
if not BOT_TOKEN:
    logger.error("Змінна середовища BOT_TOKEN не встановлена!")
    exit()

logger.info(f"Бот запущено з ID адміністраторів: {ADMIN_IDS}")
