import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_USER = os.environ.get('DB_USER')
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_PORT = os.environ.get('DB_PORT')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

