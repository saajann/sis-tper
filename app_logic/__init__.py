from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app_logic.routes import main
    app.register_blueprint(main)

    from app_logic.admin_routes import admin
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app
