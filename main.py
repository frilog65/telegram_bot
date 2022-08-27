import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio
import time
import pickle
import urllib.parse

bot1 = telebot.TeleBot('5580779124:AAGJrUdTyLDhItFhWnj3oz_FLNOP_L9dEU4')
bot2 = telebot.TeleBot('5432120976:AAGgPJSyn4GAZPVisBy7qvvMiwsbdh63xtE')


# photo = open('photo.jpg', 'rb')
# bot.send_photo(399138349, photo, caption='Новости дня! <b>Все плохо!</b>', parse_mode='html')
# audio1 = open('song.mp3', 'rb')


@bot1.message_handler(commands=['help'])
def make_post(message):
    msg = bot1.send_message(message.chat.id, 'Введите сообщение')
    bot1.register_next_step_handler(msg, make_post_text)


def make_post_text(message):
    bot2.send_message(message.chat.id, message.text)


@bot1.message_handler(commands=['save'])
def save(message):
    with open('users.pickle', 'wb') as f:
        # pickle.dump({message.from_user.id: {'sections': {'Стажировки', 'Мероприятия'}, 'themes': {'IT', 'Маркетинг'}}}, f)
        pickle.dump({}, f)
    with open('users.pickle', 'rb') as f:
        print(pickle.load(f))


@bot1.message_handler(commands=['look'])
def look(message):
    with open('users.pickle', 'rb') as f:
        users = pickle.load(f)
    if message.from_user.id not in users.keys():
        bot1.send_message(message.chat.id, 'Тебя еще нет в нашем списке :(')
        return
    user_info = users[message.from_user.id]
    result = 'Твои данные:\n<b>Направления:</b> '
    for i, elem in enumerate(user_info['sections']):
        if i != len(user_info['sections']) - 1:
            result += elem + ', '
        else:
            result += elem
    result += '\n<b>Сферы:</b> '
    for i, elem in enumerate(user_info['themes']):
        if i != len(user_info['themes']) - 1:
            result += elem + ', '
        else:
            result += elem
    bot1.send_message(message.chat.id, result, parse_mode='html')
    print(users)


@bot1.message_handler(commands=['start'])
def start(message):
    with open('users.pickle', 'rb') as f:
        users = pickle.load(f)
    if message.from_user.id not in users.keys():
        users[message.from_user.id] = {}
    users[message.from_user.id]['sections'] = set()
    users[message.from_user.id]['themes'] = set()
    with open('users.pickle', 'wb') as f:
        pickle.dump(users, f)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Стажировки', 'Мероприятия', 'Кейс-чемпионаты', 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'))
    msg = bot1.send_message(message.chat.id, 'Привет! Рады видеть тебя! Выбери, какие новости ты хочешь получать.',
                            reply_markup=markup)
    bot1.register_next_step_handler(msg, get_user_sections)


def get_user_sections(message):
    if message.text == 'Стажировки' or message.text == 'Мероприятия' or message.text == 'Кейс-чемпионаты':
        with open('users.pickle', 'rb') as f:
            users = pickle.load(f)
        users[message.from_user.id]['sections'].add(message.text)
        with open('users.pickle', 'wb') as f:
            pickle.dump(users, f)
        msg = bot1.send_message(message.chat.id, f'Добавил {message.text} в список!')
        bot1.register_next_step_handler(msg, get_user_sections)
        print(users[message.from_user.id])
    elif message.text == 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('IT', 'Маркетинг', 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'))
        msg = bot1.send_message(message.chat.id, 'Отлично! Теперь выбери сферы, которыми ты интересуешься.',
                                reply_markup=markup)
        bot1.register_next_step_handler(msg, get_user_themes)
    else:
        msg = bot1.send_message(message.chat.id, 'Я тебя не понимаю. Просто используй кнопки.')
        bot1.register_next_step_handler(msg, get_user_sections)


def get_user_themes(message):
    if message.text == 'IT' or message.text == 'Маркетинг':
        with open('users.pickle', 'rb') as f:
            users = pickle.load(f)
        users[message.from_user.id]['themes'].add(message.text)
        with open('users.pickle', 'wb') as f:
            pickle.dump(users, f)
        msg = bot1.send_message(message.chat.id, f'Добавил {message.text} в список!')
        bot1.register_next_step_handler(msg, get_user_themes)
        print(users[message.from_user.id])
    elif message.text == 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'):
        with open('users.pickle', 'rb') as f:
            users = pickle.load(f)
        result = 'Сохранили твои данные! Вот что ты выбрал:\n<b>Направления:</b> '
        for i, elem in enumerate(users[message.from_user.id]['sections']):
            if i != len(users[message.from_user.id]['sections']) - 1:
                result += elem + ', '
            else:
                result += elem
        result += '\n<b>Сферы:</b> '
        for i, elem in enumerate(users[message.from_user.id]['themes']):
            if i != len(users[message.from_user.id]['themes']) - 1:
                result += elem + ', '
            else:
                result += elem
        print(users[message.from_user.id])
        markup = types.ReplyKeyboardRemove()
        msg = bot1.send_message(message.chat.id, result, parse_mode='html', reply_markup=markup)
        bot1.clear_step_handler(msg)
    else:
        msg = bot1.send_message(message.chat.id, 'Я тебя не понимаю. Просто используй кнопки.')
        bot1.register_next_step_handler(msg, get_user_themes)


bot1.enable_save_next_step_handlers(delay=2)
bot1.load_next_step_handlers()

bot2.enable_save_next_step_handlers(delay=2)
bot2.load_next_step_handlers()

"""
    def get_user_sections(message1):
        if message1.text == 'Стажировки' or message1.text == 'Мероприятия':
            new_user['sections'].add(message1.text)
            bot1.send_message(message1.chat.id, f'Добавил {message1.text} в список!')
            print(new_user)
        elif message1.text == 'Продолжить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('IT', 'Маркетинг', 'Продолжить')
            msg = bot1.send_message(message1.chat.id, 'Отлично! Теперь выбери сферы, которыми ты интересуешься.', reply_markup=markup)
            bot1.register_next_step_handler(msg, get_user_themes)
        else:
            bot1.send_message(message1.chat.id, 'Я тебя не понимаю. Просто используй кнопки.')

    def get_user_themes(message1):
        if message1.text == 'IT' or message1.text == 'Маркетинг':
            new_user['themes'].add(message1.text)
            msg = bot1.send_message(message1.chat.id, f'Добавил {message1.text} в список!')
            bot1.register_next_step_handler(msg, get_user_themes)
        elif message1.text == 'Продолжить':
            result = 'Вот что ты выбрал!\n<b>Направления:</b>'
            for elem in new_user['sections']:
                result += ' ' + elem
            result += '\n<b>Сферы:</b>'
            for elem in new_user['themes']:
                result += ' ' + elem
            print(new_user)
            bot1.clear_step_handler(bot1.send_message(message1.chat.id, result, parse_mode='html'))

        bot1.enable_save_next_step_handlers(delay=5)
        bot1.load_next_step_handlers()"""

bot1.polling(none_stop=True)

#bot2.polling(none_stop=True)

#asyncio.run(bot1.polling(none_stop=True))
#asyncio.run(bot2.polling(none_stop=True))
