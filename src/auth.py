from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

auth = Blueprint(name="auth", import_name=__name__, url_prefix="/auth")

@auth.post('/register')
def register():
    username = request.json['username']
    password = request.json['password']
    name = request.json['name']

    if len(username) > 20:
        return {'error': "Username is too long"}, 400

    if not username.isalnum() or " " in username:
        return {'error': "Username should be alphanumeric, also no spaces"}, 400

    if User.query.filter_by(username=username).first() is not None:
        return {'error': "Username is taken"}, 409

    pwd_hash = generate_password_hash(password)
    user = User(username=username, password=pwd_hash, name=name)
    db.session.add(user)
    db.session.commit()

    return {
        "user" : { "name": name, "username": username }
    }, 200


@auth.post('/login')
def login():
    username = request.json.get("username", "")
    password = request.json.get("password", "")

    user = User.query.filter_by(username=username).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return {
                "user" : {
                    "id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "access": access,
                    "refresh": refresh
                }
            }, 200
    
    return { "error": "Wrong credentials" }, 401


@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id = user_id).first()

    return { 
        "name": user.name,
        "username": user.username
    }


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return {
        "access": access
    }, 200
