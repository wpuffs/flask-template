from flask import Flask, jsonify
import os
from src.auth import auth
from src.database import db
from src.wallet import wallet
from src.exchange import exchange
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
        )

    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(wallet)
    app.register_blueprint(exchange)

    @app.post("/insert_transaction")
    def insert_transaction():
        user_id = request.json['user_id']
        from_currency = request.json['from_currency']
        to_currency = request.json['to_currency']
        from_amount = request.json['from_amount']
        to_amount = request.json['to_amount']
        transaction = Transaction(user_id=user_id, from_currency=from_currency, to_currency=to_currency, from_amount = from_amount, to_amount = to_amount)
        
        db.session.add(transaction)
        db.session.commit()

        return {
            "transaction" : { "id": transaction.id,  "user_id": user_id, "from_currency": from_currency, "to_currency":to_currency, "from_amount":from_amount, "to_amount":to_amount }
        }, 200

    @app.errorhandler(404)
    def handle_404(e):
        return { "error": "Page not found" }, 404

    return app

