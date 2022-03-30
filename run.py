import time
from mqbot import bot


def infinity_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)


if __name__ == "__main__":
    infinity_polling()
