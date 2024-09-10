import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
# Токен вашего бота
TOKEN = '7012578157:AAG7js8XPgV87HHnJ5tZuH0ucHOTF0LBDfo'
bot = telebot.TeleBot(TOKEN)


# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('config.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/19V05KtEFZiyHVWUoKfWMjuMu1ut_DlCr3-DhXH-f3ak/edit').sheet1

# Основное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Инструкция по регистрации'))
    markup.add(types.KeyboardButton('Зарегистрироваться'))
    markup.add(types.KeyboardButton('Информация о мероприятии'))
    markup.add(types.KeyboardButton('Часто задаваемые вопросы'))
    markup.add(types.KeyboardButton('Обратиться в поддержку'))
    return markup

# Начальная команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Здесь вы можете узнать всю актуальную информацию, а также зарегистрироваться на семейный фестиваль по рыбной ловле, который состоится 14 сентября в Москве", reply_markup=main_menu())

# Обработка нажатия кнопок
@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    if message.text == 'Инструкция по регистрации':
        instruction(message)
    elif message.text == 'Зарегистрироваться':
        start_registration(message)
    elif message.text == 'Информация о мероприятии':
        event_info_menu(message)
    elif message.text == 'Часто задаваемые вопросы':
        faq(message)
    elif message.text == 'Обратиться в поддержку':
        support(message)
    elif message.text == 'Дата и время проведения':
        event_date_time(message)
    elif message.text == 'Место проведения':
        event_location(message)
    elif message.text == 'Программа мероприятия':
        event_program(message)
    elif message.text == 'Назад':
        go_back(message)

# Инструкция по регистрации
def instruction(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Зарегистрироваться'))
    markup.add(types.KeyboardButton('Назад'))

    info_text = (
        "Чтобы попасть на фестиваль, необходимо зарегистрироваться в этом телеграм боте. Необходимо будет указать:\n"
                                      
        "1. ФИО главы семьи полностью \n"
        "(в формате: Иванов Иван Иванович)\n"
        "2. Колличество участников\n"
        "3. Возраста всех участников \n(например: 35,33,10)\n"
        "4. Номер телефона\n"
        "5. Электронную почту\n"
    )
    bot.send_message(message.chat.id, info_text, reply_markup=markup)


# Обработка нажатия кнопки "Назад"
def go_back(message):
    bot.send_message(message.chat.id, "Возвращаемся в меню.", reply_markup=main_menu())

# Начало регистрации
def start_registration(message):
    msg = bot.send_message(message.chat.id, "Введите ФИО главы семьи:")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    user_data = {'name': message.text}
    msg = bot.send_message(message.chat.id, "Введите количество участников:")
    bot.register_next_step_handler(msg, get_members, user_data)

def get_members(message, user_data):
    user_data['members'] = message.text
    msg = bot.send_message(message.chat.id, "Введите возраст участников:")
    bot.register_next_step_handler(msg, get_age, user_data)

def get_age(message, user_data):
    user_data['age'] = message.text
    msg = bot.send_message(message.chat.id, "Введите контактный телефон:")
    bot.register_next_step_handler(msg, get_phone, user_data)

def get_phone(message, user_data):
    user_data['phone'] = message.text
    msg = bot.send_message(message.chat.id, "Введите адрес электронной почты:")
    bot.register_next_step_handler(msg, get_email, user_data)

def get_email(message, user_data):
    user_data['email'] = message.text

    # Подтверждение регистрации
    confirmation_text = (
        f"Проверьте введенные данные:\n"
        f"ФИО главы семьи: {user_data['name']}\n"
        f"Количество участников: {user_data['members']}\n"
        f"Возраст участников: {user_data['age']}\n"
        f"Контактный телефон: {user_data['phone']}\n"
        f"Адрес электронной почты: {user_data['email']}"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Подтвердить регистрацию'), types.KeyboardButton('Редактировать данные'))
    bot.send_message(message.chat.id, confirmation_text, reply_markup=markup)

    # Сохранение данных для дальнейшего использования
    bot.register_next_step_handler(message, confirm_registration, user_data)

def confirm_registration(message, user_data):
    if message.text == 'Подтвердить регистрацию':
        # Сохранение данных в Google Sheets
        new_row = [
            message.from_user.id,
            user_data['name'],
            user_data['members'],
            user_data['age'],
            user_data['phone'],
            user_data['email']
        ]
        sheet.append_row(new_row)
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались! Ждем вас на фестивале", reply_markup=main_menu())
    elif message.text == 'Редактировать данные':
        edit_data_menu(message, user_data)

# Меню для редактирования данных
def edit_data_menu(message, user_data):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('ФИО главы семьи'), types.KeyboardButton('Количество участников'))
    markup.add(types.KeyboardButton('Возраст участников'), types.KeyboardButton('Контактный телефон'))
    markup.add(types.KeyboardButton('Адрес электронной почты'), types.KeyboardButton('Зарегистрироваться'))
    bot.send_message(message.chat.id, "Выберите данные для редактирования:", reply_markup=markup)
    bot.register_next_step_handler(message, edit_data, user_data)

def edit_data(message, user_data):
    if message.text == 'ФИО главы семьи':
        msg = bot.send_message(message.chat.id, "Введите новое ФИО главы семьи:")
        bot.register_next_step_handler(msg, update_name, user_data)
    elif message.text == 'Количество участников':
        msg = bot.send_message(message.chat.id, "Введите новое количество участников:")
        bot.register_next_step_handler(msg, update_members, user_data)
    elif message.text == 'Возраст участников':
        msg = bot.send_message(message.chat.id, "Введите новый возраст участников:")
        bot.register_next_step_handler(msg, update_age, user_data)
    elif message.text == 'Контактный телефон':
        msg = bot.send_message(message.chat.id, "Введите новый контактный телефон:")
        bot.register_next_step_handler(msg, update_phone, user_data)
    elif message.text == 'Адрес электронной почты':
        msg = bot.send_message(message.chat.id, "Введите новый адрес электронной почты:")
        bot.register_next_step_handler(msg, update_email, user_data)
    elif message.text == 'Зарегистрироваться':
        new_row = [
            message.from_user.id,
            user_data['name'],
            user_data['members'],
            user_data['age'],
            user_data['phone'],
            user_data['email']
        ]
        sheet.append_row(new_row)
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались! Ждем вас на фестивале",
                         reply_markup=main_menu())

def update_name(message, user_data):
    user_data['name'] = message.text
    edit_data_menu(message, user_data)

def update_members(message, user_data):
    user_data['members'] = message.text
    edit_data_menu(message, user_data)

def update_age(message, user_data):
    user_data['age'] = message.text
    edit_data_menu(message, user_data)

def update_phone(message, user_data):
    user_data['phone'] = message.text
    edit_data_menu(message, user_data)


def update_email(message, user_data):
    user_data['email'] = message.text
    edit_data_menu(message, user_data)

# Информация о мероприятии
def event_info_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Дата и время проведения'))
    markup.add(types.KeyboardButton('Место проведения'))
    markup.add(types.KeyboardButton('Программа мероприятия'))
    markup.add(types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, "Выберите интересующую вас информацию:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Дата и время проведения')
def event_date_time(message):
    bot.send_message(message.chat.id, "14 сентября, суббота, с 10:00 до 15:00")

@bot.message_handler(func=lambda message: message.text == 'Место проведения')
def event_location(message):
    bot.send_message(message.chat.id, "Центр Петра Великого. Ленинградское шоссе, 45, строение 3, Москва, метро Водный стадион")

@bot.message_handler(func=lambda message: message.text == 'Программа мероприятия')
def event_program(message):
    program_text = (
        "1. 08:00 - 09:00 — Встреча участников. Распределение по командам.\n"
        "2. 09:00 - 09:30 — Официальное открытие фестиваля. Приветственное слово от организаторов.\n"
        "3. 9:30 - 16:00 — Проведение мастер-классов на тематику рыбной ловли.\n"
        "4. 9:30 - 16:00 — Игры и развлечения для детей, рыболовная викторина.\n"
        "5. 9:30 - 16:00 — Свободная рыбалка и конкурсы.\n"
        "6. 16:30 — Подведение итогов.\n"
        "7. 16:55 — Закрытие фестиваля\n"
    )
    bot.send_message(message.chat.id, program_text)

# Часто задаваемые вопросы
def faq(message):
    faq_text = (
        "1. Как зарегистрироваться на фестиваль? - Используйте кнопку 'Зарегистрироваться' в главном меню.\n"
        "2. Какое снаряжение нужно взять с собой? - Вся необходимая рыболовная оснастка будет предоставлена.\n"
        "3. Могу ли я участвовать, если никогда не ловил рыбу? - Да, на фестивале будут проводиться мастер-классы для начинающих.\n"
        "4. Что будет на мероприятии? - Вы можете посмотреть программу фестиваля в разделе Инфомрация о мероприятии\n"
        "5. Будут ли призы? - Будут вручаться памятные медали и благодарности за участие\n"
    )
    bot.send_message(message.chat.id, faq_text)

# Обратная связь с поддержкой
def support(message):
    bot.send_message(message.chat.id, "Пожалуйста, напишите свой вопрос. Мы передадим его организаторам.")
    bot.register_next_step_handler(message, forward_to_support)

def forward_to_support(message):
    # Получаем никнейм пользователя или имя, если никнейм не задан
    username = message.from_user.username
    if not username:
        username = message.from_user.first_name

    # Формируем текст сообщения с никнеймом
    forward_text = f"Сообщение от @{username}:\n\n{message.text}"

    # Отправляем сообщение с никнеймом в группу
    bot.send_message(-4143855626, forward_text)

    # Подтверждение пользователю
    bot.send_message(message.chat.id, "Ваш вопрос отправлен организаторам. Ожидайте ответа.")



bot.polling()
