from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

auth = Blueprint(name="auth", import_name=__name__, url_prefix="/api/auth")

@auth.post('/register')
def register():
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    if len(password) < 6:
        return {'error': "Password is too short"}, 400

    if len(username) < 3:
        return {'error': "User is too short"}, 400

    if not username.isalnum() or " " in username:
        return {'error': "Username should be alphanumeric, also no spaces"}, 400

    if not validators.email(email):
        return {'error': "Email is not valid"}, 400

    if User.query.filter_by(email=email).first() is not None:
        return {'error': "Email is taken"}, 409

    if User.query.filter_by(username=username).first() is not None:
        return {'error': "username is taken"}, 409

    pwd_hash = generate_password_hash(password)
    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return {
        "message": "User created",
        "user" : { "username": username, "email": email}
    }, 201


@auth.post('/login')
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return {
                "user" : {
                    "refresh": refresh,
                    "access": access,
                    "username": user.username,
                    "email": user.email
                }
            }, 200
    
    return { "error": "Wrong credentials" }, 401


@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id = user_id).first()

    return { 
        "username": user.username,
        "email": user.email
    }


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return {
        "access": access
    }, 200
