import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import sys


class WeatherArchiveParser:
    def __init__(self):
        """Инициализация парсера погодных данных"""
        self.base_url = "https://pogoda-service.ru/archive_gsod_res.php"
        self.data = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def parse_city_data(
        self, city_name, station_code, start_date="01.01.2022", end_date="01.01.2025"
    ):
        """Парсит данные для конкретного города"""
        print(f"⏳ Обрабатываю данные для {city_name}...")

        # Параметры запроса
        params = {
            "station": station_code,
            "datepicker_beg": start_date,
            "datepicker_end": end_date,
        }

        try:
            # Отправляем GET-запрос
            response = requests.get(
                self.base_url, params=params, headers=self.headers, timeout=30
            )
            response.raise_for_status()

            # Проверяем кодировку
            if response.encoding.lower() not in ["utf-8", "utf8"]:
                response.encoding = "utf-8"

            # Парсим HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Ищем таблицу с данными
            table = soup.find("table")
            if not table:
                print(f"⚠️ Не найдена таблица с данными для {city_name}")
                return

            # Получаем все строки таблицы (пропускаем заголовок)
            rows = table.find_all("tr")[1:]  # Пропускаем заголовок

            monthly_data = {}

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 7:  # Проверяем, что есть все необходимые столбцы
                    try:
                        # Извлекаем дату
                        date_str = cols[0].text.strip()
                        date_obj = datetime.strptime(date_str, "%d.%m.%Y")

                        # Извлекаем среднюю температуру (столбец 3, индекс 2)
                        temp_str = cols[2].text.strip()
                        avg_temp = float(temp_str) if temp_str else 0.0

                        # Извлекаем осадки (столбец 6, индекс 5)
                        # Обработка возможного отсутствия данных
                        precip_str = cols[5].text.strip() if len(cols) > 5 else "0"
                        precipitation = (
                            float(precip_str)
                            if precip_str and precip_str.replace(".", "", 1).isdigit()
                            else 0.0
                        )

                        # Создаем ключ для месяца
                        month_key = (date_obj.year, date_obj.month)

                        # Добавляем данные в словарь месяца
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                "temps": [],
                                "precipitations": [],
                            }

                        monthly_data[month_key]["temps"].append(avg_temp)
                        monthly_data[month_key]["precipitations"].append(precipitation)

                    except (ValueError, IndexError) as e:
                        # Пропускаем строки с ошибками
                        continue

            # Рассчитываем средние значения для каждого месяца
            for (year, month), values in monthly_data.items():
                if values["temps"]:  # Проверяем, что есть данные
                    avg_month_temp = sum(values["temps"]) / len(values["temps"])
                    avg_month_precip = sum(values["precipitations"]) / len(
                        values["precipitations"]
                    )

                    # Добавляем в общий список
                    self.data.append(
                        {
                            "Город": city_name,
                            "Год": year,
                            "Месяц": month,
                            "Средняя_температура": round(avg_month_temp, 1),
                            "Осадки_мм": round(avg_month_precip, 1),
                        }
                    )

            print(f"✅ {city_name}: обработано {len(monthly_data)} месяцев")

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении данных для {city_name}: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка при обработке {city_name}: {e}")

    def save_to_csv(self, filename="weather_archive.csv"):
        """Сохраняет данные в CSV файл"""
        if not self.data:
            print("❌ Нет данных для сохранения")
            return

        try:
            # Создаем DataFrame
            df = pd.DataFrame(self.data)

            # Сортируем по городу, году и месяцу
            df = df.sort_values(["Город", "Год", "Месяц"])

            # Сохраняем в CSV
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"\n✅ Данные успешно сохранены в файл: {filename}")
            print(f"📊 Всего записей: {len(df)}")

            # Показываем статистику
            print("\n📈 Статистика по городам:")
            for city in df["Город"].unique():
                city_data = df[df["Город"] == city]
                print(
                    f"  {city}: {len(city_data)} записей ({city_data['Год'].min()}-{city_data['Год'].max()})"
                )

            # Показываем первые несколько строк
            print("\n📋 Первые 5 строк файла:")
            print(df.head().to_string(index=False))

        except Exception as e:
            print(f"❌ Ошибка при сохранении файла: {e}")


def main():
    """Основная функция для парсинга данных"""
    print("=" * 60)
    print("ПАРСЕР АРХИВА ПОГОДЫ ДЛЯ 5 ГОРОДОВ")
    print("=" * 60)

    # Создаем экземпляр парсера
    parser = WeatherArchiveParser()

    # Список городов для обработки
    cities = [
        # (Название города, код станции, начало периода, конец периода)
        ("Санкт-Петербург", "260630", "01.01.2022", "01.01.2025"),
        ("Сочи", "371710", "01.01.2022", "01.01.2025"),
        ("Владивосток", "319600", "01.01.2022", "01.01.2025"),
        ("Калининград", "267020", "01.01.2022", "01.01.2025"),
        # Примечание: Для Махачкалы код станции не указан в ссылке
        # Если найдете код, добавьте строку:
        # ("Махачкала", "КОД_СТАНЦИИ", "01.01.2022", "01.01.2025")
    ]

    print(f"🔄 Начинаю парсинг данных для {len(cities)} городов...\n")

    # Парсим данные для каждого города
    for city_name, station_code, start_date, end_date in cities:
        parser.parse_city_data(city_name, station_code, start_date, end_date)
        time.sleep(1)  # Пауза между запросами

    # Сохраняем данные
    parser.save_to_csv()

    print("\n" + "=" * 60)
    print("Парсинг завершен!")
    print("=" * 60)


def create_mock_data():
    """Создает тестовые данные, если парсинг не сработает"""
    print("\n🛠️ Создаю тестовые данные...")

    # Тестовые данные на основе типичных климатических характеристик
    mock_data = []

    # Данные для Санкт-Петербурга (примерные значения)
    for year in [2022, 2023, 2024]:
        monthly_temps = [
            -6.0,
            -5.0,
            -1.0,
            5.0,
            12.0,
            16.0,
            18.0,
            17.0,
            12.0,
            6.0,
            1.0,
            -3.0,
        ]
        monthly_precip = [45, 35, 35, 35, 40, 65, 80, 85, 65, 65, 55, 50]

        for month in range(1, 13):
            mock_data.append(
                {
                    "Город": "Санкт-Петербург",
                    "Год": year,
                    "Месяц": month,
                    "Средняя_температура": monthly_temps[month - 1],
                    "Осадки_мм": monthly_precip[month - 1],
                }
            )

    # Данные для Сочи (примерные значения)
    for year in [2022, 2023, 2024]:
        monthly_temps = [
            6.0,
            6.0,
            8.0,
            12.0,
            17.0,
            21.0,
            24.0,
            24.0,
            21.0,
            16.0,
            12.0,
            8.0,
        ]
        monthly_precip = [185, 135, 115, 115, 95, 100, 95, 115, 135, 150, 185, 200]

        for month in range(1, 13):
            mock_data.append(
                {
                    "Город": "Сочи",
                    "Год": year,
                    "Месяц": month,
                    "Средняя_температура": monthly_temps[month - 1],
                    "Осадки_мм": monthly_precip[month - 1],
                }
            )

    # Сохраняем тестовые данные
    df = pd.DataFrame(mock_data)
    df.to_csv("weather_archive_mock.csv", index=False, encoding="utf-8-sig")
    print("✅ Тестовые данные сохранены в weather_archive_mock.csv")
    print(f"📊 Всего записей: {len(df)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Парсинг прерван пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("\n🔄 Пробую создать тестовые данные...")
        create_mock_data()
