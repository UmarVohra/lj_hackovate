from flask import Blueprint, jsonify, request, current_app
import requests
from datetime import datetime

weather = Blueprint("weather", __name__)

@weather.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "Ahmedabad")

    api_key = current_app.config["WEATHER_API_KEY"]
    base_url = current_app.config["WEATHER_BASE_URL"]

    # Current weather
    current_url = f"{base_url}/weather?q={city}&appid={api_key}&units=metric"
    current_data = requests.get(current_url).json()

    if current_data.get("cod") != 200:
        return jsonify({"error": current_data.get("message", "Error fetching weather")}), 400

    # Forecast (5-day / 3-hour)
    forecast_url = f"{base_url}/forecast?q={city}&appid={api_key}&units=metric"
    forecast_data = requests.get(forecast_url).json()

    # Group forecast by day
    daily_forecast = {}
    for entry in forecast_data.get("list", []):
        date = datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d")
        temp_min = entry["main"]["temp_min"]
        temp_max = entry["main"]["temp_max"]
        weather_desc = entry["weather"][0]["description"]

        if date not in daily_forecast:
            daily_forecast[date] = {
                "min": temp_min,
                "max": temp_max,
                "weather": weather_desc
            }
        else:
            daily_forecast[date]["min"] = min(daily_forecast[date]["min"], temp_min)
            daily_forecast[date]["max"] = max(daily_forecast[date]["max"], temp_max)

    forecast_list = [
        {
            "date": d,
            "temperature": {"min": v["min"], "max": v["max"]},
            "weather": v["weather"]
        }
        for d, v in list(daily_forecast.items())[:5]  # only next 5 days
    ]

    response = {
        "city": current_data["name"],
        "current": {
            "temperature": current_data["main"]["temp"],
            "humidity": current_data["main"]["humidity"],
            "wind_speed": current_data["wind"]["speed"],
            "weather": current_data["weather"][0]["description"],
            "aqi": "N/A",  # will add later from IQAir
            "sunrise": datetime.fromtimestamp(current_data["sys"]["sunrise"]).strftime("%H:%M:%S"),
            "sunset": datetime.fromtimestamp(current_data["sys"]["sunset"]).strftime("%H:%M:%S"),
        },
        "forecast": forecast_list
    }

    return jsonify(response)