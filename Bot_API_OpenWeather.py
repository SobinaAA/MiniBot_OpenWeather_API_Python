# -*- coding: utf-8 -*-
#Импорт библиотек
import telebot
from telebot import types #Кнопочки
import requests #Здесь и ниже импорт библиотек для работы с API Яндекс
import pandas as pd
#Глобальные переменные (от них надо будет избавиться)
bot = telebot.TeleBot('6259779371:AAF4cndZ_Nhg8nAga0E5OSXDj5BI8loQZik')
df = pd.read_csv('BD.csv', sep = ';')
url = "https://api.openweathermap.org/data/2.5/weather?" #lat={lat}&lon={lon}&appid={API key}
API_KEY_ow = ''
@bot.message_handler(commands=['start', 'stop'], content_types=['text'])
#Стартовая функция
def start(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, text=f'Привет, {message.from_user.username}! Этот бот поможет определиться, как одеть ребенка!')
        bot.send_message(message.chat.id, "Напишите возраст ребенка в месяцах (от 0 до 36), числом.")
        bot.register_next_step_handler(message, get_age) #Следующая функция - запись возраста.
    else:
        bot.send_message(message.chat.id, "Нажмите /start, пожалуйста!")
def get_age(message):
    if message.text.isdigit():
        age = int(message.text)     
        if age > 36 or age < 0:
            bot.send_message(message.from_user.id, "Необходимо ввести число от 0 до 36 (от 0 до 3 лет). Чтобы начать заново, нажмите /start.")
            bot.register_next_step_handler(message, start)
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
            keyboard.add(button_geo)
            bot.send_message(message.chat.id, "Отправьте Ваше местоположение, чтобы можно было уточнить погодные условия (доступно только в мобильной версиии приложения).", reply_markup=keyboard)
            bot.register_next_step_handler(message, make_dec, age)
    else:
        bot.send_message(message.from_user.id, "Вводите только числа, пожалуйста. Чтобы начать заново, нажмите /start.")
        bot.register_next_step_handler(message, start)
def make_dec(message, age):
    a = telebot.types.ReplyKeyboardRemove()
    params = dict(appid = API_KEY_ow, lat = str(message.location.latitude), lon = str(message.location.longitude), lang = 'ru')
    r = requests.get(url, params)
    data = r.json() if r and r.status_code == 200 else None
    temp_C = int(data['main']['temp']) - 273
    humid = int(data['main']['humidity'])
    temp_feel = int(data['main']['feels_like']) - 273
    wind = data['wind']['speed']
    char = data['weather'][0]
    char = char['id']   
    bot.send_message(message.from_user.id, 'Сейчас за окном ' + str(temp_C) + '*C (ощущается как ' + str(temp_feel) +'*C). Ветер - ' + str(wind) + ' м/с. Влажность ' + str(humid) + '%.'+' Предлагаем ориентироваться на такой комплект одежды:', reply_markup=a)
    answer = df.copy()  
    answer = answer[answer["Age"] == age]
    answer = answer[str(temp_feel)] #Для проверки сразу данные
    answer = answer.iloc[0]
    bot.send_message(message.chat.id, str(answer))
    photo = open('123.JPG', 'rb')
    bot.send_photo(message.chat.id, photo)
    bot.register_next_step_handler(message, start)
def stop(message): 
    bot.stop_bot()
#Зациклили бот
bot.polling(none_stop=True, interval=3)