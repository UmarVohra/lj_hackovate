from flask import Flask
from config import Config
from flask_cors import CORS
from routes.weatherRoutes import weather


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
app.register_blueprint(weather)


if __name__ == "__main__":
    app.run(debug=True)