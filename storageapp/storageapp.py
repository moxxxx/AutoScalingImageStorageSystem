import os
from base64 import b64encode

import boto3
from flask import Flask
from flask import request
import json
from storageapp.database import DatabaseWrapper
import random


def create_storageapp(rds_host, rds_user, rds_password, rds_database, bucket_name, local_folder):
    BUCKET_NAME = bucket_name
    LOCAL_FOLDER = local_folder

    storageapp = Flask(__name__)
    storageapp.secret_key = "%016x" % random.randint(0, 16 ** 16 - 1)

    rds = DatabaseWrapper(
        host=rds_host,
        user=rds_user,
        password=rds_password,
        database=rds_database,
    )

    @storageapp.route("/")
    def index():
        return "<p>Hello, This is StorageApp!</p>"

    @storageapp.route("/get/", methods=["POST"])
    def get_image():
        key = request.form["key"]
        data = {"success": "false", "key": key, "content": None}
        file_name = rds.get_filepath(key)
        if not file_name is None:
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            j = obj['Body'].read()
            user_image = b64encode(j).decode("utf-8")
            if user_image:
                data = {"success": "true", "key": key, "content": user_image}
        response = storageapp.response_class(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
        return response

    @storageapp.route("/upload/", methods=["POST"])
    def upload_image():
        key = request.form.get('key')
        rds.add_image(key)
        filepath = os.path.join(LOCAL_FOLDER, key)
        s3 = boto3.client('s3')
        s3.upload_file(filepath, BUCKET_NAME, key)
        data = {"success": "true", "key": key}
        response = storageapp.response_class(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
        return response

    @storageapp.route("/database/", methods=["POST"])
    def get_keys_from_database():
        key_list = rds.get_keys()
        data = {"success": "true", "key": key_list}
        response = storageapp.response_class(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
        return response

    @storageapp.route("/delete_all/", methods=["POST"])
    def delete_all_image():
        rds.clear_images()
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.objects.all().delete()
        data = {"success": "true"}
        response = storageapp.response_class(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
        return response

    return storageapp
