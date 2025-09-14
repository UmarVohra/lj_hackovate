import os

class Config:
    SECRET_KEY = "hackathon_secret"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/hackathon_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "5f6a86bf6c8648c12e487f45461467f5")
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    UV_API_KEY = "openuv-41rabrmfj643af-io"