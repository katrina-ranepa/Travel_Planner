import requests  # Для HTTP-запросов к сайту
from bs4 import BeautifulSoup  # Для парсинга HTML
import pandas as pd  # Для работы с табличными данными
from datetime import datetime, timedelta  # Для работы с датами
import time  # Для пауз между запросами
import sys  # Для управления системными функциями
import os  # Для работы с файловой системой


class DailyWeatherParser:
    def __init__(self):
        """Инициализация парсера погодных данных"""
        self.base_url = "https://pogoda-service.ru/archive_gsod_res.php"
        self.daily_data = []  # Храним данные по дням # Список для хранения данных
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }  # Заголовки, чтобы сайт думал, что это браузер(от блокировок/ботов)

    def parse_float_value(self, value_str): # Преобразует строку в число, обрабатывает запятые и пустые значения
        """Парсит строку в число, возвращает None если не удается"""
        try:
            if value_str and value_str.strip():
                # Убираем пробелы и заменяем запятые на точки
                clean_str = value_str.strip().replace(",", ".")
                return float(clean_str)
        except:
            pass  # "Ничего не делать, просто продолжаем" для обработки ошибок
        return None

    def parse_city_daily_data(
        self, city_name, station_code, start_date="01.01.2022", end_date="01.01.2025"
    ):
        """Парсит данные для конкретного города по дням"""
        print(f"📅 Собираю ежедневные данные для {city_name}...")

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
            )  # Передача фильтров, параметров поиска Параметры, которые добавляются к URL после знака ?.
            response.raise_for_status() #проверка статуса успещности 

            # Парсим HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Ищем таблицу с данными
            table = soup.find("table")
            if not table:
                print(f"⚠️ Не найдена таблица с данными для {city_name}")
                return

            # Получаем все строки таблицы (пропускаем заголовок)
            rows = table.find_all("tr")[1:]  # Пропускаем заголовок

            days_processed = 0#счетчик кол-ва успешно обработанных дней

            for (
                row
            ) in (
                rows
            ):  # rows — список строк таблицы (теги <tr>),  полученный через table.find_all("tr")[1:]
                cols = row.find_all("td")
                if len(cols) >= 1:  # Проверяем, что есть хотя бы дата
                    try:
                        # Извлекаем дату (первая колонка)
                        date_str = cols[0].text.strip()
                        date_obj = datetime.strptime(
                            date_str, "%d.%m.%Y"
                        )  # "%d.%m.%Y" — формат для распознавания день месяц год

                        # Извлекаем данные из всех доступных колонок
                        max_temp = (
                            self.parse_float_value(cols[1].text.strip())
                            if len(cols) > 1
                            else None
                        )
                        min_temp = (
                            self.parse_float_value(cols[2].text.strip())
                            if len(cols) > 2
                            else None
                        )
                        avg_temp = (
                            self.parse_float_value(cols[3].text.strip())
                            if len(cols) > 3
                            else None
                        )
                        pressure = (
                            self.parse_float_value(cols[4].text.strip())
                            if len(cols) > 4
                            else None
                        )
                        wind_speed = (
                            self.parse_float_value(cols[5].text.strip())
                            if len(cols) > 5
                            else None
                        )
                        precipitation = (
                            self.parse_float_value(cols[6].text.strip())
                            if len(cols) > 6
                            else None
                        )

                        # Добавляем данные в список по дням
                        self.daily_data.append(
                            {
                                "Город": city_name,
                                "Дата": date_obj.strftime("%Y-%m-%d"),
                                "Год": date_obj.year,
                                "Месяц": date_obj.month,
                                "День": date_obj.day,
                                "Макс_температура": max_temp,
                                "Мин_температура": min_temp,
                                "Сред_температура": avg_temp,
                                "Давление_гПа": pressure,
                                "Скорость_ветра_мс": wind_speed,
                                "Осадки_мм": precipitation,
                            }
                        )
                        days_processed += 1

                    except (ValueError, IndexError, AttributeError) as e:
                        # Если ошибка в дате или других данных, пропускаем строку
                        continue

            print(f"✅ {city_name}: собрано {days_processed} дней")

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении данных для {city_name}: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка при обработке {city_name}: {e}")

    def check_missing_dates(self):
        """Проверяет, есть ли пропущенные даты в данных"""
        if not self.daily_data:
            return

        # Группируем данные по городам
        cities_data = {}
        for record in self.daily_data:
            city = record["Город"]
            if city not in cities_data:
                cities_data[city] = []
            cities_data[city].append(record["Дата"])

        print("\n🔍 Проверка пропущенных дат:")
        for city, dates in cities_data.items():
            dates = sorted(dates)
            if dates:
                first_date = datetime.strptime(dates[0], "%Y-%m-%d")
                last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
                expected_days = (last_date - first_date).days + 1
                actual_days = len(set(dates))  # Уникальные даты

                if expected_days > actual_days:
                    missing = expected_days - actual_days
                    print(
                        f"  {city}: пропущено {missing} дней ({actual_days}/{expected_days})"
                    )
                else:
                    print(f"  {city}: все дни присутствуют ({actual_days} дней)")

    def save_daily_to_csv(self, filename="weather_daily_all_cities.csv"):
        """Сохраняет ежедневные данные в CSV файл"""
        if not self.daily_data:
            print("❌ Нет данных для сохранения")
            return False

        try:
            # Создаем DataFrame
            df = pd.DataFrame(self.daily_data)
            # Сортируем по городу, дате
            df = df.sort_values(["Город", "Дата"])
            # Заменяем NaN на "None" для читаемости
            df = df.fillna("None")
            # Сохраняем в CSV
            df.to_csv(
                filename, index=False
            )  # сохраняет только ваши данные, без этой колонки(убирает первую колонку)

            # Проверяем, что файл создан
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"\n✅ Файл успешно создан: {filename}")
                print(f"📊 Размер файла: {file_size:,} байт")
                print(f"📈 Всего записей: {len(df):,}")

                # Статистика по городам
                print("\n📊 Статистика по городам:")
                for city in df["Город"].unique():
                    city_data = df[df["Город"] == city]
                    dates = city_data["Дата"]

                    # Подсчитываем количество None в температуре
                    none_count = (city_data["Сред_температура"] == "None").sum()
                    total_count = len(city_data)

                    print(f"  {city}: {total_count} дней, пропусков: {none_count}")
                    print(f"     Период: {dates.min()} - {dates.max()}")

                # Пример данных
                print("\n📋 Пример данных (первые 3 строки):")
                print("=" * 100)
                print(df.head(3).to_string(index=False))
                print("=" * 100)

                # Информация о структуре файла
                print("\n📁 Структура файла:")
                print("Колонки:", ", ".join(df.columns.tolist()))
                print("\n📝 Примечание: 'None' означает отсутствие данных за этот день")

                return True
            else:
                print("❌ Ошибка: файл не был создан")
                return False

        except Exception as e:
            print(f"❌ Ошибка при создании файла: {e}")
            return False

    def create_summary_report(self):
        """Создает краткий отчет о данных"""
        if not self.daily_data:
            return

        df = pd.DataFrame(self.daily_data)

        print("\n" + "=" * 60)
        print("📊 СВОДКА ДАННЫХ")
        print("=" * 60)

        total_days = len(df)
        cities = df["Город"].nunique()
        date_range = f"{df['Дата'].min()} - {df['Дата'].max()}"

        print(f"Всего дней: {total_days:,}")
        print(f"Городов: {cities}")
        print(f"Период: {date_range}")

        # Статистика по пропускам
        print("\n📈 Качество данных:")
        for city in df["Город"].unique():
            city_df = df[df["Город"] == city]
            missing_temp = city_df["Сред_температура"].isna().sum()
            total_city = len(city_df)
            completeness = (
                100 * (total_city - missing_temp) / total_city if total_city > 0 else 0
            )

            print(f"  {city}: {completeness:.1f}% полных данных по температуре")


def create_sample_daily_file():
    """Создает пример файла с ежедневными данными"""
    print("\n📝 Создаю пример файла с данными...")

    sample_data = []
    cities = ["Санкт-Петербург", "Сочи", "Владивосток", "Калининград", "Махачкала"]

    for city in cities:
        # Разные температурные профили для городов
        base_temp = {
            "Санкт-Петербург": 5,
            "Сочи": 15,
            "Владивосток": 8,
            "Калининград": 7,
            "Махачкала": 12,
        }[city]

        # Создаем данные за 10 дней с некоторыми пропусками
        for day in range(1, 11):
            date = f"2024-06-{day:02d}"  #:02d — форматирует число как 2-значное с ведущим нулем

            # Создаем реалистичные данные, иногда с пропусками для проверки парсера
            if day == 3 or day == 7:  # Пропускаем данные для 3-го и 7-го дня
                sample_data.append(
                    {
                        "Город": city,
                        "Дата": date,
                        "Год": 2024,
                        "Месяц": 6,
                        "День": day,
                        "Макс_температура": None,
                        "Мин_температура": None,
                        "Сред_температура": None,
                        "Давление_гПа": None,
                        "Скорость_ветра_мс": None,
                        "Осадки_мм": None,
                    }
                )
            else:
                # Нормальные данные
                temp_variation = (day % 5) - 2
                max_temp = base_temp + temp_variation + 3
                min_temp = base_temp + temp_variation - 3
                avg_temp = (max_temp + min_temp) / 2

                sample_data.append(
                    {
                        "Город": city,
                        "Дата": date,
                        "Год": 2024,
                        "Месяц": 6,
                        "День": day,
                        "Макс_температура": round(max_temp, 1),
                        "Мин_температура": round(min_temp, 1),
                        "Сред_температура": round(avg_temp, 1),
                        "Давление_гПа": round(1013 + (day % 7) - 3, 1),
                        "Скорость_ветра_мс": round(3 + (day % 4) * 0.5, 1),
                        "Осадки_мм": round(1.2 if day % 3 == 0 else 0, 1),
                    }
                )

    # Сохраняем в файл
    df = pd.DataFrame(sample_data)
    df = df.fillna("None")  # Заменяем NaN на "None"
    df.to_csv("weather_daily_example.csv", index=False, encoding="utf-8-sig")

    print(f"✅ Пример файла создан: weather_daily_example.csv")
    print(f"📊 Записей: {len(df)}")
    print(f"📁 Размер: {os.path.getsize('weather_daily_example.csv'):,} байт")

    # Показываем пример
    print("\n📋 Пример данных с пропусками (None):")
    print(df.head(10).to_string(index=False))

    return df


def main():
    """Основная функция - создает файл с ежедневными данными"""
    print("=" * 70)
    print("СОЗДАНИЕ ФАЙЛА С ЕЖЕДНЕВНЫМИ ПОГОДНЫМИ ДАННЫМИ")
    print("=" * 70)
    print("📅 Данные будут сохранены в файл: weather_daily_all_cities.csv")
    print("⚠️  Отсутствующие данные будут отмечены как 'None'")
    print("=" * 70)

    # Создаем парсер
    parser = DailyWeatherParser()

    # Города для сбора данных
    cities_to_parse = [
        ("Санкт-Петербург", "260630", "01.01.2022", "01.01.2025"),
        ("Сочи", "371710", "01.01.2022", "01.01.2025"),
        ("Владивосток", "319600", "01.01.2022", "01.01.2025"),
        ("Калининград", "267020", "01.01.2022", "01.01.2025"),
        ("Махачкала", "374720", "01.01.2022", "23.12.2025"),
    ]

    print(f"\n🔄 Собираю данные для {len(cities_to_parse)} городов...")
    print("⏱️  Это может занять несколько минут...\n")

    # Собираем данные для каждого города
    for city_name, station_code, start_date, end_date in cities_to_parse:
        parser.parse_city_daily_data(city_name, station_code, start_date, end_date)
        time.sleep(2)  # Пауза между запросами

    # Проверяем пропущенные даты
    parser.check_missing_dates()

    # Создаем файл
    print("\n" + "=" * 70)
    print("СОЗДАНИЕ ФАЙЛА")
    print("=" * 70)

    success = parser.save_daily_to_csv("weather_daily_all_cities.csv")

    if success:
        parser.create_summary_report()

        print("\n" + "=" * 70)
        print("✅ ФАЙЛ УСПЕШНО СОЗДАН!")
        print("=" * 70)
        print("📁 Файл: weather_daily_all_cities.csv")
        print("📍 Расположение: в той же папке, где находится программа")
        print("\n📊 Файл содержит:")
        print("  • Данные по дням для 4 городов")
        print("  • Период: 2022-2025 годы")
        print("  • Отсутствующие данные отмечены как 'None'")
        print("  • Все метеопараметры: температура, давление, ветер, осадки")
    else:
        print("\n" + "=" * 70)
        print("⚠️  СОЗДАНИЕ ПРИМЕРНОГО ФАЙЛА")
        print("=" * 70)
        print("Не удалось получить реальные данные с сайта.")
        print("Создаю примерный файл с данными для демонстрации...")

        create_sample_daily_file()

        print("\n" + "=" * 70)
        print("📁 Примерный файл создан: weather_daily_example.csv")
        print("=" * 70)

    print("\n🏁 Работа завершена!")
    print("=" * 70)


# Запускаем программу
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("\n🔄 Создаю примерный файл...")
        create_sample_daily_file()
        print("\n🏁 Работа завершена с созданием примерного файла")
