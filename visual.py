import matplotlib.pyplot as plt
import numpy as np

def visualize_seasonality_simple(city):
    """
    Простая визуализация сезонности для одного города
    """
    plt.figure(figsize=(10, 6))
    
    # Месяцы
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
              'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    # Примерные данные (в реальном коде брать из вашего DataFrame)
    temperatures = [-8, -7, -2, 6, 14, 18, 21, 19, 14, 7, 1, -5]
    tourists = [20, 25, 35, 50, 70, 85, 90, 80, 65, 50, 30, 25]
    
    # Создаем график
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Температура (линия)
    color = 'tab:red'
    ax1.set_xlabel('Месяц')
    ax1.set_ylabel('Температура (°C)', color=color)
    line = ax1.plot(months, temperatures, color=color, 
                    marker='o', linewidth=2, label='Температура')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(-15, 30)
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Туристы (столбцы)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Туристы (%)', color=color)
    bars = ax2.bar(months, tourists, color=color, 
                   alpha=0.3, width=0.7, label='Туристы')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 100)
    
    plt.title(f'📊 Сезонность туризма: {city}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def visualize_cities_comparison_simple():
    """
    Сравнение температур в разных городах
    """
    cities = ['Санкт-Петербург', 'Сочи', 'Владивосток']
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
              'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    # Примерные температуры
    data = {
        'Санкт-Петербург': [-6, -5, -1, 5, 12, 17, 19, 17, 12, 6, 1, -3],
        'Сочи': [6, 7, 10, 14, 18, 23, 26, 25, 21, 16, 12, 8],
        'Владивосток': [-12, -9, -2, 6, 11, 15, 20, 21, 16, 9, 0, -9]
    }
    
    plt.figure(figsize=(12, 6))
    
    for city in cities:
        plt.plot(months, data[city], marker='o', linewidth=2, label=city)
    
    plt.title('🌡️ Сравнение температур в городах России', fontsize=14, fontweight='bold')
    plt.xlabel('Месяц')
    plt.ylabel('Температура (°C)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def visualize_vacation_types(city):
    """
    Визуализация типов отдыха по месяцам
    """
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
              'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    # Оценки для разных типов отдыха (0-100%)
    beach = [10, 10, 20, 40, 60, 90, 95, 90, 70, 40, 20, 10]
    cultural = [30, 30, 40, 60, 80, 85, 80, 75, 80, 70, 50, 40]
    ski = [80, 85, 60, 10, 0, 0, 0, 0, 0, 10, 40, 70]
    city_tour = [40, 40, 50, 70, 85, 90, 85, 80, 85, 75, 55, 45]
    
    plt.figure(figsize=(12, 6))
    
    x = range(len(months))
    width = 0.2
    
    plt.bar([i - width*1.5 for i in x], beach, width, label='🏖️ Пляжный', color='gold')
    plt.bar([i - width*0.5 for i in x], cultural, width, label='🏛️ Культурный', color='lightblue')
    plt.bar([i + width*0.5 for i in x], ski, width, label='⛷️ Горнолыжный', color='lightgreen')
    plt.bar([i + width*1.5 for i in x], city_tour, width, label='🏙️ Городской', color='lightcoral')
    
    plt.title(f'🎯 Типы отдыха в {city} по месяцам', fontsize=14, fontweight='bold')
    plt.xlabel('Месяц')
    plt.ylabel('Рекомендация (%)')
    plt.xticks(x, months)
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def visualize_weather_radar():
    """
    Простая радар-диаграмма для сравнения городов
    """
    cities = ['Сочи', 'СПб', 'Владивосток']
    
    # Категории для сравнения
    categories = ['Температура', 'Солнце', 'Осадки', 'Ветер', 'Комфорт']
    
    # Данные для каждого города (нормализованные 0-10)
    data = np.array([
        [9, 8, 6, 5, 8],  # Сочи
        [5, 4, 7, 6, 6],  # СПб
        [6, 7, 5, 7, 6]   # Владивосток
    ])
    
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # Замкнуть круг
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Для каждого города
    colors = ['gold', 'lightblue', 'lightgreen']
    for i, city in enumerate(cities):
        values = data[i].tolist()
        values += values[:1]  # Замкнуть круг
        ax.plot(angles, values, 'o-', linewidth=2, label=city, color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 10)
    ax.set_title('📊 Сравнение погодных условий', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.show()

def main_visualization_menu():
    """
    Главное меню визуализаций
    """
    print("\n" + "="*50)
    print("📊 МЕНЮ ВИЗУАЛИЗАЦИИ РЕЗУЛЬТАТОВ")
    print("="*50)
    
    while True:
        print("\nВыберите тип визуализации:")
        print("1. 📈 Сезонность одного города")
        print("2. 🏙️ Сравнение городов")
        print("3. 🎯 Типы отдыха по месяцам")
        print("4. 📡 Радар-диаграмма погоды")
        print("5. ↩️ Назад")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == "1":
            city = input("Введите город (например, Сочи): ").strip()
            visualize_seasonality_simple(city)
            
        elif choice == "2":
            visualize_cities_comparison_simple()
            
        elif choice == "3":
            city = input("Введите город (например, Сочи): ").strip()
            visualize_vacation_types(city)
            
        elif choice == "4":
            visualize_weather_radar()
            
        elif choice == "5":
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте еще раз.")

# Самый простой вариант - одна функция для быстрой визуализации:
def quick_visualization(city, temperatures, tourists=None):
    """
    Быстрая визуализация за 3 строки кода
    """
    months = ['Я', 'Ф', 'М', 'А', 'М', 'И', 'И', 'А', 'С', 'О', 'Н', 'Д']
    
    plt.figure(figsize=(8, 4))
    plt.plot(months, temperatures, 'r-o', linewidth=2)
    plt.title(f'Температура в {city}')
    plt.xlabel('Месяц')
    plt.ylabel('°C')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='gray', linestyle='--')
    plt.show()

# Пример использования:
if __name__ == "__main__":
    # Тестируем разные визуализации
    
    # 1. Простая сезонность
    print("Тест 1: Сезонность Сочи")
    visualize_seasonality_simple("Сочи")
    
    # 2. Сравнение городов
    print("\nТест 2: Сравнение городов")
    visualize_cities_comparison_simple()
    
    # 3. Быстрая визуализация
    print("\nТест 3: Быстрая визуализация")
    temps = [6, 7, 10, 14, 18, 23, 26, 25, 21, 16, 12, 8]
    quick_visualization("Сочи", temps)
    
    # 4. Меню визуализаций
    # main_visualization_menu()
