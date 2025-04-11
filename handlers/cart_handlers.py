
from bot_init import bot, user_carts, user_states
from keyboards import create_cart_keyboard, create_order_confirmation_keyboard
from utils.helpers import format_cart_text, format_order_summary
from database import get_product_by_id, save_order
from config import ADMIN_IDS, logger
from telebot import types

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
def handle_add_to_cart(call):
    user_id = call.from_user.id
    product_id = int(call.data.split('_')[3])
    product = get_product_by_id(product_id)
    if not product:
        bot.answer_callback_query(call.id, "Товар не знайдено.")
        return

    if user_id not in user_carts:
        user_carts[user_id] = {}

    if product_id in user_carts[user_id]:
        user_carts[user_id][product_id]['quantity'] += 1
    else:
        user_carts[user_id][product_id] = {
            'name': product[1],
            'price': product[4],
            'quantity': 1
        }

    bot.answer_callback_query(call.id, f"{product[1]} додано в кошик!")
    show_cart(call.message.chat.id, user_id)

def show_cart(chat_id, user_id):
    cart_text, total = format_cart_text(user_id)
    bot.send_message(chat_id, cart_text, parse_mode='Markdown', reply_markup=create_cart_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def handle_clear_cart(call):
    user_id = call.from_user.id
    if user_id in user_carts:
        user_carts[user_id] = {}
    bot.answer_callback_query(call.id, "Кошик очищено!")
    bot.send_message(call.message.chat.id, "🛒 Ваш кошик порожній")

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def handle_checkout(call):
    user_id = call.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        bot.answer_callback_query(call.id, "Ваш кошик порожній!")
        return
    user_states[user_id] = 'waiting_for_address'
    bot.send_message(call.message.chat.id, "📦 Введіть адресу доставки:")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda msg: msg.from_user.id in user_states and user_states[msg.from_user.id] == 'waiting_for_address')
def handle_address_input(msg):
    user_id = msg.from_user.id
    address = msg.text
    if 'order_info' not in user_states:
        user_states['order_info'] = {}
    if user_id not in user_states['order_info']:
        user_states['order_info'][user_id] = {}
    user_states['order_info'][user_id]['address'] = address
    user_states[user_id] = 'waiting_for_phone'
    bot.send_message(msg.chat.id, "📱 Введіть номер телефону:")

@bot.message_handler(func=lambda msg: msg.from_user.id in user_states and user_states[msg.from_user.id] == 'waiting_for_phone')
def handle_phone_input(msg):
    user_id = msg.from_user.id
    phone = msg.text
    user_states['order_info'][user_id]['phone'] = phone
    order_text, total = format_order_summary(user_id, user_states)
    markup = create_order_confirmation_keyboard()
    bot.send_message(msg.chat.id, order_text, parse_mode='Markdown', reply_markup=markup)
    user_states[user_id] = 'confirming_order'

@bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
def handle_confirm_order(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    if user_id not in user_carts or not user_carts[user_id]:
        bot.answer_callback_query(call.id, "Ваш кошик порожній!")
        return

    cart = user_carts[user_id]
    address = user_states['order_info'][user_id]['address']
    phone = user_states['order_info'][user_id]['phone']
    products_str = ", ".join([f"{item['name']} x{item['quantity']}" for item in cart.values()])
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    order_id = save_order(user_id, user_name, products_str, total, address, phone)

    bot.send_message(
        call.message.chat.id,
        f"✅ *Замовлення #{order_id} підтверджено!*\n\n"
        f"Дякуємо за покупку. Очікуйте дзвінка для уточнення оплати.\n"
        f"*Сума:* ${total:.2f}\n"
        f"*Телефон:* {phone}",
        parse_mode='Markdown'
    )

    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                f"🔔 *Нове замовлення #{order_id}*\n\n"
                f"👤 {user_name} (ID: {user_id})\n"
                f"🛒 {products_str}\n"
                f"💵 ${total:.2f}\n"
                f"📦 {address}\n"
                f"📱 {phone}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Не вдалося повідомити адміна {admin_id}: {e}")

    user_carts[user_id] = {}
    if user_id in user_states:
        del user_states[user_id]
    if user_id in user_states.get('order_info', {}):
        del user_states['order_info'][user_id]
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_order")
def handle_cancel_order(call):
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    if 'order_info' in user_states and user_id in user_states['order_info']:
        del user_states['order_info'][user_id]
    bot.send_message(call.message.chat.id, "❌ Замовлення скасовано. Товари залишились у кошику.")
    bot.answer_callback_query(call.id)