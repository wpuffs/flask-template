from flask import Flask, jsonify, request
import os
import json
from src.auth import auth
from src.database import db
from src.wallet import wallet
from src.exchange import exchange
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flask_cors import CORS, cross_origin

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
            CORS_HEADERS = 'Content-Type'
        )

    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)
    cors = CORS(app)

    app.register_blueprint(auth)
    app.register_blueprint(wallet)
    app.register_blueprint(exchange)



    @app.errorhandler(404)
    def handle_404(e):
        return { "error": "Page not found in multicurrency app" }, 404

    return app

