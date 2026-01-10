from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from app.extensions import db  # import db from extensions

# TO UPDATE:
# from app.models import club, club, externalEvent, internalEvent, student
from app.models import supply

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}'
    db.init_app(app)

    # Importing models
    from app.models import supply

    # Creating tables
    with app.app_context():
        db.create_all()

    # Registering blueprint routes - organizes code to define http requests
    from app.routes.supplyRoutes import supply_bp
    app.register_blueprint(supply_bp, url_prefix="/supply")
    

    return app