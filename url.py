import json

import requests

from config import db

s = requests.session()


class URLRequests:
    # Инициализация: Создание таблицы и нужных полей
    def __init__(self, user_id):
        db.CreateDB()
        self.user_id = user_id
        self.space = None
        self.space_id = None
        self.project = None
        self.project_id = None
        self.board = None
        self.board_id = None
        self.board_columns = None
        self.task = None
        self.task_status = None
        self.base_url = "https://api.teamflame.ru/"

    # Инициализация: Создание аккаунта
    def SignUp(self, last_name: str, first_name: str, sur_name: str, mail: str, password: str):
        __URL = 'https://auth-api.teamflame.ru/auth/sign-up'

        col = {
            "email": mail,
            "firstName": first_name,
            "lastName": last_name,
            "surName": sur_name,
            "password": password
        }

        s.post(__URL, json=col)

        return URLRequests(self.user_id).SignIn(mail, password)

    # Инициализация: Вход в аккаунт, Получение токена, Создание хедера, Добавление пользователя
    def SignIn(self, mail: str, password: str):
        __URL = 'https://auth-api.teamflame.ru/auth/sign-in'
        col = {
            "email": mail,
            "password": password
        }
        answer = s.post(__URL, json=col)

        if answer.status_code != 200:
            return answer.status_code

        req = json.loads(answer.text)

        token = req["tokens"]["accessToken"]["token"]

        db.UpdateDB(self.user_id, 'mail', mail)
        db.UpdateDB(self.user_id, 'password', password)
        db.UpdateDB(self.user_id, 'token', token)

        return answer.status_code

    def PostCreateSpace(self, name):  # Создание нового Пространства
        __URL = self.base_url + 'space/create'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        col = {
            "name": name,
            "logo": "",
            "color": "#754AEE",
            "invites": []
        }

        s.post(__URL, json=col, headers=header)

    def GetSpaces(self, num: int):  # Получение всех Пространств
        __URL = self.base_url + 'space/spacesByUserId'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        req = s.get(__URL, headers=header).text
        req = json.loads(req)

        self.space = req[num]
        self.space_id = req[num]['id']

        return req

    def PostUpdateSpace(self, name: str):  # Обновление данных Пространства
        __URL = self.base_url + 'space/update/' + self.space_id
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        self.space['name'] = name

        s.post(__URL, json=self.space, headers=header)

    def PostCreateProject(self, private: True or False, name, project_key: str):  # Создание нового Проекта
        if len(project_key) != 3:
            return "Ошибка project_key длиной не 3 символа"

        __URL = self.base_url + 'project/create'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        col = {
            "private": private,
            "logo": "",
            "color": "#754AEE",
            "space": self.space_id,
            "projectKey": project_key,  # 3 Символа
            "name": name,
            "location": self.space_id
        }

        s.post(__URL, json=col, headers=header)

    def GetProject(self, num):  # Получение списка Проектов
        __URL = self.base_url + 'project/projectsBySpace/' + self.space_id
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        req = s.get(__URL, headers=header).text
        req = json.loads(req)

        self.project = req[num]
        self.project_id = req[num]['id']

        return req

    def PostCreateBoard(self, name):  # Создание новой Доски
        __URL = self.base_url + 'board/create'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        col = {
            "name": name,
            "logo": "",
            "color": "#754AEE",
            "projectId": self.project_id,
            "location": self.space_id
        }

        s.post(__URL, json=col, headers=header)

    def GetBoard(self, num):  # Получение списка Досок
        __URL = self.base_url + 'board/boardsByProject/' + self.project_id
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        req = s.get(__URL, headers=header).text
        req = json.loads(req)

        self.board = req[num]
        self.board_id = req[num]['id']
        self.board_columns = req[num]['columns']

        return req

    def PostCreateTask(self, name, description, status='Сделать'):  # Создание новой Задачи: 1 Задача
        __URL = self.base_url + 'task/create'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        if status == "Сделать":
            self.task_status = 0
        elif status == "В работе":
            self.task_status = 1
        elif status == "Готово":
            self.task_status = 2
        elif status == "Закрыто":
            self.task_status = 3

        col = {
            "name": name,
            "description": description,
            "columnId": self.board_columns[self.task_status],
            "location": self.space_id,
            "projectId": self.project_id,
            "boardId": self.board_id,
            "spaceId": self.space_id
        }

        req = s.post(__URL, json=col, headers=header)

        return req.status_code

    def GetTaskByBoard(self, num):  # Получение Задач в колонке
        __URL = self.base_url + 'column/getByBoardOneLayer/' + self.board_id
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        req = s.get(__URL, headers=header).text
        req = json.loads(req)

        self.task = req[num]['tasks']

        return req

    def GetTaskByProject(self):
        __URL = self.base_url + 'task/getTasksByProject/' + self.project_id
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        req = s.get(__URL, headers=header).text
        req = json.loads(req)

        return req

    def PostTaskChangeColumn(self, num, column_num):  # Изменение статуса Задачи: 2 Задача
        __URL = self.base_url + 'task/change-column/' + self.task[num]['id']
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        col = {
            "columnId": self.board_columns[column_num],
            "location": self.space_id
        }

        s.post(__URL, json=col, headers=header)

    def PostComment(self, num, comment):  # Добавление комментария к задаче: 3 Задача
        __URL = self.base_url + 'comment/create'
        token = db.SelectDB(self.user_id)

        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        col = {
            "task": self.task[num]['id'],
            "text": f"<p>{comment}</p>"
        }

        req = s.post(__URL, json=col, headers=header)

        return req.status_code
