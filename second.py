import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio
import time
import pickle

# bot1 = telebot.TeleBot('5580779124:AAGJrUdTyLDhItFhWnj3oz_FLNOP_L9dEU4')
bot2 = telebot.TeleBot('5432120976:AAGgPJSyn4GAZPVisBy7qvvMiwsbdh63xtE')


@bot2.message_handler(commands=['start'])
def start(message):
    posts = {message.from_user.id: {}}
    posts[message.from_user.id]['sections'] = set()
    posts[message.from_user.id]['themes'] = set()

    with open('posts.pickle', 'wb') as f:
        pickle.dump(posts, f)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Стажировки', 'Мероприятия', 'Кейс-чемпионаты', 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'))
    msg = bot2.send_message(message.chat.id, 'Выберите направления:', reply_markup=markup)
    bot2.register_next_step_handler(msg, make_sections)


def make_sections(message):
    if message.text == 'Стажировки' or message.text == 'Мероприятия' or message.text == 'Кейс-чемпионаты':
        with open('posts.pickle', 'rb') as f:
            posts = pickle.load(f)
        posts[message.from_user.id]['sections'].add(message.text)
        with open('posts.pickle', 'wb') as f:
            pickle.dump(posts, f)
        msg = bot2.send_message(message.chat.id, f'Добавил {message.text} в список!')
        bot2.register_next_step_handler(msg, make_sections)
        print(posts[message.from_user.id])
    elif message.text == 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('IT', 'Маркетинг', 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'))
        msg = bot2.send_message(message.chat.id, 'Отлично! Теперь выбери сферы:',
                                reply_markup=markup)
        bot2.register_next_step_handler(msg, make_themes)
    else:
        msg = bot2.send_message(message.chat.id, 'Я тебя не понимаю. Просто используй кнопки.')
        bot2.register_next_step_handler(msg, make_sections)


def make_themes(message):
    if message.text == 'IT' or message.text == 'Маркетинг':
        with open('posts.pickle', 'rb') as f:
            posts = pickle.load(f)
        posts[message.from_user.id]['themes'].add(message.text)
        with open('posts.pickle', 'wb') as f:
            pickle.dump(posts, f)
        msg = bot2.send_message(message.chat.id, f'Добавил {message.text} в список!')
        bot2.register_next_step_handler(msg, make_themes)
        print(posts[message.from_user.id])
    elif message.text == 'Продолжить ' + b'\xE2\x9C\x85'.decode('utf-8'):
        with open('posts.pickle', 'rb') as f:
            posts = pickle.load(f)
        result = 'Сохранили твои данные! Вот что ты выбрал:\n<b>Направления:</b> '
        for i, elem in enumerate(posts[message.from_user.id]['sections']):
            if i != len(posts[message.from_user.id]['sections']) - 1:
                result += elem + ', '
            else:
                result += elem
        result += '\n<b>Сферы:</b> '
        for i, elem in enumerate(posts[message.from_user.id]['themes']):
            if i != len(posts[message.from_user.id]['themes']) - 1:
                result += elem + ', '
            else:
                result += elem
        print(posts[message.from_user.id])
        markup = types.ReplyKeyboardRemove()
        bot2.send_message(message.chat.id, result, parse_mode='html')
        msg = bot2.send_message(message.chat.id, 'Тебе напиши пост и отправь его:', parse_mode='html',
                                reply_markup=markup)
        bot2.register_next_step_handler(msg, make_post)
    else:
        msg = bot2.send_message(message.chat.id, 'Я тебя не понимаю. Просто используй кнопки.')
        bot2.register_next_step_handler(msg, make_themes)


def make_post(message):
    bot1 = telebot.TeleBot('5580779124:AAGJrUdTyLDhItFhWnj3oz_FLNOP_L9dEU4')
    with open('users.pickle', 'rb') as f:
        users = pickle.load(f)
    with open('posts.pickle', 'rb') as f:
        posts = pickle.load(f)

    for user in users.keys():
        if len(users[user]['sections'].intersection(posts[message.chat.id]['sections'])) > 0 and len(
                users[user]['themes'].intersection(posts[message.chat.id]['themes'])) > 0:
            if message.content_type == 'text':
                bot1.send_message(user, message.text, parse_mode='html')
            elif message.content_type == 'photo':
                # bot2.send_message(message.chat.id, message.photo[3])
                for i, elem in enumerate(message.photo):
                    if i == len(message.photo) - 1:
                        file_name = elem.file_unique_id + '.jpg'
                        file_info = bot2.get_file(elem.file_id)
                        downloaded_file = bot2.download_file(file_info.file_path)
                        with open(file_name, 'wb') as new_file:
                            new_file.write(downloaded_file)

                        photo = open(file_name, 'rb')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(
                            types.InlineKeyboardButton('Узнать больше', url='https://sbergraduate.ru/ambassadors/'))
                        bot1.send_photo(message.chat.id, photo, caption=message.caption, parse_mode='html',
                                        reply_markup=markup)


bot2.polling(none_stop=True)
