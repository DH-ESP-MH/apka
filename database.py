
import sqlite3
from datetime import datetime
from config import DB_PATH, logger

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        user_name TEXT,
        products TEXT NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        address TEXT,
        phone TEXT,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        user_name TEXT,
        message TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Синя кулькова ручка", "Письмове приладдя", "Гладке письмо кульковою ручкою з синім чорнилом", 1.50, None),
            ("Графітовий олівець HB", "Письмове приладдя", "Стандартний олівець твердості HB для письма та малювання", 0.75, None),
            ("Зошит A4", "Паперові вироби", "Зошит у лінійку, 80 сторінок, формат A4", 3.20, None),
            ("Кольорові стікери", "Паперові вироби", "Набір з 5 кольорів, по 100 аркушів кожного", 2.50, None),
            ("Металевий степлер", "Офісне приладдя", "Міцний металевий степлер на 20 аркушів", 5.99, None),
            ("Скріпки", "Офісне приладдя", "Коробка з 100 металевих скріпок", 1.25, None),
            ("Пластикова лінійка 30см", "Шкільне канцелярське приладдя", "Прозора пластикова лінійка з метричною та імперською шкалами", 1.00, None),
            ("Білий ластик", "Шкільне канцелярське приладдя", "М'який білий ластик для олівцевих позначок", 0.80, None)
        ]
        cursor.executemany("INSERT INTO products (name, category, description, price, image_url) VALUES (?, ?, ?, ?, ?)", sample_products)
    
    conn.commit()
    conn.close()
    logger.info("База даних успішно ініціалізована")

def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, description, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_products_by_category(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM products WHERE category=?", (category,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, description, price FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def add_product(name, category, description, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, description, price) VALUES (?, ?, ?, ?)",
                 (name, category, description, price))
    conn.commit()
    conn.close()
    logger.info(f"Додано новий продукт: {name}")

def remove_product(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    logger.info(f"Видалено продукт з ID: {product_id}")

def save_order(user_id, user_name, products, total_price, address, phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, user_name, products, total_price, address, phone) VALUES (?, ?, ?, ?, ?, ?)",
                 (user_id, user_name, products, total_price, address, phone))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Створено нове замовлення #{order_id} від користувача {user_name}")
    return order_id

def get_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, user_name, products, total_price, status, order_date FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

def save_feedback(user_id, user_name, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (user_id, user_name, message) VALUES (?, ?, ?)",
                 (user_id, user_name, message))
    conn.commit()
    conn.close()
    logger.info(f"Отримано новий відгук від користувача {user_name}")