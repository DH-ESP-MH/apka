import logging
import os

BOT_TOKEN = "8178011882:AAGgVrr68rmXAqJpIdCthC6CojqHaTdTNI0" 
ADMIN_IDS = [7123063710]  
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