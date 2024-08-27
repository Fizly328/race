import sqlite3

import telebot
import time
import logging

from config import TOKEN
from telebot import types
from db import *

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level=logging.INFO)

user_data = {}

def set_user_state(user_id, role, state):
    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO user_states (user_id, role, state)
                              VALUES (?, ?, ?)''', (user_id, role, state))
            conn.commit()

    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")


def get_user_state(user_id):
    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state FROM user_states WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return None  # Пользователь не найден
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        race_btn = types.KeyboardButton(text='🏁 Гонки на Cherry 🏁')

        markup.add(race_btn)

        bot.send_message(user_id, 'Добро пожаловать заного!')
        bot.send_message(user_id, 'Выбери что бы ты хотел, Шумахер', reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Пожалуйста, попробуйте снова.')
        logging.error(f"Error in Start: {e}")


@bot.message_handler(func=lambda message: message.text == '🏁 Гонки на Cherry 🏁')
def race_reg(message):
    user_id = message.chat.id
    try:
        state = get_user_state(user_id)
        if state == 'registered':
            bot.send_message(user_id, "Вы уже бросили свой вызов!")

        elif state != 'registered':
            msg = bot.send_message(user_id, 'Введите ваш Nick_Name: \n')
            bot.register_next_step_handler(msg, user_name)

    except Exception as e:
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова!')

def user_name(message):
    user_id = message.chat.id
    try:
        if user_id not in user_data:
            user_data[user_id] = {}
        name = message.text
        user_data[user_id] = {'id': user_id, 'name': name, 'last_name': message.chat.username or 'Не указан'}
        msg = bot.send_message(user_id, 'Введите ваш сервер:\n')
        bot.register_next_step_handler(msg, user_server)
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO races_reg (id, name, last_name)
                              VALUES (?, ?, ?)''', (
            user_id, name, message.chat.username
            ))
            conn.commit()
    except Exception as e:
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова!')


def user_server(message):
    user_id = message.chat.id
    try:
        if user_id not in user_data:
            user_data[user_id] = {}
        server = message.text
        user_data[user_id] = {'server': server}
        msg = bot.send_message(user_id, 'Какая у вас машина:\n')
        bot.register_next_step_handler(msg, user_car)
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO races_reg (server)
                              VALUES (?)''',  (
            server,
            ))
            conn.commit()


    except Exception as e:
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова!')


def user_car(message):
    user_id = message.chat.id
    try:
        car = message.text

        # Проверка и инициализация user_data[user_id], если необходимо
        if user_id not in user_data:
            user_data[user_id] = {}

        user_data[user_id]['car'] = car

        # Проверяем, что все нужные данные заполнены

        # Вставляем данные в базу
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO races_reg (car)
                              VALUES (?)''', (
                car,
            ))
            conn.commit()
            bot.send_message(user_id, 'Ваши данные успешно сохранены!')
            bot.send_message(user_id, 'Если в течение 2 недель вызов не примется, то он будет удален!')
            set_user_state(user_id, 'racing', 'registered')

    except Exception as e:
        logging.error(f"Error in user_car: {e}")
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова!')

@bot.message_handler(commands=['show'])
def view_all_races_reg(message):
    chat_id = message.chat.id
    # Подключаемся к базе данных
    with sqlite3.connect('example.db') as conn:
        cursor = conn.cursor()
        # Проверяем, есть ли у клиента заказы
        cursor.execute("SELECT * FROM races_reg WHERE id = ?", (chat_id,))
        rows = cursor.fetchall()
        if rows:
            response = "Ваши заказы:\n\n"
            for row in rows:
                response += f"ID: {row[0]},\n Name: {row[1]},\n User_Name: {row[2]},\n Сервер: {row[3]}\n Машина: {row[4]}\n"
            bot.send_message(chat_id, response)
        else:
            bot.send_message(chat_id, "Нету зарегестрированных людей.")


if __name__ == "__main__":
    create_tables()
    create_states()
    while True:
        try:
            logging.info("Starting bot polling")
            bot.polling(none_stop=True, timeout=60, interval=0)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            print(f"Ошибка: {e}")
            time.sleep(15)
