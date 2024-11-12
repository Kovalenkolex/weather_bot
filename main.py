import types
import telebot
from telebot import types
import sqlite3
import openmeteo_requests
from openmeteo_sdk.Variable import Variable
import os


bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
place_name1 = ''
la = ''
lo = ''


def weather(lati, longi):
    # Запрос к api openmeteo
    om = openmeteo_requests.Client()
    params = {
        "latitude": {lati},
        "longitude": {longi},
        "current": ["temperature_2m"]
    }
    responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]
    current = response.Current()
    current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))
    current_temperature_2m = next(
        filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, current_variables))
    return current_temperature_2m.Value()


def latitude(message):
    # Прием широты и запрос долготы у пользователя
    global la
    la = message.text.strip()
    bot.send_message(message.chat.id, 'Введите долготу, используя точку как разделитель\n'
                                      'Например 12.123 (значение от -180 до 180):')
    bot.register_next_step_handler(message, longitude)


def longitude(message):
    # Прием долготы у пользователя и вывод температуры в точке
    global lo
    global la
    lo = message.text.strip()
    bot.send_message(message.chat.id, f'Там сейчас {round(weather(la, lo))} ℃')
    # Кнопки с вопросом
    mark = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да', callback_data='yes')
    btn2 = types.InlineKeyboardButton('Нет', callback_data='no')
    mark.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Сохранить это место?', reply_markup=mark)


def save_place(message):
    # Сохранение места в базу данных и вывод инфы польз-лю
    place_name1 = message.text.strip()
    # conn = sqlite3.connect('basa.sql')
    conn = sqlite3.connect('/sql/basa.sql')
    cur = conn.cursor()
    update_statement = 'UPDATE users SET latitude=?, longitude=?, place_name=? WHERE tg_id = ?'
    cur.execute(update_statement, (la, lo, place_name1, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Сохранено место "{place_name1}" с координатами: \n'
                                      f'Широта {la}, долгота {lo}.\n'
                                      f'Чтобы получить информацию о погоде там, введите /weather')


@bot.message_handler(commands=['start', 'main'])
def start(message):
    # Создание БД при запуске бота (при её отсутствии)
    # conn = sqlite3.connect('basa.sql')
    conn = sqlite3.connect('/sql/basa.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (tg_id int, first_name varchar(50), last_name varchar(50),'
                'latitude float, longitude float, place_name varchar(50), payment int DEFAULT 0)')
    cur.execute('SELECT tg_id FROM users')
    tgid = cur.fetchall()
    # Добавление инфы про пользователя в БД
    ids = str(tgid)[1:-1].replace('(', '').replace(')',
                                                   '').replace(',', '').split(' ')
    if ids == ['']:
        int_ids = [None]
    else:
        int_ids = [int(item) for item in ids]
    if message.from_user.id in int_ids:
        pass
    else:
        cur.execute('INSERT INTO users (tg_id, first_name, last_name) VALUES (?, ?, ?)',
                (message.from_user.id, message.from_user.first_name, message.from_user.last_name))
    
    # Вывод стартовых кнопок и надписи
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Санкт-Петербург', callback_data='spb')
    btn2 = types.InlineKeyboardButton('Москва', callback_data='msk')
    markup.row(btn1, btn2)
    btn3 = types.InlineKeyboardButton('Тольятти', callback_data='tlt')
    btn4 = types.InlineKeyboardButton('Другое место', callback_data='else')
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'Привет! Чтобы получить информацию о погоде, выберите город:', reply_markup=markup)


@bot.message_handler(commands=['weather'])
def home_weather(message):
    # Отображение погоды в сохраненном месте
    # conn = sqlite3.connect('basa.sql')
    conn = sqlite3.connect('/sql/basa.sql')
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude, place_name FROM users WHERE tg_id=?", (message.from_user.id,))
    result = cur.fetchone()
    if result:
        latitude_value, longitude_value, place_name = result
        if latitude_value is None or longitude_value is None:
            # Если широты или долготы нет, запуск latitude
            bot.send_message(message.chat.id, 'Сохраненного места нет, давайте это исправим. '
                                                       'Укажите координаты места.\n'
                                                       'Сначала введите широту, используя точку как разделитель \n'
                                                       'Например 12.123 (значение от -90 до 90):')
            bot.register_next_step_handler(message, latitude)
        else:
            bot.send_message(message.chat.id, f'Сохраненное место "{place_name}", '
                                              f'координаты: широта {latitude_value}, долгота {longitude_value} \n'
                                              f'Там сейчас {round(weather(latitude_value, longitude_value))} ℃')
    else:
        bot.send_message(message.chat.id, 'Сохраненного места нет, давайте это исправим. '
                                          'Укажите координаты места.\n'
                                          'Сначала введите широту, используя точку как разделитель \n'
                                          'Например 12.123 (значение от -90 до 90):')
        bot.register_next_step_handler(message, latitude)


@bot.message_handler(commands=['sethome'])
def sethome(message):
    # Запуск сохранения места
    bot.send_message(message.chat.id, 'Укажите координаты места.\n'
                                      'Сначала введите широту, используя точку как разделитель \n'
                                      'Например 12.123 (значение от -90 до 90):')
    bot.register_next_step_handler(message, latitude)


@bot.message_handler(commands=['help'])
def help(message):
    # Отображение доп инф
    bot.send_message(message.chat.id, '<b>Помощь с ботом:</b> \n'
                                      'Знаю команды Привет, /weather, /sethome \n'
                                      '<em>Если что-то пошло не так, и бот перестал отвечать, '
                                      'введите еще раз команду /start</em>', parse_mode='html')



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    # Действия при нажатии на стартовые кнопки
    global la
    global lo
    if callback.data == 'msk':
        la = 55.7522
        lo = 37.6156
        bot.send_message(callback.message.chat.id, f'В Москве сейчас {round(weather(la, lo))} ℃')
    elif callback.data == 'tlt':
        la = 53.5303
        lo = 49.3461
        bot.send_message(callback.message.chat.id, f'В Тольятти сейчас {round(weather(la,lo))} ℃')
    elif callback.data == 'spb':
        la = 59.9386
        lo = 30.3141
        bot.send_message(callback.message.chat.id, f'В Санкт-Петербурге сейчас {round(weather(la, lo))} ℃')
    elif callback.data == 'else':
        bot.send_message(callback.message.chat.id, 'Укажите координаты места.\n'
                                                    'Сначала введите широту, используя точку как разделитель \n'
                                                   'Например 12.123 (значение от -90 до 90):')
        bot.register_next_step_handler(callback.message, latitude)
    elif callback.data == 'yes':
        bot.send_message(callback.message.chat.id, 'Введите название для этого места:')
        bot.register_next_step_handler(callback.message, save_place)
    elif callback.data == 'no':
        bot.send_message(callback.message.chat.id, 'Окей, не сохраняем')


@bot.message_handler()
def greet(message):
    # В случае рукописного текста
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!')
    else:
        bot.send_message(message.chat.id, 'Я не знаю такую команду, попробуй другую')


bot.polling(non_stop=True)