import boto3
import botocore
import os
import random

from botocore.exceptions import ClientError
from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import secure_filename
from src.database import Image, db
from string import ascii_letters, digits

images = Blueprint(name="images", import_name=__name__, url_prefix="/api/images")

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3", region_name="ap-southeast-1", aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"))
bucket_name = "flask-template"

@images.post('/upload')
@jwt_required()
def upload_image():
    current_user = get_jwt_identity()

    try:
        temp_file = request.files["image"]
    except BadRequestKeyError as e:
        return { "error": "Image file is missing" }, 400

    mimetype = temp_file.content_type
    temp_file_name = secure_filename(temp_file.filename)
    temp_file_ext = temp_file_name.split(".")[-1]

    object_name = str(current_user) + "_" + get_random_name() + "." + temp_file_ext

    try:
        response = s3_client.upload_fileobj(temp_file, bucket_name, object_name)
    except Exception as e:
        return { "error": "Error uploading image to s3 server" }, 500

    image = Image(name=object_name, user_id=current_user)
    db.session.add(image)
    db.session.commit()

    return { "success": "Image uploaded" }, 200


@images.get('/all')
@jwt_required()
def get_user_images():
    current_user = get_jwt_identity()
    
    images = Image.query.filter_by(user_id=current_user)
    data = []

    for item in images:
            data.append({
                "id": item.id,
                "name": item.name,
                "created_at": item.created_at
            })
        
    return jsonify({ "data": data }), 200


@images.get('/download/<int:id>')
@jwt_required()
def download_image(id):
    current_user = get_jwt_identity()

    image = Image.query.filter_by(user=current_user, id=id).first()
    file_ext = image.name.split(".")[-1]

    with open(str(current_user) + "_buffer." + file_ext, "wb") as f:
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=image.name)
            print(response)
            s3_client.download_fileobj(bucket_name, image.name, f)

        except botocore.excepts.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return { "error": "Image file does not exist on the server" }
        
    return send_file("../" + str(current_user) + "_buffer." + file_ext, as_attachment=True)


@images.delete('/delete/<int:id>')
@jwt_required()
def delete_image(id):
    current_user = get_jwt_identity()

    image = Image.query.filter_by(user_id=current_user, id=id).first()

    if not image:
        return { "error": "Image file not found in database" }, 404

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=image.name)
    except botocore.excepts.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return { "error": "Image file does not exist on the server" }

    db.session.delete(image)
    db.session.commit()

    return { "success": "Image has been deleted" }, 200



@images.put('/replace/<int:id>')
@jwt_required()
def replace_image(id):
    current_user = get_jwt_identity()

    image = Image.query.filter_by(user_id=current_user, id=id).first()
    if not image:
        return { "error": "Image file not found in database" }, 404
    
    try:
        temp_file = request.files["image"]
    except BadRequestKeyError as e:
        return { "error": "Image file is missing" }, 400
    
    try:
        response = s3_client.upload_fileobj(temp_file, bucket_name, image.name)
        return { "success": "Image replaced" }, 200

    except Exception as e:
        return { "error": "Error uploading image to s3 server" }, 500


def get_random_name():
    string = ""
    for i in range(10):
        string += random.choice(ascii_letters + digits);
    return string
    