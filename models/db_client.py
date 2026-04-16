
import psycopg2
from psycopg2 import extras
from resources.db_creds import MoviesDbCreds

def connect_to_postgres():
    """Функция подключения к PostrgreSQL базе данных"""
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            dbname=MoviesDbCreds.NAME,
            user=MoviesDbCreds.USERNAME,
            password=MoviesDbCreds.PASSWORD,
            host=MoviesDbCreds.HOST,
            port=MoviesDbCreds.PORT
        )
        print("Успешно подключено к DB")

        #Creating Cursor
        cursor = connection.cursor()

        #Getting info about SQL Server
        print("Информация о сервере PostgreSQL:")
        print(connection.get_dsn_parameters(), "\n")

        #SQL script executing
        cursor.execute("SELECT version();")

        # Создание стандартного курсора
        cursor = connection.cursor()

        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Выполнение SQL-запроса
        cursor.execute(f'''
                SELECT * from genres
                ORDER by id desc limit 100'''
                       )

        # Получение результата
        record = cursor.fetchall()
        print(record)

        #Getting results
        record = cursor.fetchone()
        print("Вы подключены к - ", record, "\n")

    except Exception as e:
        print("Ошибка при работе с бд", e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == "__main__":
    connect_to_postgres()