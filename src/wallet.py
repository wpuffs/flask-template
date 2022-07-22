from flask import Blueprint, request, jsonify
import validators
from src.database import Wallet, Currency, User, db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

wallet = Blueprint(name="wallet", import_name=__name__, url_prefix="/wallet")

@wallet.post('/create')
@jwt_required()
def create_wallet():
    current_user = get_jwt_identity()
    wallet_name = request.json['name']

    if Wallet.query.filter_by(user_id=current_user, name=wallet_name).first():
            return jsonify({
                'error': 'Wallet with same name already exists'
            }), 400
    
    wallet = Wallet(name=wallet_name, user_id=current_user)
    db.session.add(wallet)
    db.session.commit()

    return { 
        "wallet": {
            "id": wallet.id,
            "name": wallet.name,
        }
    }, 200


@wallet.get('/all')
@jwt_required()
def get_all_wallets(): 
    current_user = get_jwt_identity()

    wallets = Wallet.query.filter_by(user_id=current_user).all()

    data = []

    for wallet in wallets:
        data.append({
            'id': wallet.id,
            'name': wallet.name
        })

    return {
        "wallets": data
    }, 200


@wallet.get('/<int:wallet_id>')
@jwt_required()
def get_wallet(wallet_id):
    current_user = get_jwt_identity()

    wallet = Wallet.query.filter_by(user_id=current_user, id=wallet_id).first()

    if not wallet:
        return { "error": "Wallet not found" }, 400

    return { 
        "wallet": {
            "id": wallet.id,
            "name": wallet.name,
        }
    }, 200


@wallet.delete('/<int:wallet_id>')
@jwt_required()
def delete_wallet(wallet_id): 
    Wallet.query.filter_by(id=wallet_id).delete()
    db.session.commit()
    return jsonify({"message": "Wallet deleted"}), 200


@wallet.post('/currency/<int:wallet_id>')
@jwt_required()
def add_wallet_currency(wallet_id):
    current_user = get_jwt_identity()

    currency = request.json['currency']
    amount = request.json['amount']

    if not Wallet.query.filter_by(user_id=current_user, id=wallet_id).first():
                return jsonify({
                    'error': 'Wallet does not exists'
                }), 400
    
    if Currency.query.filter_by(wallet_id=wallet_id, currency=currency).first():
                return jsonify({
                    'error': 'Wallet with same currency already exists'
                }), 400
        
    currency = Currency(wallet_id=wallet_id, currency=currency, amount=amount)
    db.session.add(currency)
    db.session.commit()

    return {
        "currency": {
            "id": currency.id,
            "wallet_id": currency.wallet_id,
            "currency": currency.currency,
            "amount": currency.amount
        }
    }, 200
    

@wallet.get('/currency/<int:wallet_id>')
@jwt_required()
def get_wallet_currencies(wallet_id):
    current_user = get_jwt_identity()

    if not Wallet.query.filter_by(user_id=current_user, id=wallet_id).first():
                return jsonify({
                    'error': 'Wallet does not exists'
                }), 400

    currencies = Currency.query.filter_by(wallet_id=wallet_id).all()

    data = []

    for currency in currencies:
        data.append({
            'id': currency.id,
            'wallet_id': currency.wallet_id,
            'currency': currency.currency,
            'amount': currency.amount
        })

    return {
        "currencies": data
    }, 200


@wallet.delete('/currency/<int:currency_id>')
@jwt_required()
def delete_wallet_currency(currency_id):
    Currency.query.filter_by(id=currency_id).delete()
    db.session.commit()
    return jsonify({"message": "Currency deleted"}), 200
    
