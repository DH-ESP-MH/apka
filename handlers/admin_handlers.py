from telebot import types
from bot_init import bot, user_states
from config import ADMIN_IDS, logger
from database import get_products, get_product_by_id, add_product, remove_product, get_orders
from keyboards import (
    create_admin_keyboard,
    create_product_categories_admin_keyboard,
    create_admin_confirm_keyboard
)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Доступ заборонено")
        return
        
    admin_text = (
        "👑 *АДМІНІСТРАТОРСЬКА ПАНЕЛЬ*\n\n"
        "▫️ /additem - Додати товар\n"
        "▫️ /removeitem - Видалити товар\n"
        "▫️ /orders - Переглянути замовлення\n"
        "▫️ /stats - Статистика магазину"
    )
    
    bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', 
                   reply_markup=create_admin_keyboard())

@bot.message_handler(commands=['additem'])
def handle_add_item_command(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Доступ заборонено.")
        return
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id] = 'admin_adding_product_name'
    bot.send_message(message.chat.id, "🏷️ Введіть назву товару:")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_adding_product_name')
def handle_add_product_name(message):
    user_id = message.from_user.id
    name = message.text
    if 'admin_product_info' not in user_states:
        user_states['admin_product_info'] = {}
    user_states['admin_product_info'][user_id] = {'name': name}
    user_states[user_id] = 'admin_adding_product_category'
    bot.send_message(message.chat.id, "📂 Оберіть категорію товару:", reply_markup=create_product_categories_admin_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_category_'))
def handle_add_product_category(call):
    user_id = call.from_user.id
    category_idx = int(call.data.split('_')[2])  # Отримуємо індекс категорії
    categories = ["Письмове приладдя", "Паперові вироби", "Офісне приладдя", "Шкільне канцелярське приладдя"]
    
    if category_idx < 0 or category_idx >= len(categories):
        bot.send_message(call.message.chat.id, "❌ Некоректна категорія.")
        bot.answer_callback_query(call.id)
        return
    
    category = categories[category_idx]
    user_states['admin_product_info'][user_id]['category'] = category
    user_states[user_id] = 'admin_adding_product_description'
    bot.send_message(call.message.chat.id, "📝 Введіть опис товару:")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_adding_product_description')
def handle_add_product_description(message):
    user_id = message.from_user.id
    user_states['admin_product_info'][user_id]['description'] = message.text
    user_states[user_id] = 'admin_adding_product_price'
    bot.send_message(message.chat.id, "💰 Введіть ціну товару (наприклад, 10.99):")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id] == 'admin_adding_product_price')
def handle_add_product_price(message):
    user_id = message.from_user.id
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError("Ціна має бути додатною")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Некоректна ціна. Спробуйте ще раз:")
        return
    user_states['admin_product_info'][user_id]['price'] = price
    product = user_states['admin_product_info'][user_id]
    text = (
        f"📋 *Інформація про товар:*\n\n"
        f"*Назва:* {product['name']}\n"
        f"*Категорія:* {product['category']}\n"
        f"*Опис:* {product['description']}\n"
        f"*Ціна:* ${product['price']:.2f}\n\n"
        f"Додати цей товар до каталогу?"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=create_admin_confirm_keyboard())
    user_states[user_id] = 'admin_confirming_product'

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_product")
def handle_admin_add_product(call):
    try:
        user_id = call.from_user.id
        if user_id not in ADMIN_IDS:
            bot.send_message(call.message.chat.id, "⛔ Доступ заборонено.")
            bot.answer_callback_query(call.id)
            return
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id] = 'admin_adding_product_name'
        bot.send_message(call.message.chat.id, "🏷️ Введіть назву товару (або /cancel, щоб скасувати):")
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Помилка в handle_admin_add_product: {e}")
        bot.send_message(call.message.chat.id, "❌ Виникла помилка. Спробуйте ще раз.")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_product")
def handle_admin_remove_product(call):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(call.message.chat.id, "⛔ Доступ заборонено.")
        bot.answer_callback_query(call.id)
        return
    products = get_products()
    if not products:
        bot.send_message(call.message.chat.id, "Каталог порожній.")
        bot.answer_callback_query(call.id)
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for product in products:
        product_id, name, category, _, price = product
        markup.add(types.InlineKeyboardButton(f"{name} - ${price:.2f}", callback_data=f"admin_remove_{product_id}"))
    markup.add(types.InlineKeyboardButton("❌ Скасувати", callback_data="admin_cancel_remove"))
    bot.send_message(call.message.chat.id, "🗑️ Оберіть товар для видалення:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_confirm_add_product")
def handle_confirm_add_product(call):
    try:
        user_id = call.from_user.id
        if 'admin_product_info' not in user_states or user_id not in user_states['admin_product_info']:
            bot.send_message(call.message.chat.id, "❌ Дані про товар відсутні. Спробуйте ще раз.")
            bot.answer_callback_query(call.id)
            return
        product = user_states['admin_product_info'][user_id]
        add_product(product['name'], product['category'], product['description'], product['price'])
        bot.send_message(call.message.chat.id, f"✅ Товар '{product['name']}' додано до каталогу.")
        if 'admin_product_info' in user_states and user_id in user_states['admin_product_info']:
            del user_states['admin_product_info'][user_id]
        if user_id in user_states:
            del user_states[user_id]
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Помилка в handle_confirm_add_product: {e}")
        bot.send_message(call.message.chat.id, "❌ Виникла помилка. Спробуйте ще раз.")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_cancel_add_product")
def handle_cancel_add_product(call):
    user_id = call.from_user.id
    if 'admin_product_info' in user_states and user_id in user_states['admin_product_info']:
        del user_states['admin_product_info'][user_id]
    if user_id in user_states:
        del user_states[user_id]
    bot.send_message(call.message.chat.id, "❌ Додавання товару скасовано.")
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['removeitem'])
def handle_remove_item_command(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Доступ заборонено.")
        return
    products = get_products()
    if not products:
        bot.send_message(message.chat.id, "Каталог порожній.")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for product in products:
        product_id, name, category, _, price = product
        markup.add(types.InlineKeyboardButton(f"{name} - ${price:.2f}", callback_data=f"admin_remove_{product_id}"))
    markup.add(types.InlineKeyboardButton("❌ Скасувати", callback_data="admin_cancel_remove"))
    bot.send_message(message.chat.id, "🗑️ Оберіть товар для видалення:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_remove_') and call.data != 'admin_remove_product')
def handle_remove_product_selection(call):
    try:
        product_id = int(call.data.split('_')[2])
    except (IndexError, ValueError):
        bot.send_message(call.message.chat.id, "❌ Некоректний формат ID товару.")
        bot.answer_callback_query(call.id)
        return
    product = get_product_by_id(product_id)
    if not product:
        bot.send_message(call.message.chat.id, "❌ Товар не знайдено.")
        bot.answer_callback_query(call.id)
        return
    product_id, name, category, _, price = product
    text = (
        f"🗑️ Ви впевнені, що хочете видалити цей товар?\n\n"
        f"*Назва:* {name}\n"
        f"*Категорія:* {category}\n"
        f"*Ціна:* ${price:.2f}"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Підтвердити", callback_data=f"admin_confirm_remove_{product_id}"),
        types.InlineKeyboardButton("❌ Скасувати", callback_data="admin_cancel_remove")
    )
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_confirm_remove_'))
def handle_confirm_remove_product(call):
    product_id = int(call.data.split('_')[3])
    product = get_product_by_id(product_id)
    if not product:
        bot.send_message(call.message.chat.id, "❌ Товар не знайдено.")
        bot.answer_callback_query(call.id)
        return
    name = product[1]
    remove_product(product_id)
    bot.send_message(call.message.chat.id, f"✅ Товар '{name}' видалено з каталогу.")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_cancel_remove")
def handle_cancel_remove_product(call):
    bot.send_message(call.message.chat.id, "❌ Видалення скасовано.")
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['orders'])
def handle_orders_command(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Доступ заборонено.")
        return
    orders = get_orders()
    if not orders:
        bot.send_message(message.chat.id, "Замовлення відсутні.")
        return
    text = "📋 *Список замовлень:*\n\n"
    for order in orders:
        order_id, uid, uname, products, total, status, date = order
        text += (
            f"*Замовлення #{order_id}*\n"
            f"👤 {uname} (ID: {uid})\n"
            f"🛒 {products}\n"
            f"💵 Сума: ${total:.2f}\n"
            f"📦 Статус: {status}\n"
            f"📅 Дата: {date}\n\n"
            "-------------------------\n\n"
        )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "admin_view_orders")
def handle_admin_view_orders(call):
    try:
        user_id = call.from_user.id
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Доступ заборонено.")
            return
            
        # Створюємо нове повідомлення для імітації команди
        class FakeMessage:
            def __init__(self):
                self.chat = type('', (), {'id': call.message.chat.id})()
                self.from_user = type('', (), {'id': user_id})()
                self.text = '/orders'
                
        handle_orders_command(FakeMessage())
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Помилка в handle_admin_view_orders: {e}")
        bot.answer_callback_query(call.id, "❌ Помилка при перегляді замовлень")

@bot.message_handler(commands=['stats'])
def handle_stats_command(message):
    user_id = message.from_user.id  # Використовуємо правильний спосіб отримання ID
    logger.info(f"Команда /stats отримана від {user_id}")
    
    if user_id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Доступ заборонено.")
        return
    
    products = get_products()
    orders = get_orders()
    total_revenue = sum(order[4] for order in orders)  # total_price
    
    stats_text = (
        "📊 *Статистика магазину:*\n\n"
        f"📦 Кількість товарів: {len(products)}\n"
        f"📋 Кількість замовлень: {len(orders)}\n"
        f"💵 Загальний дохід: ${total_revenue:.2f}"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def handle_admin_stats(call):
    try:
        user_id = call.from_user.id
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Доступ заборонено.")
            return
            
        # Створюємо нове повідомлення для імітації команди
        class FakeMessage:
            def __init__(self):
                self.chat = type('', (), {'id': call.message.chat.id})()
                self.from_user = type('', (), {'id': user_id})()
                self.text = '/stats'
                
        handle_stats_command(FakeMessage())
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Помилка в handle_admin_stats: {e}")
        bot.answer_callback_query(call.id, "❌ Помилка при отриманні статистики")

