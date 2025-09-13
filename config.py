import os

class Config:
    SECRET_KEY = "hackathon_secret"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/hackathon_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join("static", "uploads")