
# Weather & ML Prediction API

This project is a Flask-based web application that provides weather data, air quality, UV index, and machine learning-based weather event predictions for multiple cities. It integrates with the OpenWeatherMap API and uses PyTorch models for advanced forecasting.

## Features
- Get current weather, 7-day forecast, AQI, and UV index for supported cities
- ML-based prediction of weather events (normal, wind, thunderstorm) and wind speed
- RESTful API endpoint for easy integration
- CORS enabled for cross-origin requests
- Easily extensible for more cities and features

## Project Structure

```
├── app.py                # Main Flask app entry point
├── config.py             # Configuration (API keys, DB URI, etc.)
├── routes/
│   └── weatherRoutes.py  # Weather API and ML endpoints
├── utilities/            # ML models, scaler, and data CSV
│   ├── lstm_class_multi.pth
│   ├── lstm_reg_multi.pth
│   ├── scaler.pkl
│   └── multi_city_labeled_fixed.csv
└── ...
```

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies:**
	 ```bash
	 pip install flask flask_cors torch pandas numpy requests pymysql
	 ```
3. **Set up environment variables (optional):**
	 - `WEATHER_API_KEY` (default provided in config.py)
	 - `UV_API_KEY` (default provided in config.py)
4. **Ensure MySQL is running** (if you plan to use the DB URI in `config.py`)
5. **Run the app:**
	 ```bash
	 python app.py
	 ```

## API Usage

### Get Weather & Prediction

**Endpoint:** `/api/weather`

- **GET** or **POST**
- **Params:** `city` (Ahmedabad, Delhi, Mumbai, Bangalore)

**Example:**
```bash
curl "http://localhost:5000/api/weather?city=Ahmedabad"
```

**Response:**
```json
{
	"city": "Ahmedabad",
	"coordinates": {"lat": ..., "lon": ...},
	"cities": ["Ahmedabad", "Delhi", ...],
	"current": {
		"temperature": 30.5,
		"humidity": 60,
		"wind_speed": 5.2,
		"weather": "clear sky",
		"aqi": 2,
		"uv_index": 5.1,
		"sunrise": "06:10:00",
		"sunset": "18:45:00"
	},
	"forecast": [
		{"date": "2024-09-14", "temperature": {"min": 27, "max": 34}, "weather": "scattered clouds"},
		...
	],
	"ml_prediction": {
		"event": "normal",
		"confidence": 0.98,
		"predicted_wind_speed": 7.5,
		"reason": "Stable conditions",
		"alert_class": "success"
	}
}
```


## ML Models

This project uses two custom PyTorch LSTM models for weather event prediction:

- **LSTMClass**: A classification model that predicts the probability of three weather events: `normal`, `wind`, and `thunderstorm`.
- **LSTMReg**: A regression model that predicts the next wind speed value.

### Model Architecture
- Both models use an LSTM layer with 6 input features and a hidden size of 50.
- The classifier outputs 3 classes, while the regressor outputs a single value.

### Input Features
- `temperature_2m`
- `relative_humidity_2m`
- `pressure_msl`
- `wind_speed_10m`
- `precipitation`
- `event_code` (for sequence context)

### Training Data
- Models are trained on the `multi_city_labeled_fixed.csv` dataset, which contains historical weather data for multiple Indian cities.
- The data is preprocessed and scaled using a fitted scaler (`scaler.pkl`).

### Model Files
- `utilities/lstm_class_multi.pth`: Weights for the classification model
- `utilities/lstm_reg_multi.pth`: Weights for the regression model
- `utilities/scaler.pkl`: Scaler for input normalization

### Usage in API
- On each API call, the latest 120 data points for the selected city are preprocessed and passed to the models.
- The classifier predicts the most likely weather event and its confidence.
- The regressor predicts the next wind speed value.

### Extending/Updating Models
- To retrain or update the models, use the same data format and update the `.pth` and `.pkl` files in the `utilities/` folder.

For more details, see the model loading and inference code in `routes/weatherRoutes.py`.

## Extending
- Add more cities/data to `multi_city_labeled_fixed.csv`
- Update or retrain ML models as needed
- Add new endpoints in `routes/`

## License
MIT License 