import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Нахожу путь к папке, где лежит текущий файл
BASE_DIR = Path(__file__).resolve().parent

# 2. Указываю путь до .env в корневой папке
ENV_PATH = BASE_DIR.parent / '.env'

# 3. Загружаю конкретный файл
load_dotenv(dotenv_path=ENV_PATH)

class MoviesDbCreds:
    HOST = os.getenv('DATABASE_HOST')
    PORT = os.getenv('DATABASE_PORT')
    NAME = os.getenv('DATABASE_NAME')
    USERNAME = os.getenv('DATABASE_USER')
    PASSWORD = os.getenv('DATABASE_PASSWORD')

