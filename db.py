import psycopg2
from psycopg2 import sql


class DBConnect:
    def __init__(self, user: str, password: str):
        self.conn = psycopg2.connect(
            host="localhost",
            database="user_data",
            user=user,
            password=password
        )

        self.cur = self.conn.cursor()

    # SQL-запрос для создания таблицы
    def CreateDB(self):
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                mail VARCHAR(255),
                password VARCHAR(255),
                token VARCHAR(255)
            )
        """)

        self.cur.execute(create_table_query)

        # Подтверждение изменений
        self.conn.commit()

    # SQL-запрос для добавления данных
    def InsertDB(self, user_id: int, mail: str, password: str, token: str):

        check_user_query = "SELECT * FROM users WHERE user_id = %s;"
        self.cur.execute(check_user_query, (user_id,))
        existing_user = self.cur.fetchone()

        # Если пользователь с указанным user_id не существует, выполнить вставку
        if not existing_user:
            insert_query = "INSERT INTO users (user_id, mail, password, token) VALUES (%s, %s, %s, %s);"
            self.cur.execute(insert_query, (user_id, mail, password, token))

            # Подтверждение изменений
            self.conn.commit()

    # SQL-запрос для обновления данных
    def UpdateDB(self, user_id, set_num, num):
        update_query = f"UPDATE users SET {set_num} = %s WHERE user_id = %s;"

        # Выполнение SQL-запроса с передачей параметров
        self.cur.execute(update_query, (num, user_id))

        # Подтверждение изменений
        self.conn.commit()

    # SQL-запрос для выборки данных из таблицы для определенного пользователя по его ID
    def SelectDB(self, user_id):
        select_query = "SELECT * FROM users WHERE user_id = CAST(%s AS INTEGER);"

        # Выполнение SQL-запроса
        self.cur.execute(select_query, (user_id,))

        # Получение первой строки результата (если она существует)
        row = self.cur.fetchone()

        if row:
            # ID пользователя: row[1]
            # Логин: row[2]
            # Пароль: row[3]
            # Токен: row[4]

            return row[4]

        else:
            return 404
