from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from app.extensions import db  # import db from extensions

from app.models import supply, request, drone, droneDistance, room

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}'
    db.init_app(app)

    # Importing models
    from app.models import supply, request, drone, droneDistance, room

    # Creating tables
    with app.app_context():
        db.create_all()

    # Registering blueprint routes - organizes code to define http requests
    from app.routes.supplyRoutes import supply_bp
    app.register_blueprint(supply_bp, url_prefix="/supply")
    from app.routes.droneRoutes import drone_bp
    app.register_blueprint(drone_bp, url_prefix="/drone")
    from app.routes.requestRoutes import request_bp
    app.register_blueprint(request_bp, url_prefix="/request")
    from app.routes.roomRoutes import room_bp
    app.register_blueprint(room_bp, url_prefix="/room")

    return app