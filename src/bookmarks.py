from flask import Blueprint, request, jsonify
import validators

from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint(name="bookmarks", import_name=__name__, url_prefix="/api/bookmarks")

@bookmarks.get('/')
@bookmarks.post('/')
@jwt_required()
def handle_bookmark():
    current_user = get_jwt_identity()
    if request.method == "POST":
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return { "error": "Bookmark url is not a valid url" }, 400
        
        if Bookmark.query.filter_by(url=url).first():
            return { "error": "Bookmark url already exists" }, 400
        
        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return {
            "id": bookmark.id,
            "url": bookmark.url,
            "body": bookmark.body,
            "created_at": bookmark.created_at
        }, 201
    
    else: #GET method
        bookmarks = Bookmark.query.filter_by(user_id=current_user)
        data = []
        
        for item in bookmarks:
            data.append({
                "id": item.id,
                "url": item.url,
                "body": item.body,
                "created_at": item.created_at
            })
        
        return jsonify({ "data": data }), 200


@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return { "error": "Bookmark not found" }, 404
    else:
        return {
            "id": bookmark.id,
            "url": bookmark.url,
            "body": bookmark.body,
            "created_at": bookmark.created_at
        }, 200


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return { "error": "Item not found" }, 404
    
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return { "error": "Bookmark url is not a valid url" }, 400
    
    bookmark.url = url
    bookmark.body = body
    db.session.commit()

    return {
            "id": bookmark.id,
            "url": bookmark.url,
            "body": bookmark.body,
            "created_at": bookmark.created_at
        }, 201


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return { "error": "Bookmark not found" }, 404

    db.session.delete(bookmark)
    db.session.commit()

    return { "success": "Bookmark has been deleted" }, 200