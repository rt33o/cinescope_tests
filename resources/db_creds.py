import os
from dotenv import load_dotenv
load_dotenv()

class DataBaseCreds:
    USERNAME = os.getenv("DATABASE_USER")
    PASSWORD = os.getenv("DATABASE_PASSWORD")
    NAME = os.getenv("DATABASE_NAME")
    HOST = os.getenv("DATABASE_HOST")
    PORT = os.getenv('DATABASE_PORT')
