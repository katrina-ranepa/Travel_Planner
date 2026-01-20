from dotenv import load_dotenv
import os
import telebot 
import pandas as pd
from datetime import datetime

def get_token():
    """Загружает токен только из .env файла"""
    # Загружаем переменные из .env
    load_dotenv()
    
    # Получаем токен
    token = os.getenv("TOKEN")
    
    if not token:
        raise ValueError("❌ Токен не найден в .env файле. Создайте файл .env с содержимым: TOKEN=ваш_токен")
    
    return token.strip()

# Использование
try:
    TOKEN = get_token()
    print(f"✅ Токен загружен: {TOKEN[:10]}...")
except ValueError as e:
    print(e)
    exit(1)


# Загрузка данных
try:
    df = pd.read_csv("weather_daily_all_cities.csv")#загрузка данныхх
    df["Дата"] = pd.to_datetime(df["Дата"])
except:
    df = pd.DataFrame()

# Функции
def get_weather_info(city, month):
    cities_data = {
        "санкт-петербург": [-6, -5, -1, 5, 12, 16, 18, 17, 12, 6, 1, -3],
        "сочи":           [6, 6, 8, 12, 17, 21, 24, 24, 21, 16, 12, 8],  
        "владивосток":    [-12, -10, -3, 5, 11, 15, 20, 21, 17, 10, 0, -9],
        "калининград":    [-1, -1, 2, 7, 13, 17, 19, 19, 14, 9, 4, 0],
        "махачкала":      [2, 2, 5, 11, 17, 22, 25, 25, 20, 14, 8, 4]
    }
        # Приводим город к нижнему регистру
    city_lower = city.lower().strip()
    
    # Проверяем разные варианты написания
    if city_lower == "cочи":  # если английская C
        city_lower = "сочи"
    
    if city_lower in cities_data:
        if 1 <= month <= 12:
            temp = cities_data[city_lower][month-1]
            return f"Средняя температура: {temp}°C", temp
    
    return "Нет данных", None


def get_vacation_type(temp, month):
    """Определение типа отдыха"""
    if temp is None:
        return "🎭 Разный"
    
    if 20 <= temp <= 32 and month in [6, 7, 8]:
        return "🏖️ Пляжный"
    elif 10 <= temp <= 25 and month in [5, 6, 9]:
        return "🏛️ Экскурсионный"
    elif -10 <= temp <= -2 and month in [12, 1, 2]:
        return "⛷️ Горнолыжный"
    elif 5 <= temp <= 25 and month in [4, 5, 6, 9, 10]:
        return "🏙️ Городской"
    else:
        return "🎭 Разный"

# Обработчики команд
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🏙️ Список городов")
    btn2 = telebot.types.KeyboardButton("📅 Рекомендации")
    btn3 = telebot.types.KeyboardButton("ℹ️ Помощь")
    markup.add(btn1, btn2, btn3)
    
    welcome_text = """
👋 Привет! Я бот для рекомендаций путешествий по России.

✨ Что я умею:
• Показывать погоду в городах
• Давать рекомендации по отдыху
• Подбирать лучшие месяцы для поездки

📌 Используйте кнопки меню или команды:
/start - Начать
/cities - Список городов
/recommend - Рекомендации
/help - Помощь
    """
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📋 Доступные команды:
/start - Начать работу
/cities - Показать список городов
/recommend [город] [месяц] - Рекомендации
  Пример: /recommend Сочи 7
/best [город] - Лучшие месяцы для города
/help - Эта справка

🎭 Типы отдыха:
🏖️ Пляжный (20-32°C) - июнь-август
🏛️ Экскурсионный (10-25°C) - май, июнь, сентябрь
⛷️ Горнолыжный (-10...-2°C) - декабрь-февраль
🏙️ Городской (5-25°C) - апрель-июнь, сентябрь-октябрь
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['cities'])
def send_cities(message):
    if df.empty:
        cities = ["Санкт-Петербург", "Сочи", "Владивосток", "Калининград", "Махачкала"]
    else:
        cities = sorted(df["Город"].unique().tolist())
    
    cities_text = "🏙️ Доступные города:\n" + "\n".join([f"• {city}" for city in cities])
    bot.send_message(message.chat.id, cities_text)

@bot.message_handler(commands=['recommend'])
def send_recommendation(message):
    try:
        # Парсим команду /recommend город месяц
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "❌ Используйте: /recommend [город] [месяц]")
            return
        
        city = parts[1]
        month = int(parts[2])
        
        if month < 1 or month > 12:
            bot.send_message(message.chat.id, "❌ Месяц должен быть от 1 до 12")
            return
        
        # Получаем данные
        weather_info, temp = get_weather_info(city, month)
        vacation_type = get_vacation_type(temp, month)
        
        # Формируем ответ
        months_ru = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        
        response = f"""
📊 Рекомендация для {city} в {months_ru[month-1]}:

{weather_info}
🎯 Тип отдыха: {vacation_type}

📌 Рекомендации по одежде:
"""
        if temp is not None:
            if temp > 20:
                response += "• Легкая одежда\n• Головной убор\n• Солнцезащитные очки"
            elif temp > 10:
                response += "• Демисезонная одежда\n• Ветровка\n• Зонт"
            elif temp > 0:
                response += "• Теплая куртка\n• Шапка\n• Перчатки"
            else:
                response += "• Зимняя одежда\n• Термобелье\n• Теплая обувь"
        
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['best'])
def send_best_months(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "❌ Используйте: /best [город]")
            return
        
        city = parts[1]
        
        if df.empty:
            # Примерные данные для демо
            response = f"""
🏆 Лучшие месяцы для {city}:

🏖️ Пляжный отдых: Июнь, Июль, Август
🏛️ Экскурсионный: Май, Июнь, Сентябрь
⛷️ Горнолыжный: Декабрь, Январь, Февраль
🏙️ Городской: Апрель-Октябрь
            """
        else:
            # Анализируем реальные данные
            best_months = []
            for month in range(1, 13):
                _, temp = get_weather_info(city, month)
                if temp is not None:
                    if 18 <= temp <= 28:
                        best_months.append(month)
            
            months_ru = ["январь", "февраль", "март", "апрель", "май", "июнь",
                        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
            
            if best_months:
                best_list = ", ".join([months_ru[m-1] for m in best_months])
                response = f"✅ Лучшие месяцы для поездки в {city}: {best_list}"
            else:
                response = f"ℹ️ Для {city} нет ярко выраженных лучших месяцев"
        
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    if text == "🏙️ Список городов":
        send_cities(message)
    
    elif text == "📅 Рекомендации":
        bot.send_message(message.chat.id, 
            "📝 Введите команду:\n/recommend [город] [месяц]\n\nПример: /recommend Сочи 7")
    
    elif text == "ℹ️ Помощь":
        send_help(message)
    
    elif text.startswith("Рекомендация для"):
        # Пример обработки свободного ввода
        try:
            parts = text.split(" ")
            city = parts[2]
            month = int(parts[4])
            
            # Имитируем команду
            fake_message = type('obj', (object,), {'text': f'/recommend {city} {month}', 
                                                  'chat': message.chat})
            send_recommendation(fake_message)
        except:
            bot.send_message(message.chat.id, "❌ Не понимаю. Используйте команды из меню.")
    
    else:
        bot.send_message(message.chat.id, 
            "🤔 Не понял запрос. Используйте кнопки меню или команды:\n"
            "/start - Начать\n"
            "/help - Помощь")

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.polling(none_stop=True)


## 1. Установите зависимости
# pip install python-telegram-bot pandas python-dotenv

# 2. Создайте .env файл с токеном
# echo "TOKEN" > .env

# Ctrl + C - остановить
