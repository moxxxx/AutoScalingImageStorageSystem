from flask import Flask
from flask import request
import json
from .memcache import Memcache
import random


def create_cacheapp():

    cacheapp = Flask(__name__)
    cacheapp.secret_key = "%016x" % random.randint(0, 16**16 - 1)
    memcache = Memcache()

    total_miss = 0
    total_hit = 0

    @cacheapp.route("/")
    def index():
        return "Cacheapp"

    @cacheapp.route("/get_keys/", methods=["POST", "GET"])
    def get_keys():
        keys = list(memcache.cache.keys())
        data = {"key": keys}
        response = cacheapp.response_class(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
        return response

    @cacheapp.route("/put_image/", methods=["POST", "GET"])
    def put_image():
        ret = memcache.put(request.form["key"], request.form["user_image"])
        return "success" if ret else "failed"

    @cacheapp.route("/get/", methods=["POST", "GET"])
    def get_image():
        nonlocal total_hit
        nonlocal total_miss
        key = request.form["key"]
        image = memcache.get(key)
        if image:
            data = {"success": "true", "key": key, "content": image}
            response = cacheapp.response_class(
                response=json.dumps(data), status=200, mimetype="application/json"
            )
            miss = False
        else:
            data = {"success": "false", "key": key, "content": None}
            response = cacheapp.response_class(
                response=json.dumps(data), status=200, mimetype="application/json"
            )
            miss = True

        if miss:
            total_miss += 1
        else:
            total_hit += 1

        return response

    @cacheapp.route("/invalidate_image/", methods=["POST"])
    def invalidate_image():
        memcache.invalidateKey(request.form["key"])
        return "success"

    @cacheapp.route("/clear_cache/", methods=["POST"])
    def clear_cache():
        memcache.clear()
        total_hit = 0
        total_miss = 0
        return "success"

    @cacheapp.route("/refresh_configuration/", methods=["POST"])
    def refresh_configuration():
        capacity = int(request.form["capacity"])
        policy = request.form["policy"]
        memcache.refreshConfiguration(capacity, policy)
        return "success"

    @cacheapp.route("/get_hit_miss/", methods=["POST"])
    def get_hit_miss():
        response = cacheapp.response_class(
            response=json.dumps(
                {
                    "hit": total_hit,
                    "miss": total_miss,
                    "num_items": memcache.getNumItems(),
                    "total_size": memcache.getSpace(),
                }
            ),
            status=200,
            mimetype="application/json",
        )
        return response

    @cacheapp.route("/reset_hit_miss/", methods=["POST"])
    def reset_hit_miss():
        nonlocal total_hit
        nonlocal total_miss
        total_miss = 0
        total_hit = 0
        return "success"

    return cacheapp
