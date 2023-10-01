import psycopg2
from psycopg2 import sql


class DBState:
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
            CREATE TABLE IF NOT EXISTS users_state (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                space_num INTEGER,
                project_num INTEGER,
                board_num INTEGER
            )
        """)

        self.cur.execute(create_table_query)

        # Подтверждение изменений
        self.conn.commit()

    def InsertDB(self, user_id):
        check_user_query = "SELECT * FROM users_state WHERE user_id = %s;"
        self.cur.execute(check_user_query, (user_id,))
        existing_user = self.cur.fetchone()

        # Если пользователь с указанным user_id не существует, выполнить вставку
        if not existing_user:
            insert_query = ("INSERT INTO users_state (user_id, space_num, project_num, board_num)"
                            " VALUES (%s, %s, %s, %s);")
            self.cur.execute(insert_query, (user_id, 0, 0, 0))

            # Подтверждение изменений
            self.conn.commit()

    def UpdateDB(self, user_id, set_num, num):
        update_query = f"UPDATE users_state SET {set_num} = %s WHERE user_id = %s;"

        # Выполнение SQL-запроса с передачей параметров
        self.cur.execute(update_query, (num, user_id))

        # Подтверждение изменений
        self.conn.commit()

    def SelectDB(self, user_id):
        select_query = "SELECT * FROM users_state WHERE user_id = CAST(%s AS INTEGER);"

        # Выполнение SQL-запроса
        self.cur.execute(select_query, (user_id,))

        # Получение первой строки результата (если она существует)
        row = self.cur.fetchone()

        if row:
            # ID пользователя: row[1]
            # Выбранное Пространство: row[2]
            # Выбранный Проект: row[3]
            # Выбранная Доска: row[4]

            return [row[2], row[3], row[4]]
