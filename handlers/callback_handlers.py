
from telebot import types
from bot_init import bot, user_states
from database import get_products_by_category, get_products, get_product_by_id
from keyboards import (
    create_product_details_keyboard,
    create_categories_keyboard,
    create_payment_methods_keyboard,
    create_payment_simulation_keyboard,
    create_payment_retry_keyboard
)
from handlers.cart_handlers import show_cart
from utils.helpers import format_cart_text

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def handle_category_callback(call):
    chat_id = call.message.chat.id
    category_type = call.data.split('_')[1]
    
    category_map = {
        'writing': 'Письмове приладдя',
        'paper': 'Паперові вироби',
        'office': 'Офісне приладдя',
        'school': 'Шкільне канцелярське приладдя',
        'all': 'All'
    }
    
    category = category_map.get(category_type, 'All')
    
    if category == "All":
        products = get_products()
        show_products_list(chat_id, products, "Всі товари")
    else:
        products = get_products_by_category(category)
        show_products_list(chat_id, products, category)
    
    bot.answer_callback_query(call.id)

def show_products_list(chat_id, products, category_name):
    if not products:
        bot.send_message(chat_id, f"😕 Не знайдено товарів у категорії: {category_name}")
        return
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for product in products:
        if category_name == "Всі товари":
            product_id, name, category, desc, price = product
            btn_text = f"{name} ({category}) - ${price:.2f}"
        else:
            product_id, name, desc, price = product
            btn_text = f"{name} - ${price:.2f}"
            
        markup.add(types.InlineKeyboardButton(
            btn_text, 
            callback_data=f"product_{product_id}"
        ))
    
    markup.add(types.InlineKeyboardButton("« Назад до категорій", callback_data="back_to_categories"))
    
    bot.send_message(
        chat_id,
        f"📋 *{category_name}*\n\nОберіть товар для деталей:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def handle_product_callback(call):
    chat_id = call.message.chat.id
    product_id = int(call.data.split('_')[1])
    product = get_product_by_id(product_id)
    
    if not product:
        bot.send_message(chat_id, "😕 Товар не знайдено")
        return
    
    product_id, name, category, description, price = product
    
    product_text = (
        f"*{name}*\n\n"
        f"*Категорія:* {category}\n"
        f"*Ціна:* ${price:.2f}\n\n"
        f"*Опис:* {description}"
    )
    
    markup = create_product_details_keyboard(product_id, category)
    
    bot.send_message(
        chat_id,
        product_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_categories")
def handle_back_to_categories(call):
    bot.send_message(
        call.message.chat.id,
        "📚 *Оберіть категорію товарів:*",
        reply_markup=create_categories_keyboard(),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_'))
def handle_back_to_category(call):
    category = call.data.split('_')[2]
    category = category.replace('_', ' ')
    
    if category == "All":
        products = get_products()
        show_products_list(call.message.chat.id, products, "Всі товари")
    else:
        products = get_products_by_category(category)
        show_products_list(call.message.chat.id, products, category)
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "payment")
def handle_payment(call):
    chat_id = call.message.chat.id
    
    bot.send_message(
        chat_id,
        "💰 *Оберіть спосіб оплати:*",
        reply_markup=create_payment_methods_keyboard(),
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment_method(call):
    payment_method = call.data.split('_')[1]
    
    if payment_method == 'card':
        bot.send_message(
            call.message.chat.id,
            "💳 *Оплата карткою*\n\n"
            "У реальній реалізації тут буде інтеграція з платіжною системою.\n"
            "Для демонстрації ми імітуємо процес оплати.",
            parse_mode='Markdown'
        )
        
        bot.send_message(call.message.chat.id, "Обробка платежу...")
        
        markup = create_payment_simulation_keyboard()
        
        bot.send_message(
            call.message.chat.id,
            "Для демонстрації оберіть результат платежу:",
            reply_markup=markup
        )
    
    elif payment_method == 'cash':
        bot.send_message(
            call.message.chat.id,
            "💵 *Накладений платіж*\n\n"
            "Ваше замовлення буде доставлено за вказаною адресою, "
            "оплата здійснюється при отриманні.",
            parse_mode='Markdown'
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('payment_'))
def handle_payment_simulation(call):
    result = call.data.split('_')[1]
    
    if result == 'success':
        bot.send_message(
            call.message.chat.id,
            "✅ *Оплата успішна!*\n\n"
            "Ваше замовлення підтверджено та буде оброблено найближчим часом.\n"
            "Дякуємо за покупку!",
            parse_mode='Markdown'
        )
    
    elif result == 'fail':
        bot.send_message(
            call.message.chat.id,
            "❌ *Помилка оплати*\n\n"
            "Виникла проблема з вашим платежем. Спробуйте ще раз або оберіть інший спосіб оплати.",
            parse_mode='Markdown'
        )
        
        markup = create_payment_retry_keyboard()
        
        bot.send_message(
            call.message.chat.id,
            "Що ви хочете зробити?",
            reply_markup=markup
        )
    
    bot.answer_callback_query(call.id)