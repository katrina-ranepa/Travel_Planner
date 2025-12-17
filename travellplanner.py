import requests
from bs4 import BeautifulSoup


def get_weather(city):
    """Получить погоду для города"""
    # Формируем URL для города
    url = f"https://world-weather.ru/pogoda/russia/{city.lower()}/"

    try:
        # Получаем страницу
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Город {city} не найден")
            return None

        # Парсим HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Извлекаем данные
        temp = soup.find("div", {"id": "weather-now-number"})
        desc = soup.find("div", {"id": "weather-now-description"})

        if temp and desc:
            return {"city": city, "temp": temp.text.strip(), "desc": desc.text.strip()}
        else:
            print("Данные не найдены")
            return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def analyze_weather(weather):
    """Проанализировать погоду"""
    if not weather:
        return

    print(f"\nПогода в {weather['city']}:")
    print(f"Температура: {weather['temp']}")
    print(f"Погода: {weather['desc']}")

    # Простая рекомендация
    temp_num = "".join(filter(str.isdigit, weather["temp"]))
    if temp_num:
        temp_num = int(temp_num)
        if temp_num > 25:
            print("Рекомендация: Жарко, идеально для пляжа! 🏖️")
        elif temp_num > 15:
            print("Рекомендация: Тепло, хорошо для прогулок! 🚶")
        elif temp_num > 5:
            print("Рекомендация: Прохладно, нужна куртка! 🧥")
        else:
            print("Рекомендация: Холодно, одевайтесь тепло! ⛄")


def main():
    """Основная функция"""
    print("ПРОСТОЙ ПЛАНИРОВЩИК ПОГОДЫ 🌤️")
    print("-" * 30)

    # Примеры городов
    cities = ["москва", "сочи", "казань", "самара"]

    for city in cities:
        weather = get_weather(city)
        analyze_weather(weather)
        print("-" * 30)


if __name__ == "__main__":
    main()
