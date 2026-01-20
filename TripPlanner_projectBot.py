import os
import telebot
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ Токен не найден в .env файле")
    print("📝 Создайте .env с содержимым: TOKEN=ваш_токен")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Данные городов [Янв, Фев, Мар, Апр, Май, Июн, Июл, Авг, Сен, Окт, Ноя, Дек]
DATA = {
    "санкт-петербург": [-6, -5, -1, 5, 12, 16, 18, 17, 12, 6, 1, -3],
    "сочи": [6, 6, 8, 12, 17, 21, 24, 24, 21, 16, 12, 8],
    "владивосток": [-12, -10, -3, 5, 11, 15, 20, 21, 17, 10, 0, -9],
    "калининград": [-1, -1, 2, 7, 13, 17, 19, 19, 14, 9, 4, 0],
    "махачкала": [2, 2, 5, 11, 17, 22, 25, 25, 20, 14, 8, 4],
}


@bot.message_handler(commands=["start"])
def start(message):
    text = """👋 *Travel Bot*
    
📋 Команды:
/start - начало
/help - помощь  
/cities - города
/recommend город месяц - рекомендация
/best город - лучшие месяцы

*Пример:* /recommend Сочи 7"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def help(message):
    text = """📋 *Доступные команды:*
/start - начало
/cities - города
/recommend город месяц - рекомендация
/best город - лучшие месяцы

*Города:* СПб, Сочи, Владивосток, Калининград, Махачкала"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["cities"])
def cities(message):
    cities = "\n".join([f"• {c.title()}" for c in DATA.keys()])
    bot.send_message(message.chat.id, f"🏙️ *Города:*\n{cities}", parse_mode="Markdown")


@bot.message_handler(commands=["recommend"])
def recommend(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Используйте: /recommend город месяц")
            return

        city = parts[1].lower()
        month = int(parts[2])

        if month < 1 or month > 12:
            bot.send_message(message.chat.id, "❌ Месяц 1-12")
            return

        if city not in DATA:
            bot.send_message(message.chat.id, "❌ Город не найден")
            return

        temp = DATA[city][month - 1]
        months_ru = [
            "Янв",
            "Фев",
            "Мар",
            "Апр",
            "Май",
            "Июн",
            "Июл",
            "Авг",
            "Сен",
            "Окт",
            "Ноя",
            "Дек",
        ]

        # Тип отдыха
        if temp > 20 and month in [6, 7, 8]:
            vacation = "🏖️ Пляжный"
        elif 10 <= temp <= 25 and month in [5, 6, 9]:
            vacation = "🏛️ Экскурсионный"
        elif temp < 0 and month in [12, 1, 2]:
            vacation = "⛷️ Горнолыжный"
        else:
            vacation = "🏙️ Городской"

        # Одежда
        if temp > 20:
            clothes = "👕 Легкая одежда"
        elif temp > 10:
            clothes = "🧥 Демисезон"
        elif temp > 0:
            clothes = "🧥 Куртка"
        else:
            clothes = "🧥 Зимняя"

        text = f"""📊 *{city.title()} в {months_ru[month-1]}:*
🌡️ {temp}°C
🎯 {vacation}
👕 {clothes}"""

        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    except:
        bot.send_message(message.chat.id, "❌ Ошибка")


@bot.message_handler(commands=["best"])
def best(message):
    try:
        city = message.text.split()[1].lower()

        if city not in DATA:
            bot.send_message(message.chat.id, "❌ Город не найден")
            return

        # Месяцы с температурой 18-28°C
        best_months = []
        months_ru = [
            "Янв",
            "Фев",
            "Мар",
            "Апр",
            "Май",
            "Июн",
            "Июл",
            "Авг",
            "Сен",
            "Окт",
            "Ноя",
            "Дек",
        ]

        for i, temp in enumerate(DATA[city]):
            if 18 <= temp <= 28:
                best_months.append(months_ru[i])

        if best_months:
            text = f"✅ {city.title()}: {', '.join(best_months)}"
        else:
            text = f"ℹ️ Для {city.title()} нет ярких сезонов"

        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    except:
        bot.send_message(message.chat.id, "❌ Используйте: /best город")


# Запуск
print("🤖 Бот запущен")
bot.polling()

## 1. Установите зависимости
# pip install python-telegram-bot pandas python-dotenv

# 2. Создайте .env файл с токеном
# echo "TOKEN" > .env

# Ctrl + C - остановить
