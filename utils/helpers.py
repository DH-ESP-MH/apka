
from bot_init import user_carts

def format_cart_text(user_id):
    if user_id not in user_carts or not user_carts[user_id]:
        return "🛒 Ваш кошик порожній", 0
    
    cart_text = "🛒 *Ваш кошик:*\n\n"
    total = 0
    
    for product_id, item in user_carts[user_id].items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_text += f"• {item['name']} x{item['quantity']} - ${subtotal:.2f}\n"
    
    cart_text += f"\n*Загальна сума: ${total:.2f}*"
    
    return cart_text, total

def format_order_summary(user_id, user_states):
    cart = user_carts[user_id]
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    order_text = "📝 *Підсумок замовлення:*\n\n"
    for product_id, item in cart.items():
        subtotal = item['price'] * item['quantity']
        order_text += f"• {item['name']} x{item['quantity']} - ${subtotal:.2f}\n"
    
    order_text += f"\n*Загальна сума: ${total:.2f}*\n\n"
    order_text += f"*Адреса доставки:* {user_states['order_info'][user_id]['address']}\n"
    order_text += f"*Телефон:* {user_states['order_info'][user_id]['phone']}\n\n"
    order_text += "Будь ласка, підтвердіть ваше замовлення:"
    
    return order_text, total