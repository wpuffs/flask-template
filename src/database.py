import string
import random

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    wallets = db.relationship("Wallet", backref="user")

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    
    def __repr__(self) -> str:
        return 'User: {self.username}'

class Wallet(db.Model):
    __tablename__ = "wallet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    currencies = db.relationship("Currency", backref="wallet")

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'Wallet'

class Currency(db.Model):
    __tablename__ = "currency"
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'Currency'

class Exchange(db.Model):
    __tablename__ = "exchange"
    id = db.Column(db.Integer, primary_key=True)
    base = db.Column(db.String(3), unique=True, nullable=False)
    exchange = db.Column(db.String(3), unique=True, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'Exchange Rate: {self.base}'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable = False)
    transaction_fromcurr = db.Column(db.String(3), nullable=False)
    transaction_fromamt = db.Column(db.Integer, nullable=False)
    transaction_toamt = db.Column(db.Integer, nullable=False)
    transaction_tocurr = db.Column(db.String(3), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'Transaction: {self.id}'