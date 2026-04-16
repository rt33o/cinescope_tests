from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import MoviesDbCreds
import os

USERNAME = MoviesDbCreds.USERNAME
PASSWORD = MoviesDbCreds.PASSWORD
HOST = MoviesDbCreds.HOST
PORT = MoviesDbCreds.PORT
NAME = MoviesDbCreds.NAME

db_url = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{NAME}"
print(f"\n\n>>> DEBUG URL: {db_url} <<<\n")

#  движок для подключения к базе данных
engine = create_engine(db_url,
    echo=False  # Установить True для отладки SQL запросов
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()