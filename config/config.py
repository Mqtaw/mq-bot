import os
from dotenv import load_dotenv

load_dotenv()



basedir = os.path.abspath(os.path.dirname('README.md'))
db_path = os.path.join(basedir, "app.db")

class Config(object):
    TELEBOT_TOKEN = os.environ.get('TELEBOT_TOKEN')
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DATABASE_URL')}" or f'sqlite:////{db_path}'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = bool(int(os.environ.get('MAIL_USE_TLS')))
    # MAIL_USE_SSL = bool(int(os.environ.get('MAIL_USE_SSL')))
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # ADMINS = ['Testmqt@yandex.ru']
    # POSTS_PER_PAGE = 4
    # LANGUAGES = ['en', 'es']
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
