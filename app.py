from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from routes.authRoutes import auth
from routes.crudRoutes import items
from routes.mainRoutes import main
from models import User, Item

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(items, url_prefix="/items")
app.register_blueprint(main)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
