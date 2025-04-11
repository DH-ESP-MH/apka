from telebot import types
from bot_init import bot, user_states, user_carts
from keyboards import create_main_keyboard, create_categories_keyboard, create_admin_main_keyboard
from database import get_products_by_category, get_products, get_product_by_id, save_feedback
from utils.helpers import format_cart_text, format_order_summary
from handlers.cart_handlers import show_cart
from config import ADMIN_IDS, logger
from handlers.admin_handlers import handle_admin

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"Команда /start отримана від {message.from_user.id}")
    print(f"Команда /start отримана від {message.from_user.id}")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    try:
        if user_id in ADMIN_IDS:
            welcome_text = (
                f"👋 Вітаємо, адміністраторе {user_name}!\n\n"
                "Ви маєте доступ до спеціальних функцій.\n"
                "Скористайтеся /admin для керування магазином."
            )
        else:
            welcome_text = (
                f"👋 Вітаємо в боті Канцелярського магазину, {user_name}!\n\n"
                "Я допоможу вам переглянути каталог, оформити замовлення та більше."
            )
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=create_admin_main_keyboard(user_id))
        logger.info(f"Відповідь на /start відправлена користувачу {user_id}")
        print(f"Відповідь на /start відправлена користувачу {user_id}")
    except Exception as e:
        logger.error(f"Помилка при обробці /start для користувача {user_id}: {e}")
        print(f"Помилка при обробці /start для користувача {user_id}: {e}")
        bot.send_message(message.chat.id, "❌ Виникла помилка. Спробуйте ще раз або зверніться до адміністратора.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    logger.info(f"Команда /help отримана від {message.from_user.id}")
    print(f"Команда /help отримана від {message.from_user.id}")
    help_text = (
        "📋 *Доступні команди:*\n\n"
        "/start - Запустити бота\n"
        "/help - Допомога\n"
        "/info - Інформація про магазин\n"
        "/catalog - Переглянути товари\n"
        "/order - Переглянути кошик\n"
        "/feedback - Залишити відгук"
    )
    if message.from_user.id in ADMIN_IDS:
        help_text += "\n\n*Команди для адміністратора:*\n"
        help_text += "/admin - Відкрити адмін-панель\n"
        help_text += "/additem - Додати товар\n"
        help_text += "/removeitem - Видалити товар\n"
        help_text += "/orders - Переглянути замовлення\n"
        help_text += "/stats - Статистика магазину"
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    logger.info(f"Відповідь на /help відправлена користувачу {message.from_user.id}")
    print(f"Відповідь на /help відправлена користувачу {message.from_user.id}")

@bot.message_handler(commands=['info'])
def handle_info(message):
    logger.info(f"Команда /info отримана від {message.from_user.id}")
    print(f"Команда /info отримана від {message.from_user.id}")
    info_text = (
        "🏢 *Про наш магазин*\n\n"
        "Пропонуємо широкий асортимент якісної канцелярії для школи, офісу та дому.\n\n"
        "🕗 *Графік роботи:*\n"
        "Пн-Пт: 9:00 - 18:00\nСб: 10:00 - 16:00\nНд: вихідний\n\n"
        "📞 Для зв'язку скористайтеся /feedback."
    )
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')
    logger.info(f"Відповідь на /info відправлена користувачу {message.from_user.id}")
    print(f"Відповідь на /info відправлена користувачу {message.from_user.id}")

@bot.message_handler(commands=['catalog'])
def handle_catalog(message):
    logger.info(f"Команда /catalog отримана від {message.from_user.id}")
    print(f"Команда /catalog отримана від {message.from_user.id}")
    bot.send_message(message.chat.id, "📚 *Оберіть категорію товарів:*", reply_markup=create_categories_keyboard(), parse_mode='Markdown')
    logger.info(f"Відповідь на /catalog відправлена користувачу {message.from_user.id}")
    print(f"Відповідь на /catalog відправлена користувачу {message.from_user.id}")

@bot.message_handler(commands=['order'])
def handle_order_command(message):
    logger.info(f"Команда /order отримана від {message.from_user.id}")
    print(f"Команда /order отримана від {message.from_user.id}")
    user_id = message.from_user.id
    show_cart(message.chat.id, user_id)
    logger.info(f"Відповідь на /order відправлена користувачу {user_id}")
    print(f"Відповідь на /order відправлена користувачу {user_id}")

@bot.message_handler(commands=['feedback'])
def handle_feedback(message):
    logger.info(f"Команда /feedback отримана від {message.from_user.id}")
    print(f"Команда /feedback отримана від {message.from_user.id}")
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_for_feedback'
    bot.send_message(message.chat.id, "📝 Будь ласка, залиште ваш відгук або питання. Ми цінуємо вашу думку!")
    logger.info(f"Відповідь на /feedback відправлена користувачу {user_id}")
    print(f"Відповідь на /feedback відправлена користувачу {user_id}")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id] == 'waiting_for_feedback')
def handle_feedback_message(message):
    logger.info(f"Отримано відгук від {message.from_user.id}")
    print(f"Отримано відгук від {message.from_user.id}")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    feedback_text = message.text
    save_feedback(user_id, user_name, feedback_text)
    bot.send_message(message.chat.id, "🙏 Дякуємо за ваш відгук!")
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                f"💬 *Новий відгук*\n\nВід: {user_name} (ID: {user_id})\nПовідомлення: {feedback_text}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Не вдалося повідомити адміна {admin_id}: {e}")
            print(f"Не вдалося повідомити адміна {admin_id}: {e}")
    if user_id in user_states:
        del user_states[user_id]
    logger.info(f"Відгук від {user_id} оброблено")
    print(f"Відгук від {user_id} оброблено")

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_text_buttons(message):
    user_id = message.from_user.id
    text = message.text.lower()
    
    logger.info(f"Отримано текстове повідомлення від {user_id}: {text}")
    print(f"Отримано текстове повідомлення від {user_id}: {text}")
    
    if any(keyword in text for keyword in ['Каталог', 'каталог']):
        handle_catalog(message)
    elif any(keyword in text for keyword in ['Допомога', 'допомога','help']):
        handle_help(message)
    elif any(keyword in text for keyword in ['Інформація', 'інформація','інфа']):
        handle_info(message)
    elif any(keyword in text for keyword in ['Кошик', 'кошик']):
        handle_order_command(message)
    elif message.text == '👑 Адмінпанель' and user_id in ADMIN_IDS:
        handle_admin(message)
    elif any(keyword in text for keyword in ['hello', 'hi', 'hey', 'привіт', 'Привіт']):
        bot.send_message(
            message.chat.id,
            f"👋 Привіт, {message.from_user.first_name}! Чим можу допомогти?"
        )
    elif any(keyword in text for keyword in ['price', 'cost', 'how much', 'ціна', 'вартість']):
        bot.send_message(
            message.chat.id,
            "📊 Ви можете переглянути наші ціни в каталозі. Використайте команду /catalog."
        )
    elif any(keyword in text for keyword in ['delivery', 'shipping', 'доставка']):
        bot.send_message(
            message.chat.id,
            "🚚 Ми пропонуємо доставку за будь-якою адресою у місті. Деталі доставки обговорюються після оформлення замовлення."
        )
    elif any(keyword in text for keyword in ['payment', 'pay', 'оплата']):
        bot.send_message(
            message.chat.id,
            "💳 Ми приймаємо різні способи оплати, включаючи кредитні/дебетові картки та накладений платіж."
        )
    elif any(keyword in text for keyword in ['thanks', 'thank you', 'дякую']):
        bot.send_message(
            message.chat.id,
            "☺️ Будь ласка! Ознайомтесь з нашим каталогом або звертайтесь, якщо є запитання."
        )
    else:
        bot.send_message(
            message.chat.id,
            "Не розумію вашого запитання. Спробуйте скористатись кнопками або введіть /help для перегляду доступних команд."
        )
    logger.info(f"Відповідь на текстове повідомлення відправлена користувачу {user_id}")
    print(f"Відповідь на текстове повідомлення відправлена користувачу {user_id}")