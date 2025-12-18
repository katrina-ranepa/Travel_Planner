# trip_planner_simple.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import time

# City configuration
CITIES = {
    "Moscow": "https://pogoda-service.ru/archive_gsod_res.php?station=276120&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "St_Petersburg": "https://pogoda-service.ru/archive_gsod_res.php?station=260630&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "Sochi": "https://pogoda-service.ru/archive_gsod_res.php?station=371710&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "Vladivostok": "https://pogoda-service.ru/archive_gsod_res.php?station=319600&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "Murmansk": "https://pogoda-service.ru/archive_gsod_res.php?station=221130&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "Kaliningrad": "https://pogoda-service.ru/archive_gsod_res.php?station=267020&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
    "Yekaterinburg": "https://pogoda-service.ru/archive_gsod_res.php?station=284400&datepicker_beg=01.01.2020&datepicker_end=01.01.2025",
}

# Similar cities for data approximation
SIMILAR_CITIES = {
    "Kazan": "Yekaterinburg",
    "Makhachkala": "Sochi",
    "Irkutsk": "Yekaterinburg",
    "Petropavlovsk_Kamchatsky": "Vladivostok",
}


class SimpleWeatherParser:
    """Simple weather data parser and analyzer"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.city_data_cache = {}

    def get_city_data(self, city_name):
        """Get historical weather data for a city"""
        print(f"🌍 Loading data for {city_name}...")

        # Check cache first
        if city_name in self.city_data_cache:
            return self.city_data_cache[city_name]

        # For similar cities, use data from similar city
        if city_name in SIMILAR_CITIES:
            similar_city = SIMILAR_CITIES[city_name]
            if similar_city in self.city_data_cache:
                # Adjust temperatures for similar city
                data = self.city_data_cache[similar_city].copy()
                temp_adjustment = self._get_temperature_adjustment(
                    city_name, similar_city
                )

                # Adjust temperatures
                for i in range(len(data)):
                    data[i]["max"] += temp_adjustment
                    data[i]["min"] += temp_adjustment

                print(f"✅ {city_name}: {len(data)} records (from {similar_city})")
                self.city_data_cache[city_name] = data
                return data

        # Get data from URL
        try:
            url = CITIES[city_name]
            response = self.session.get(url, timeout=30)
            response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")

            if not table:
                print(f"⚠️ No data found for {city_name}")
                return None

            # Extract table rows
            data = []
            for row in table.find_all("tr")[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    date_str = cols[0].text.strip()
                    temp_max = cols[1].text.strip().replace(",", ".")
                    temp_min = cols[2].text.strip().replace(",", ".")

                    # Check if we have temperature data
                    if temp_max and temp_min:
                        try:
                            data.append(
                                {
                                    "date": date_str,
                                    "max": float(temp_max),
                                    "min": float(temp_min),
                                }
                            )
                        except ValueError:
                            continue

            if not data:
                print(f"⚠️ No valid data for {city_name}")
                return None

            print(f"✅ {city_name}: {len(data)} records loaded")
            self.city_data_cache[city_name] = data
            return data

        except Exception as e:
            print(f"❌ Error for {city_name}: {e}")
            return None

    def _get_temperature_adjustment(self, city, similar_city):
        """Get temperature adjustment for similar cities"""
        adjustments = {
            "Kazan": -2,  # Kazan is colder than Yekaterinburg
            "Makhachkala": 3,  # Makhachkala is warmer than Sochi
            "Irkutsk": -8,  # Irkutsk is colder than Yekaterinburg
            "Petropavlovsk_Kamchatsky": -5,  # Colder than Vladivostok
        }
        return adjustments.get(city, 0)

    def analyze_city(self, city_name, activity_type="city"):
        """Analyze city and provide recommendations"""

        # Get city data
        data = self.get_city_data(city_name)
        if not data:
            return None

        # Create DataFrame
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

        # Filter for last 5 years
        current_year = datetime.now().year
        df = df[df["year"] >= current_year - 5]

        if len(df) == 0:
            return None

        # Calculate average temperature
        df["avg"] = (df["max"] + df["min"]) / 2

        # Monthly statistics
        monthly_stats = {}
        for month in range(1, 13):
            month_data = df[df["month"] == month]
            if len(month_data) > 0:
                monthly_stats[month] = {
                    "avg": month_data["avg"].mean(),
                    "max": month_data["max"].max(),
                    "min": month_data["min"].min(),
                    "count": len(month_data),
                }

        # Create recommendations based on activity type
        recommendations = self._create_recommendations(
            city_name, monthly_stats, activity_type
        )
        return recommendations

    def _create_recommendations(self, city_name, monthly_stats, activity_type):
        """Create travel recommendations"""

        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        # Activity requirements
        activity_requirements = {
            "beach": {
                "ideal_temp": (20, 32),
                "months": [6, 7, 8],
                "desc": "🏖️ Beach vacation",
            },
            "sightseeing": {
                "ideal_temp": (10, 25),
                "months": [5, 6, 9],
                "desc": "🏛️ Sightseeing",
            },
            "ski": {
                "ideal_temp": (-10, -2),
                "months": [12, 1, 2],
                "desc": "⛷️ Ski vacation",
            },
            "city": {
                "ideal_temp": (5, 25),
                "months": [4, 5, 6, 9, 10],
                "desc": "🏙️ City tourism",
            },
        }

        requirements = activity_requirements.get(
            activity_type, activity_requirements["city"]
        )

        # Score each month
        month_scores = []
        for month, stats in monthly_stats.items():
            score = self._calculate_month_score(
                stats["avg"], requirements["ideal_temp"]
            )

            # Bonus for good months
            if month in requirements["months"]:
                score += 20

            month_scores.append((month, score, stats))

        # Sort by score
        month_scores.sort(key=lambda x: x[1], reverse=True)

        # Build result
        result = {
            "city": city_name,
            "activity": requirements["desc"],
            "best_months": [],
            "worst_months": [],
            "monthly_stats": monthly_stats,
            "general_stats": self._get_general_stats(monthly_stats),
        }

        # Add best months (top 3)
        for month, score, stats in month_scores[:3]:
            if score > 50:  # Only good months
                month_info = {
                    "name": month_names[month],
                    "temp": stats["avg"],
                    "score": score,
                }
                result["best_months"].append(month_info)

        # Add worst months (bottom 3)
        for month, score, stats in month_scores[-3:]:
            if score < 30:  # Only bad months
                month_info = {
                    "name": month_names[month],
                    "temp": stats["avg"],
                    "score": score,
                }
                result["worst_months"].append(month_info)

        return result

    def _calculate_month_score(self, temperature, ideal_range):
        """Calculate score for a month based on temperature"""
        ideal_min, ideal_max = ideal_range

        if ideal_min <= temperature <= ideal_max:
            # Perfect temperature
            return 80 + (ideal_max - temperature) * 2
        elif temperature < ideal_min:
            # Too cold
            return max(0, 80 - (ideal_min - temperature) * 5)
        else:
            # Too hot
            return max(0, 80 - (temperature - ideal_max) * 3)

    def _get_general_stats(self, monthly_stats):
        """Get general statistics"""
        if not monthly_stats:
            return {}

        temps = [stats["avg"] for stats in monthly_stats.values()]

        return {
            "avg_year_temp": np.mean(temps),
            "warmest_month": max(monthly_stats.items(), key=lambda x: x[1]["avg"])[0],
            "coldest_month": min(monthly_stats.items(), key=lambda x: x[1]["avg"])[0],
            "total_months": len(monthly_stats),
        }

    def print_recommendation(self, recommendation):
        """Print recommendation in nice format"""
        if not recommendation:
            print("No recommendation available")
            return

        print("\n" + "=" * 60)
        print(f"🏙️  TRAVEL RECOMMENDATION: {recommendation['city']}")
        print(f"🎯 Activity type: {recommendation['activity']}")
        print("=" * 60)

        # Best months
        if recommendation["best_months"]:
            print("\n✅ BEST TIME TO TRAVEL:")
            for month in recommendation["best_months"]:
                print(
                    f"   • {month['name']}: {month['temp']:.1f}°C (Score: {month['score']:.0f}/100)"
                )

        # Worst months
        if recommendation["worst_months"]:
            print("\n❌ WORST TIME TO TRAVEL:")
            for month in recommendation["worst_months"]:
                print(
                    f"   • {month['name']}: {month['temp']:.1f}°C (Score: {month['score']:.0f}/100)"
                )

        # General stats
        stats = recommendation["general_stats"]
        if stats:
            month_names = {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December",
            }

            print("\n📊 GENERAL STATISTICS:")
            print(f"   • Average year temperature: {stats['avg_year_temp']:.1f}°C")

            warm_month = month_names.get(
                stats["warmest_month"], f"Month {stats['warmest_month']}"
            )
            cold_month = month_names.get(
                stats["coldest_month"], f"Month {stats['coldest_month']}"
            )

            warm_temp = recommendation["monthly_stats"][stats["warmest_month"]]["avg"]
            cold_temp = recommendation["monthly_stats"][stats["coldest_month"]]["avg"]

            print(f"   • Warmest month: {warm_month} ({warm_temp:.1f}°C)")
            print(f"   • Coldest month: {cold_month} ({cold_temp:.1f}°C)")

        print("\n" + "=" * 60)

    def compare_cities(self, city1, city2, activity_type="city"):
        """Compare two cities"""
        print(f"\n🔍 COMPARING: {city1} vs {city2}")

        rec1 = self.analyze_city(city1, activity_type)
        rec2 = self.analyze_city(city2, activity_type)

        if not rec1 or not rec2:
            print("Cannot compare - missing data")
            return

        print("\n" + "=" * 60)
        print(f"🏙️  CITY COMPARISON: {activity_type} vacation")
        print("=" * 60)

        # Compare best months
        print(f"\n✅ BEST MONTHS COMPARISON:")
        print(f"{city1}: ", end="")
        if rec1["best_months"]:
            print(f"{', '.join([m['name'] for m in rec1['best_months'][:2]])}")
        else:
            print("No good months")

        print(f"{city2}: ", end="")
        if rec2["best_months"]:
            print(f"{', '.join([m['name'] for m in rec2['best_months'][:2]])}")
        else:
            print("No good months")

        # Compare temperatures
        temp1 = rec1["general_stats"].get("avg_year_temp", 0)
        temp2 = rec2["general_stats"].get("avg_year_temp", 0)

        print(f"\n🌡️  AVERAGE TEMPERATURE:")
        print(f"{city1}: {temp1:.1f}°C")
        print(f"{city2}: {temp2:.1f}°C")

        if temp1 > temp2:
            print(f"→ {city1} is {temp1 - temp2:.1f}°C warmer")
        else:
            print(f"→ {city2} is {temp2 - temp1:.1f}°C warmer")

        print("\n" + "=" * 60)


# Main function to run the parser
def main():
    print("🚀 TripPlanner - Weather Analysis for Russian Cities")
    print("=" * 60)

    # Create parser
    parser = SimpleWeatherParser()

    # Available cities
    all_cities = list(CITIES.keys()) + list(SIMILAR_CITIES.keys())
    print(f"📊 Available cities: {', '.join(all_cities)}")

    # Test with some cities
    test_cities = ["Moscow", "Sochi", "Murmansk", "Kazan"]

    print("\n🔍 Analyzing cities...")
    print("-" * 40)

    for city in test_cities:
        # Analyze for different activity types
        print(f"\n📍 Analyzing {city}...")

        # Beach vacation analysis
        if city in ["Sochi", "Vladivostok", "Makhachkala"]:
            recommendation = parser.analyze_city(city, "beach")
            if recommendation:
                parser.print_recommendation(recommendation)
        # City tourism for others
        else:
            recommendation = parser.analyze_city(city, "city")
            if recommendation:
                parser.print_recommendation(recommendation)

        time.sleep(1)  # Be nice to the server

    # Compare some cities
    print("\n" + "=" * 60)
    print("🔍 COMPARISON TOOLS")
    print("=" * 60)

    # Compare Moscow and Sochi for city tourism
    parser.compare_cities("Moscow", "Sochi", "city")

    # Compare for beach vacation
    print("\n" + "=" * 60)
    parser.compare_cities("Sochi", "Vladivostok", "beach")

    # Save data to CSV
    print("\n💾 Saving data to files...")
    for city in ["Moscow", "Sochi", "Murmansk"]:
        data = parser.get_city_data(city)
        if data:
            df = pd.DataFrame(data)
            filename = f"{city.lower()}_weather.csv"
            df.to_csv(filename, index=False, encoding="utf-8")
            print(f"  Saved {len(df)} records to {filename}")

    print("\n✅ Analysis complete!")
    print("🎯 Tips:")
    print("  • For beach vacations: Sochi, Makhachkala, Vladivostok")
    print("  • For city tourism: Moscow, St_Petersburg, Kazan")
    print(
        "  • For unique experiences: Murmansk (northern lights), Kaliningrad (European Russia)"
    )
    print("  • For winter sports: Yekaterinburg, Irkutsk")


if __name__ == "__main__":
   