from telebot import types
from config import ADMIN_IDS

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton('📚 Каталог'),
        types.KeyboardButton('ℹ️ Інформація'),
        types.KeyboardButton('❓ Допомога'),
        types.KeyboardButton('🛒 Кошик')
    ]
    markup.add(*buttons)
    return markup

def create_admin_main_keyboard(user_id):
    markup = create_main_keyboard()
    if user_id in ADMIN_IDS:
        markup.add(types.KeyboardButton('👑 Адмінпанель'))
    return markup

def create_categories_keyboard():
    categories = [
        ("✏️ Письмове приладдя", "cat_writing"),
        ("📄 Паперові вироби", "cat_paper"), 
        ("📎 Офісне приладдя", "cat_office"),
        ("📏 Шкільне канцелярське приладдя", "cat_school"),
        ("🔍 Всі товари", "cat_all")
    ]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(categories)-1, 2):
        markup.row(
            types.InlineKeyboardButton(categories[i][0], callback_data=categories[i][1]),
            types.InlineKeyboardButton(categories[i+1][0], callback_data=categories[i+1][1])
        )
    markup.add(types.InlineKeyboardButton(categories[-1][0], callback_data=categories[-1][1]))
    return markup

def create_product_details_keyboard(product_id, category):
    category_map = {
        'Письмове приладдя': 'writing',
        'Паперові вироби': 'paper',
        'Офісне приладдя': 'office',
        'Шкільне канцелярське приладдя': 'school'
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_to_cart_{product_id}"),
        types.InlineKeyboardButton("« Назад", callback_data=f"back_to_{category_map.get(category, 'all')}")
    )
    return markup

def create_cart_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout"),
        types.InlineKeyboardButton("❌ Очистити кошик", callback_data="clear_cart")
    )
    markup.add(types.InlineKeyboardButton("🛍️ Продовжити покупки", callback_data="back_to_categories"))
    return markup

def create_order_confirmation_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Підтвердити", callback_data="confirm_order"),
        types.InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")
    )
    return markup

def create_admin_keyboard():
    buttons = [
        ("➕ Додати товар", "admin_add_product"),
        ("➖ Видалити товар", "admin_remove_product"),
        ("📋 Переглянути замовлення", "admin_view_orders"),
        ("📊 Статистика", "admin_stats")
    ]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            markup.row(
                types.InlineKeyboardButton(buttons[i][0], callback_data=buttons[i][1]),
                types.InlineKeyboardButton(buttons[i+1][0], callback_data=buttons[i+1][1])
            )
        else:
            markup.add(types.InlineKeyboardButton(buttons[i][0], callback_data=buttons[i][1]))
    return markup

def create_product_categories_admin_keyboard():
    categories = ["Письмове приладдя", "Паперові вироби", "Офісне приладдя", "Шкільне канцелярське приладдя"]
    markup = types.InlineKeyboardMarkup()
    for category in categories:
        markup.add(types.InlineKeyboardButton(category, callback_data=f"admin_category_{categories.index(category)}"))
    markup.add(types.InlineKeyboardButton("❌ Скасувати", callback_data="admin_cancel_operation"))
    return markup

def create_admin_confirm_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Підтвердити", callback_data="admin_confirm_add_product"),
        types.InlineKeyboardButton("❌ Скасувати", callback_data="admin_cancel_operation")
    )
    return markup

def create_payment_methods_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Кредитна/Дебетова картка", callback_data="pay_card"))
    markup.add(types.InlineKeyboardButton("💵 Накладений платіж", callback_data="pay_cash"))
    return markup

def create_payment_simulation_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Симулювати успішний платіж", callback_data="payment_success"))
    markup.add(types.InlineKeyboardButton("❌ Симулювати невдалий платіж", callback_data="payment_fail"))
    return markup

def create_payment_retry_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Повторити платіж", callback_data="payment"))
    markup.add(types.InlineKeyboardButton("❌ Скасувати замовлення", callback_data="cancel_order"))
    return markup