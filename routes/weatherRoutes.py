from flask import Blueprint, jsonify, request, current_app
import requests
from datetime import datetime
import torch
import torch.nn as nn
import pickle
import numpy as np
import pandas as pd
import os

weather = Blueprint("weather", __name__)
# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTILS_DIR = os.path.join(BASE_DIR, "utilities")

# ---------------- ML MODELS ----------------
class LSTMClass(nn.Module):
    def __init__(self, input_size=6, hidden=50, num_classes=3):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, num_classes)

    def forward(self, x):
        _, (hn, _) = self.lstm(x)
        return self.fc(hn[-1])


class LSTMReg(nn.Module):
    def __init__(self, input_size=6, hidden=50):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x):
        _, (hn, _) = self.lstm(x)
        return self.fc(hn[-1])


# Load once (global)
model_c = LSTMClass()
model_c.load_state_dict(torch.load(os.path.join(UTILS_DIR, "lstm_class_multi.pth")))
model_c.eval()

model_r = LSTMReg()
model_r.load_state_dict(torch.load(os.path.join(UTILS_DIR, "lstm_reg_multi.pth")))
model_r.eval()

scaler = pickle.load(open(os.path.join(UTILS_DIR, "scaler.pkl"), 'rb'))



# ---------------- WEATHER API ----------------
@weather.route("/api/weather", methods=["GET", "POST"])
def get_weather():
    # ---- City input handling ----
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        city = data.get("city", "Ahmedabad")
    else:  # GET request
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
        for d, v in list(daily_forecast.items())[:7]
    ]

    # ---------------- ML Prediction ----------------
    df = pd.read_csv(os.path.join(UTILS_DIR, "multi_city_labeled_fixed.csv"))
    sample_data = df[df['city'] == city][[
    'temperature_2m', 'relative_humidity_2m',
    'pressure_msl', 'wind_speed_10m', 'precipitation'
    ]]  # Agar empty hai -> fallback Ahmedabad

    if sample_data.empty:
        sample_data = df[df['city'] == "Ahmedabad"][[
            'temperature_2m', 'relative_humidity_2m',
            'pressure_msl', 'wind_speed_10m', 'precipitation'
        ]]

    sample_data = sample_data.tail(120).values

    event_code = np.zeros((120, 1))
    X = np.hstack((event_code, scaler.transform(sample_data)))
    X_t = torch.tensor(X, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        probs = torch.softmax(model_c(X_t), dim=1).numpy()[0]
        wind_pred = model_r(X_t).numpy().flatten()[0]

    event = ['normal', 'wind', 'thunderstorm'][np.argmax(probs)]
    reason = "High precip + humidity" if event == 'thunderstorm' else \
             "High wind speed" if event == 'wind' else \
             "Stable conditions"

    # --- AQI ---
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={current_data['coord']['lat']}&lon={current_data['coord']['lon']}&appid={api_key}"
    aqi_data = requests.get(aqi_url).json()
    aqi_value = aqi_data.get("list", [{}])[0].get("main", {}).get("aqi", "N/A")
    def get_uv_index(lat, lon, uv_token):
        url = "https://api.openuv.io/api/v1/uv"
        headers = {"x-access-token": uv_token}
        params = {"lat": lat, "lng": lon}
        res = requests.get(url, headers=headers, params=params).json()
        return res.get("result", {}).get("uv", "N/A")
    uv_token = current_app.config.get("UV_API_KEY")
    uv_value = get_uv_index(
    current_data["coord"]["lat"],
    current_data["coord"]["lon"],
    uv_token
)
    # ---------------- Final Response ----------------
    response = {
        "city": current_data["name"],
        "coordinates": {
            "lat": current_data["coord"]["lat"],
            "lon": current_data["coord"]["lon"]
        },
        "cities": ["Ahmedabad", "Delhi", "Mumbai", "Bangalore"],
        "current": {
            "temperature": current_data["main"]["temp"],
            "humidity": current_data["main"]["humidity"],
            "wind_speed": current_data["wind"]["speed"],
            "weather": current_data["weather"][0]["description"],
            "aqi": aqi_value,
            "uv_index":uv_value,
            "sunrise": datetime.fromtimestamp(current_data["sys"]["sunrise"]).strftime("%H:%M:%S"),
            "sunset": datetime.fromtimestamp(current_data["sys"]["sunset"]).strftime("%H:%M:%S"),
        },
        "forecast": forecast_list,
        "ml_prediction": {
            "event": event,
            "confidence": float(max(probs)),
            "predicted_wind_speed": float(wind_pred),
            "reason": reason,
            "alert_class": (
                "success" if event == "normal"
                else "warning" if event == "wind"
                else "danger"
            )
        }
    }

    return jsonify(response)
