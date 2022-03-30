from collections import namedtuple
import re

import telebot

from config.config import Config
from mqbot import database

# ApiTelegramException = telebot.apihelper.ApiTelegramException
# telebot.apihelper.proxy = {'https': f'http://{USERPROXY}:{PROXY_PASSWORD}@proxy.tcsbank.ru:8080'}
bot = telebot.TeleBot(Config.TELEBOT_TOKEN, threaded=False)


class Keyboard(object):
    KeyboardButton = namedtuple('KeyboardButton', ['title', 'callback_data'])

    def __init__(self):
        self.buttons: list[namedtuple] = []

    def add_button(self, title, callback_data):
        self.buttons.append(self.KeyboardButton(title=title, callback_data=callback_data))

    @property
    def keyboard(self):
        init_keyboard = telebot.types.InlineKeyboardMarkup()
        for button in self.buttons:
            init_keyboard.row(
                telebot.types.InlineKeyboardButton(
                    button.title, callback_data=button.callback_data
                )
            )
        return init_keyboard


@bot.message_handler(commands=['start'])
def start_handler(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)
    username = message.from_user.username if message.from_user.username else \
        message.from_user.first_name
    print(username)
    if user:
        msg = 'Для вас бот уже настроен. Воспользутесь ' \
              'командой /help для получения списка команд'
        bot.send_message(message.chat.id, text=msg)
    else:
        database.create_user(db.__next__(), tg_id=user_id, username=username)
        bot.send_message(message.chat.id, text='Пользователь создан')


@bot.message_handler(commands=['help'])
def start_handler(message):

    msg = "Бот для управления списками покупок.\n" \
          "Классическое использование - пишем название товара для добавки в текущий список, " \
          "пишем номер товара в списке для удаления. \n" \
          "Доступны команды:\n" \
          "/show - Показывает текущий список покупок\n" \
          "/share - Поделится списком покупок\n" \
          "/create - Создать новый список покупок\n" \
          "/choose - выбрать список покупок для взаимодействия\n" \
          "/delete - выбрать список покупок для удаления\n" \
          "/my_id - получить свой идентификатор"

    bot.send_message(message.chat.id, text=msg)


@bot.message_handler(commands=['show'])
def show_current_list_handler(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)
    shopping_list = database.get_shopping_list(
        db=db.__next__(), user_id=user_id, shopping_list_id=user.current_shopping_list_id)

    if not shopping_list:
        bot.send_message(message.chat.id, text=f'Выбранный список был удален владельцем')
        return None

    if not shopping_list.shopping_list.products:
        bot.send_message(message.chat.id,
                         text=f'Список покупок "{shopping_list.shopping_list_name}" пуст')
        return None

    items = shopping_list.shopping_list.products.split(',')
    msg = f'Текущий список покупок: {shopping_list.shopping_list_name}\n'
    for num, item in enumerate(items, start=1):
        msg += f'{num}: {item}\n'
    bot.send_message(message.chat.id, text=msg)


@bot.message_handler(commands=['share'])
def share_current_list_handler(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)
    shopping_list = database.get_shopping_list(
        db=db.__next__(), user_id=user_id, shopping_list_id=user.current_shopping_list_id)

    if not shopping_list:
        bot.send_message(message.chat.id, text=f'Выбранный список был удален владельцем')
        return None

    msg = f'Укажите id пользователя, с которым желаете ' \
          f'поделится списком покупок "{shopping_list.shopping_list_name}"'
    markup = telebot.types.ForceReply(selective=True)
    bot.send_message(message.chat.id, text=msg, reply_markup=markup)


@bot.message_handler(commands=['check_users'])
def check_joints_handler(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)

    shopping_list = database.get_shopping_list(
        db=db.__next__(), user_id=user_id, shopping_list_id=user.current_shopping_list_id)
    if not  shopping_list.owner:
        bot.send_message(message.chat.id, text='Проверка присоединенных к списку полоьзователей '
                                               'доступна только для владельца списка')
        return None

    attached_users = database.get_shopping_list_attached_users(
        db=db.__next__(), shopping_list_id=user.current_shopping_list_id)

    if not attached_users:
        bot.send_message(message.chat.id, text='Отсутствуют присоединенные пользователи '
                                               'для текущего списка')
        return None

    for user in attached_users:
        bot.send_message(message.chat.id, text=user.user.username)


@bot.message_handler(commands=['detach_user'])
def check_joints_handler(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)

    shopping_list = database.get_shopping_list(
        db=db.__next__(), user_id=user_id, shopping_list_id=user.current_shopping_list_id)
    if not shopping_list.owner:
        bot.send_message(message.chat.id, text='Отключение пользователей от списка '
                                               'доступно только для владельца')
        return None

    attached_users = database.get_shopping_list_attached_users(
        db=db.__next__(), shopping_list_id=user.current_shopping_list_id)


    if not attached_users:
        bot.send_message(message.chat.id, text='Отсутствуют присоединенные пользователи '
                                               'для текущего списка')
        return None

    keyboard = Keyboard()
    for attach in attached_users:
        keyboard.add_button(title=f'{attach.user.username}',
                            callback_data=f'detach&{attach.shopping_list_id}&{attach.user_id}')
    bot.send_message(message.chat.id, "Кого отсоединяем?", reply_markup=keyboard.keyboard)



@bot.message_handler(func=lambda message: message.reply_to_message and
                                          "Укажите id пользователя," in
                                          message.reply_to_message.text)
def share_current_list_request(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)

    username = message.from_user.username if message.from_user.username else\
        message.from_user.first_name


    msg = f'Пользователь {username} желает поделиться с вами списком покупок. ' \
          f'Ответьте желаемым названием списка, если принимаете.\n User_id={user_id}, ' \
          f'list_id={user.current_shopping_list_id}'
    markup = telebot.types.ForceReply(selective=True)
    bot.send_message(message.text, text=msg, reply_markup=markup)



@bot.message_handler(func=lambda message: message.reply_to_message and
                                          "желает поделиться с вами списком покупок" in
                                          message.reply_to_message.text)
def share_current_list_response(message):
    db = database.get_db()
    user_id = message.from_user.id
    source_user, shopping_list_id = re.findall(r'\d+', message.reply_to_message.text)[-2:]

    database.join_user_to_shopping_list(db=db.__next__(), user_id=user_id,
                                        shopping_list_id=int(shopping_list_id),
                                        name=message.text)

    username = message.from_user.username if message.from_user.username else\
        message.from_user.first_name

    bot.send_message(message.chat.id, text=f'Список покупок "{message.text}" добавлен.')
    bot.send_message(int(source_user), text=f'Пользователь "{username}" принял список покупок')


@bot.message_handler(commands=['create'])
def add_list_ask_name(message):
    markup = telebot.types.ForceReply(selective=True)
    bot.reply_to(message, text="Назовите новый список:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.reply_to_message and
                                          "Назовите новый список:" in
                                          message.reply_to_message.text)
def add_list_create(message):
    db = database.get_db()
    shopping_list_name = database.create_shopping_list(db.__next__(),
                                                  user_id=message.from_user.id,
                                                  name=message.text)
    msg = f'Список покупок {shopping_list_name} создан и назначен текущим'
    bot.send_message(message.chat.id, text=msg)


@bot.message_handler(commands=['choose', 'delete'])
def choose_list(message):
    command = message.text[1:]
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)

    keyboard = Keyboard()
    for sl in user.shopping_lists:
        keyboard.add_button(title=f'{sl.shopping_list_name}',
                            callback_data=f'{command}&{sl.shopping_list_id}')

    msg = 'Выберети текущий список покупок:' if command == 'choose' \
        else 'Выберети список для удаления:'
    bot.send_message(message.chat.id, msg,
                     reply_markup=keyboard.keyboard)



@bot.message_handler(commands=['my_id'])
def get_id_handler(message):
    bot.send_message(message.chat.id, text='Ваш ID:')
    bot.send_message(message.chat.id, text=f'{message.from_user.id}')


@bot.message_handler(func=lambda message: True)
def add_item(message):
    db = database.get_db()
    user_id = message.from_user.id
    user = database.get_user(db=db.__next__(), tg_id=user_id)
    shopping_list = database.get_shopping_list(
        db=db.__next__(), user_id=user_id,
        shopping_list_id=user.current_shopping_list_id)

    if not shopping_list:
        bot.send_message(message.chat.id, text=f'Выбранный список был удален владельцем')
        return None

    status = database.update_products(db=db.__next__(), shopping_list=shopping_list.shopping_list,
                                      item=message.text)
    if not status:
        bot.send_message(message.chat.id, text="Указан номер элемента вне списка")
    elif status == 'Deleted':
        show_current_list_handler(message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('choose'))
def choose_list_callback_handler(query):
    bot.answer_callback_query(query.id)
    db = database.get_db()
    user_id = query.message.chat.id
    shopping_list_id = int(query.data.split('&')[1])
    database.change_current_shopping_list(db=db.__next__(), user_id=user_id,
                                          shopping_list_id=shopping_list_id)

    shopping_list = database.get_shopping_list(db=db.__next__(), user_id=user_id,
                                               shopping_list_id=shopping_list_id)

    msg = f'Выбран список покупок: {shopping_list.shopping_list_name}'
    bot.send_message(query.message.chat.id, text=msg)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('delete'))
def choose_list_callback_handler(query):
    bot.answer_callback_query(query.id)
    db = database.get_db()
    user_id = query.message.chat.id
    shopping_list_id = int(query.data.split('&')[1])
    status = database.delete_shopping_list(db=db.__next__(), user_id=user_id,
                                           shopping_list_id=shopping_list_id)
    if not status:
        bot.send_message(query.message.chat.id, text='Невозможно удалить активный список')
    else:
        bot.send_message(query.message.chat.id, text=f'Список покупок удален')


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('detach'))
def detach_user_callback_handler(query):
    bot.answer_callback_query(query.id)
    db = database.get_db()
    print(query.data.split('&')[1:])
    shopping_list_id, detach_user_id = map(int, query.data.split('&')[1:])
    database.detach_user_from_shopping_list(db=db.__next__(), shopping_list_id=shopping_list_id,
                                           detach_user_id=detach_user_id)
    bot.send_message(query.message.chat.id, text=f'Пользователь отсоединен')


if __name__ == "__main__":
    bot.infinity_polling()
