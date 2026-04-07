
import psycopg2
from resources.db_creds import DataBaseCreds

def connect_to_postgres():
    """Функция подключения к PostrgreSQL базе данных"""
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            dbname=DataBaseCreds.NAME,
            user=DataBaseCreds.USERNAME,
            password=DataBaseCreds.PASSWORD,
            host=DataBaseCreds.HOST,
            port=DataBaseCreds.PORT
        )
        print("Успешно подключено к DB")

        #Creating Cursor
        cursor = connection.cursor()

        #Getting info about SQL Server
        print("Информация о сервере PostgreSQL:")
        print(connection.get_dsn_parameters(), "\n")

        #SQL script executing
        cursor.execute("SELECT version();")

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