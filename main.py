import logging
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import TOKEN, db, db_state
from url import URLRequests

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

open_space = InlineKeyboardButton('Открыть Пространство', callback_data='open_project_call')
open_project = InlineKeyboardButton('Открыть Проект', callback_data='open_board_call')
open_board = InlineKeyboardButton('Открыть Доску', callback_data='open_task_list_call')
open_task_list = InlineKeyboardButton('Открыть Список задач', callback_data='open_task_list_call')
create_task = InlineKeyboardButton('Добавить Задачу', callback_data='create_task_call')

create_btn = InlineKeyboardButton('Сделать', callback_data='create')
work_btn = InlineKeyboardButton('В работе', callback_data='work')
success_btn = InlineKeyboardButton('Готово', callback_data='success')
exit_btn = InlineKeyboardButton('Закрыто', callback_data='exit')

comment_btn = InlineKeyboardButton('Комментарий', callback_data='comment')


# Определение состояний
class Form(StatesGroup):
    name = State()
    description = State()
    comment = State()


class TGMessage:
    def __init__(self):
        self.user_id = None
        self.task_query = None
        self.comment_id = None

    async def start(self, message):
        self.user_id = message.chat.id

        db.CreateDB()
        db_state.CreateDB()
        db.InsertDB(self.user_id, mail='None', password='None', token='None')
        db_state.InsertDB(self.user_id)
        await bot.send_message(message.chat.id, 'Это бот сайта TeamFlame\n\n'
                                                'Для авторизации наберите /auth mail password\n\n'
                                                'Для регистрации наберите\n'
                                                '/reg\n'
                                                'Фамилия\n'
                                                'Имя\n'
                                                'Отчество\n'
                                                'Почта\n'
                                                'Пароль')

    async def auth(self, message):
        self.user_id = message.chat.id

        try:
            db.CreateDB()
            db_state.CreateDB()
            db.InsertDB(self.user_id, mail='None', password='None', token='None')
            db_state.InsertDB(self.user_id)

            data = message.text.split('/auth ')[1]
            data = data.split()
            if URLRequests(user_id=self.user_id).SignIn(data[0], data[1]) == 200:
                await bot.send_message(message.chat.id, 'Успешная авторизация:')
                await TGMessage.space(self, message)
            else:
                await bot.send_message(message.chat.id, 'Аккаунт не найден\n\n'
                                                        'Для регистрации наберите\n'
                                                        '/reg\n'
                                                        'Фамилия\n'
                                                        'Имя\n'
                                                        'Отчество\n'
                                                        'Почта\n'
                                                        'Пароль')
        except IndexError:
            await bot.send_message(message.chat.id, 'Неверный формат ввода')

    async def reg(self, message):
        self.user_id = message.chat.id

        try:
            db.CreateDB()
            db_state.CreateDB()
            db.InsertDB(self.user_id, mail='None', password='None', token='None')
            db_state.InsertDB(self.user_id)

            data = message.text.split('/reg')[1]
            data = data.split('\n')
            if URLRequests(user_id=self.user_id).SignUp(data[1], data[2], data[3], data[4], data[5]) == 200:
                await bot.send_message(message.chat.id, 'Успешная регистрация')
                await TGMessage.space(self, message)
            else:
                await bot.send_message(message.chat.id, 'Ошибка ввода данных')
        except IndexError:
            await bot.send_message(message.chat.id, 'Неверный формат ввода')

    async def space(self, message: types.Message):
        self.user_id = message.chat.id
        account = URLRequests(user_id=self.user_id)
        await bot.send_message(message.chat.id, 'Пространства:')
        i = 0
        for space in account.GetSpaces(0):
            if space['description']:
                open_space.callback_data = f'open_project_call/{i}'
                button_open_space = InlineKeyboardMarkup().add(open_space)
                await bot.send_message(message.chat.id, f"№{i + 1}\n\n"
                                                        f"Название:\n\n{space['name']}\n\n"
                                                        f"Описание:\n\n{space['description']}",
                                       reply_markup=button_open_space)
            else:
                open_space.callback_data = f'open_project_call/{i}'
                button_open_space = InlineKeyboardMarkup().add(open_space)
                await bot.send_message(message.chat.id, f"№{i + 1}\n\n"
                                                        f"Название:\n\n{space['name']}",
                                       reply_markup=button_open_space)
            i += 1

    async def process_callback_project(self, callback_query: types.CallbackQuery):
        try:
            self.user_id = callback_query.from_user.id
            account = URLRequests(user_id=self.user_id)

            data = callback_query.data.split('/')

            db_state.UpdateDB(self.user_id, 'space_num', data[1])
            num_space = db_state.SelectDB(self.user_id)[0]

            await bot.answer_callback_query(callback_query.id)

            account.GetSpaces(int(num_space))
            await bot.send_message(self.user_id, 'Проекты:')
            i = 0
            for project in account.GetProject(0):
                open_project.callback_data = f'open_board_call/{i}'
                button_project = InlineKeyboardMarkup().add(open_project)
                await bot.send_message(self.user_id, f"№{i + 1}\n\n"
                                                     f"Название:\n\n{project['name']}",
                                       reply_markup=button_project)
                i += 1
        except IndexError:
            await bot.send_message(self.user_id, 'Проектов нет')

    async def process_callback_board(self, callback_query: types.CallbackQuery):
        try:
            self.user_id = callback_query.from_user.id
            account = URLRequests(user_id=self.user_id)

            data = callback_query.data.split('/')

            db_state.UpdateDB(self.user_id, 'project_num', data[1])

            num_space = db_state.SelectDB(self.user_id)[0]
            num_project = db_state.SelectDB(self.user_id)[1]

            await bot.answer_callback_query(callback_query.id)

            account.GetSpaces(int(num_space))
            account.GetProject(int(num_project))

            await bot.send_message(self.user_id, 'Доски:')
            i = 0
            for board in account.GetBoard(0):
                open_task_list.callback_data = f'open_task_list_call/{i}'
                create_task.callback_data = f'create_task_call/{i}'
                button_board = InlineKeyboardMarkup().add(open_task_list).add(create_task)
                await bot.send_message(self.user_id, f"№{i + 1}\n\n"
                                                     f"Название:\n\n{board['name']}",
                                       reply_markup=button_board)
                i += 1
        except IndexError:
            await bot.send_message(self.user_id, 'Проектов нет')

    async def process_callback_task_list(self, callback_query: types.CallbackQuery):
        try:
            self.user_id = callback_query.from_user.id
            self.task_query = callback_query
            account = URLRequests(user_id=self.user_id)

            data = callback_query.data.split('/')

            db_state.UpdateDB(self.user_id, 'board_num', data[1])

            num_space = db_state.SelectDB(self.user_id)[0]
            num_project = db_state.SelectDB(self.user_id)[1]
            num_board = db_state.SelectDB(self.user_id)[2]

            await bot.send_message(self.user_id, '---------------------\n\n\n'
                                                 'Список Задач:'
                                                 '\n\n\n---------------------')
            account.GetSpaces(int(num_space))
            account.GetProject(int(num_project))
            account.GetBoard(int(num_board))
            num_task = 0
            num_coll = 0
            for board_task in account.GetTaskByBoard(0):
                await bot.send_message(self.user_id, f"-----------\n\n"
                                                     f"{board_task['name']}"
                                                     f"\n\n-----------")
                if board_task['name'] == 'Сделать':
                    task_btn = InlineKeyboardMarkup().row(
                        work_btn, success_btn, exit_btn
                    ).add(comment_btn)

                elif board_task['name'] == 'В работе':
                    task_btn = InlineKeyboardMarkup().row(
                        create_btn, success_btn, exit_btn
                    ).add(comment_btn)

                elif board_task['name'] == 'Готово':
                    task_btn = InlineKeyboardMarkup().row(
                        create_btn, work_btn, exit_btn
                    ).add(comment_btn)

                elif board_task['name'] == 'Закрыто':
                    task_btn = InlineKeyboardMarkup().row(
                        create_btn, work_btn, success_btn
                    ).add(comment_btn)

                if not board_task['tasks']:
                    await bot.send_message(self.user_id, "Задач нет")
                for task in board_task['tasks']:
                    create_btn.callback_data = f'create/{num_coll} {num_task}'
                    work_btn.callback_data = f'work/{num_coll} {num_task}'
                    success_btn.callback_data = f'success/{num_coll} {num_task}'
                    exit_btn.callback_data = f'exit/{num_coll} {num_task}'
                    comment_btn.callback_data = f'comment/{num_coll} {num_task}'

                    if task['description']:
                        await bot.send_message(self.user_id, f"Название:\n\n{task['name']}\n\n"
                                                             f"Описание:\n\n{task['description']}",
                                               reply_markup=task_btn)
                    else:
                        await bot.send_message(self.user_id, f"Название:\n\n{task['name']}",
                                               reply_markup=task_btn)
                    num_task += 1
                num_task = 0
                num_coll += 1
        except IndexError:
            await bot.send_message(self.user_id, 'Нет списка для Задача')

    async def process_callback_create_task(self, callback_query: types.CallbackQuery):
        self.user_id = callback_query.from_user.id

        await Form.name.set()
        await bot.send_message(self.user_id, f"Введите Название")

    async def process_name(self, message: types.Message, state: FSMContext):
        # Получаем введенные данные
        async with state.proxy() as data:
            data['name'] = message.text

        # Переход ко второму шагу
        await Form.description.set()
        await bot.send_message(self.user_id, f"Введите Описание")

    async def process_description(self, message: types.Message, state: FSMContext):
        self.user_id = message.chat.id
        account = URLRequests(user_id=self.user_id)

        num_space = db_state.SelectDB(self.user_id)[0]
        num_project = db_state.SelectDB(self.user_id)[1]
        num_board = db_state.SelectDB(self.user_id)[2]

        account.GetSpaces(int(num_space))
        account.GetProject(int(num_project))
        account.GetBoard(int(num_board))

        # Получаем введенные данные
        async with state.proxy() as data:
            data['description'] = message.text

        if account.PostCreateTask(data['name'], data['description']) == 201:
            await bot.send_message(self.user_id, "Задача добавлена")
            await TGMessage.process_callback_task_list(self, self.task_query)

        # Завершаем состояние
        await state.finish()

    async def process_callback_comment(self, callback_query: types.CallbackQuery):
        self.user_id = callback_query.from_user.id

        self.comment_id = callback_query.data.split('/')[1].split()

        await Form.comment.set()
        await bot.send_message(self.user_id, f"Введите Комментарий")

    async def process_comment(self, message: types.Message, state: FSMContext):
        self.user_id = message.chat.id
        account = URLRequests(user_id=self.user_id)

        num_space = db_state.SelectDB(self.user_id)[0]
        num_project = db_state.SelectDB(self.user_id)[1]
        num_board = db_state.SelectDB(self.user_id)[2]

        # Получаем введенные данные
        async with state.proxy() as data:
            data['comment'] = message.text

        account.GetSpaces(int(num_space))
        account.GetProject(int(num_project))
        account.GetBoard(int(num_board))
        account.GetTaskByBoard(int(self.comment_id[0]))

        if account.PostComment(int(self.comment_id[1]), data['comment']) == 201:
            await bot.send_message(self.user_id, f"Комментарий добавлен")

        # Завершаем состояние
        await state.finish()

    async def process_callback_create(self, callback_query: types.CallbackQuery):
        TGMessage.change_desk(self, callback_query, 0)
        await TGMessage.process_callback_task_list(self, self.task_query)

    async def process_callback_work(self, callback_query: types.CallbackQuery):
        TGMessage.change_desk(self, callback_query, 1)
        await TGMessage.process_callback_task_list(self, self.task_query)

    async def process_callback_success(self, callback_query: types.CallbackQuery):
        TGMessage.change_desk(self, callback_query, 2)
        await TGMessage.process_callback_task_list(self, self.task_query)

    async def process_callback_exit(self, callback_query: types.CallbackQuery):
        TGMessage.change_desk(self, callback_query, 3)
        await TGMessage.process_callback_task_list(self, self.task_query)

    def change_desk(self, callback_query, change_coll_num):
        self.user_id = callback_query.from_user.id
        account = URLRequests(user_id=self.user_id)

        data = callback_query.data.split('/')[1]
        data = data.split()

        num_space = db_state.SelectDB(self.user_id)[0]
        num_project = db_state.SelectDB(self.user_id)[1]
        num_board = db_state.SelectDB(self.user_id)[2]

        account.GetSpaces(int(num_space))
        account.GetProject(int(num_project))
        account.GetBoard(int(num_board))
        account.GetTaskByBoard(int(data[0]))
        account.PostTaskChangeColumn(int(data[1]), change_coll_num)


tg_message_handler = TGMessage()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_func(message: types.Message):
    await tg_message_handler.start(message)


# Обработчик команды /space
@dp.message_handler(commands=['space'])
async def help_func(message: types.Message):
    await tg_message_handler.space(message)


# Обработчик команды /auth
@dp.message_handler(commands=['auth'])
async def auth_func(message: types.Message):
    await tg_message_handler.auth(message)


# Обработчик команды /reg
@dp.message_handler(commands=['reg'])
async def reg_func(message: types.Message):
    await tg_message_handler.reg(message)


# Обработчик выбора Проекта
@dp.callback_query_handler(lambda c: c.data.startswith('open_project_call'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_project(callback_query)


# Обработчик выбора Доски
@dp.callback_query_handler(lambda c: c.data.startswith('open_board_call'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_board(callback_query)


# Обработчик выбора Списка задач
@dp.callback_query_handler(lambda c: c.data.startswith('open_task_list_call'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_task_list(callback_query)


# Обработчик создания Задачи
@dp.callback_query_handler(lambda c: c.data.startswith('create_task_call'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_create_task(callback_query)


# Обработчик для имени Таска
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await tg_message_handler.process_name(message, state)


# Обработчик для описания Таска
@dp.message_handler(state=Form.description)
async def process_description(message: types.Message, state: FSMContext):
    await tg_message_handler.process_description(message, state)


# Обработчик для создания Комментария
@dp.message_handler(state=Form.comment)
async def process_description(message: types.Message, state: FSMContext):
    await tg_message_handler.process_comment(message, state)


@dp.callback_query_handler(lambda c: c.data.startswith('create'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_create(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith('work'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_work(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith('success'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_success(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith('exit'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_exit(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith('comment'))
async def process_callback_button(callback_query: types.CallbackQuery):
    await tg_message_handler.process_callback_comment(callback_query)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
