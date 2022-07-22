from flask import Blueprint, request, jsonify
import validators
from src.database import Transaction, Wallet, Currency, User, db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

transaction = Blueprint(name="transaction", import_name=__name__, url_prefix="/transaction")

@transaction.post("/insert")
@jwt_required()
def insert_transaction():
    current_user = get_jwt_identity()
    from_currency = request.json['from_currency']
    to_currency = request.json['to_currency']
    from_amount = request.json['from_amount']
    to_amount = request.json['to_amount']
    transaction = Transaction(user_id=user_id, from_currency=from_currency, to_currency=to_currency, from_amount = from_amount, to_amount = to_amount)
    
    db.session.add(transaction)
    db.session.commit()

    return {
            "transaction" : { 
            "id": transaction.id, 
            "user_id": user_id, 
            "from_currency": from_currency, 
            "to_currency":to_currency, 
            "from_amount":from_amount, 
            "to_amount":to_amount 
        }
    }, 200