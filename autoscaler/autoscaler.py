from flask import Flask
from flask import request
import json
import random
from .repeated_timer import RepeatedTimer
from .memcache_client import MemcacheClient
import hashlib
import datetime
import requests
import time

import threading


class Config:
    auto_scale = False
    expand_ratio = 2.0
    shrink_ratio = 0.5
    max_miss = 0.8
    min_miss = 0.2


def create_autoscaler(ip_list, web_host, web_port):
    WEB_HOST = web_host
    WEB_PORT = web_port

    assert len(ip_list) == 8

    for ip in ip_list:
        MemcacheClient(ip).clear_cache()

    config = Config()
    app = Flask(__name__)
    app.secret_key = "%016x" % random.randint(0, 16 ** 16 - 1)

    gpl = threading.RLock()

    ring = [0 for i in range(16)]

    def unique(ring):
        s = set()
        for r in ring:
            s.add(r)
        return list(s)

    def get_physical_index(key):
        def get_virtual_index(key):
            return int(hashlib.md5(key.encode()).hexdigest()[0], base=16)

        def virtual_index_to_physical_index(idx):
            return ring[idx]

        physical_index = virtual_index_to_physical_index(get_virtual_index(key))
        return physical_index

    @app.route("/")
    def index():
        return "<p>Auto-scaler</p>"

    @app.route("/get/", methods=["POST"])
    def get():
        with gpl:
            key = request.form["key"]
            physical_index = get_physical_index(key)
            return MemcacheClient(ip_list[physical_index]).get(key)

    @app.route("/put_image/", methods=["POST"])
    def put_image():
        print("enter put image")
        with gpl:
            print("get gpl")
            key = request.form["key"]
            user_image = request.form["user_image"]
            physical_index = get_physical_index(key)
            print("physical index:", physical_index)
            return MemcacheClient(ip_list[physical_index]).put_image(key, user_image)

    @app.route("/invalidate_image/", methods=["POST"])
    def invalidate_image():
        with gpl:
            key = request.form["key"]
            physical_index = get_physical_index(key)
            return MemcacheClient(ip_list[physical_index]).invalidate_image(key)

    @app.route("/get_keys/", methods=["POST"])
    def get_keys():
        with gpl:
            keys = []
            for ip in ip_list:
                keys += json.loads(MemcacheClient(ip).get_keys())["key"]
            returned_data = {"key": keys}
            response = app.response_class(
                response=json.dumps(returned_data), status=200, mimetype="application/json"
            )
            return response

    @app.route("/clear_cache/", methods=["POST"])
    def clear_cache():
        with gpl:
            for ip in ip_list:
                MemcacheClient(ip).clear_cache()
            return {"success": "true"}

    @app.route("/get_ring/", methods=["POST"])
    def get_ring():
        with gpl:
            return str(ring)

    def serialize():
        dic = {}
        for ip in ip_list:
            client = MemcacheClient(ip)
            keys = json.loads(client.get_keys())["key"]
            for key in keys:
                ret = json.loads(client.get(key))
                assert ret["success"] == "true"
                dic[key] = ret["content"]
        return dic

    def refresh():
        print("enter refresh")
        size_now = len(unique(ring))
        print("size now:", size_now)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        url = "http://" + WEB_HOST + ":" + str(WEB_PORT) + "/update_notification/"
        requests.post(url, data={'size_now': size_now, 'timestamp': timestamp})
        dic = serialize()
        print("dic.keys:", dic.keys())
        for ip in ip_list:
            MemcacheClient(ip).clear_cache()
        for key in dic.keys():
            physical_index = get_physical_index(key)
            print("key:", key, "physical_index:", physical_index)
            MemcacheClient(ip_list[physical_index]).put_image(key, dic[key])
        return

    history = []

    def get_hit_miss():
        hit = 0
        miss = 0
        total_size = 0
        num_items = 0
        for ip in ip_list:
            js = json.loads(MemcacheClient(ip).get_hit_miss())
            hit += js["hit"]
            miss += js["miss"]
            total_size += js["total_size"]
            num_items += js["num_items"]
        return hit, miss, total_size, num_items

    hit, miss, total_size, num_items = get_hit_miss()
    history.append(
        {
            "time_now": datetime.datetime.now().ctime(),
            "hit": hit,
            "miss": miss,
            "total_size": total_size,
            "num_items": num_items,
        }
    )

    def resize():
        with gpl:
            nonlocal ring
            current_len = len(unique(ring))
            hit, miss, total_size, num_items = get_hit_miss()
            nonlocal history
            history.append(
                {
                    "time_now": datetime.datetime.now().ctime(),
                    "hit": hit,
                    "miss": miss,
                    "total_size": total_size,
                    "num_items": num_items,
                }
            )
            history = history[-30:]

            if config.auto_scale == False:
                return

            def get_action(hit, miss):
                if hit + miss == 0:
                    ratio = 0.5
                else:
                    ratio = miss / (hit + miss)
                if ratio >= config.max_miss:
                    return "grow"
                elif ratio <= config.min_miss:
                    return "shrink"
                else:
                    return "hold"

            action = get_action(hit, miss)

            print("hit:", hit, "miss:", miss, "action:", action)

            if action == "hold":
                pass
            elif action == "shrink":
                if current_len <= 1:
                    pass
                else:
                    resized_length = int(current_len * config.shrink_ratio)
                    if resized_length <= 1:
                        resized_length = 1
                    ring = [
                        i % resized_length for i in range(16)
                    ]
                    refresh()
            elif action == "grow":
                if current_len >= 8:
                    pass
                else:
                    resized_length = int(current_len * config.expand_ratio)
                    if resized_length >= 8:
                        resized_length = 8
                    ring = [
                        i % resized_length for i in range(16)
                    ]
                    refresh()

            for ip in ip_list:
                MemcacheClient(ip).reset_hit_miss()

    # controller
    @app.route("/change_mode/", methods=["POST"])
    def change_mode():
        with gpl:
            config.auto_scale = not config.auto_scale
            response = app.response_class(
                response=json.dumps({"success": "true"}),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/get_mode/", methods=["POST"])
    def get_mode():
        with gpl:
            response = app.response_class(
                response=json.dumps(
                    {
                        "success": "true",
                        "mode": ("auto" if config.auto_scale else "manual"),
                    }
                ),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/manual_grow_pool_size/", methods=["POST"])
    def manual_grow_pool_size():
        with gpl:
            nonlocal ring
            returned_data = {"success": "true"}
            current_len = len(unique(ring))
            if current_len >= 8:
                returned_data = {"success": "false"}
            else:
                ring = [i % int(current_len + 1) for i in range(16)]
                refresh()
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/manual_shrink_pool_size/", methods=["POST"])
    def manual_shrink_pool_size():
        with gpl:
            nonlocal ring
            returned_data = {"success": "true"}
            current_len = len(unique(ring))
            if current_len <= 1:
                returned_data = {"success": "false"}
            else:
                ring = [i % int(current_len - 1) for i in range(16)]
                refresh()
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/cache_pool_status/", methods=["POST"])
    def cache_pool_status():
        with gpl:
            ec2_list = [
                "EC2_0",
                "EC2_1",
                "EC2_2",
                "EC2_3",
                "EC2_4",
                "EC2_5",
                "EC2_6",
                "EC2_7",
            ]
            current_len = len(unique(ring))
            status_list = ["active"] * current_len + ["inactive"] * (8 - current_len)

            returned_data = {
                "ec2_list": ec2_list,
                "status_list": status_list,
                "mode": ("auto" if config.auto_scale else "manual"),
                "node_num": current_len,
                "max_missrate": config.max_miss,
                "min_missrate": config.min_miss,
                "expand_ratio": config.expand_ratio,
                "shrink_ratio": config.shrink_ratio,
            }
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/refresh_configuration/", methods=["POST"])
    def refresh_configuration():
        with gpl:
            capacity = request.form["capacity"]
            policy = request.form["policy"]
            returned_data = {"success": "true"}

            for ip in ip_list:
                MemcacheClient(ip).refresh_configuration(capacity, policy)
                MemcacheClient(ip).clear_cache()

            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/show_statistics/", methods=["POST", "GET"])
    def show_statistics():
        with gpl:
            returned_data = {"success": "true", "data_list": history}
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/update_policy/", methods=["POST"])
    def update_policy():
        with gpl:
            config.max_miss = float(request.form["max_missrate"])
            config.min_miss = float(request.form["min_missrate"])
            config.expand_ratio = float(request.form["expand_ratio"])
            config.shrink_ratio = float(request.form["shrink_ratio"])
            returned_data = {"success": "true"}
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/get_last_min/", methods=["POST"])
    def get_last_min():
        with gpl:
            returned_data = {"hit": history[-1]["hit"], "miss": history[-1]["miss"]}
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    @app.route("/set_node_num/", methods=["POST"])
    def set_node_num():
        with gpl:
            nonlocal ring
            returned_data = {"success": "true"}
            new_len = int(request.form["node_num"])
            if new_len <= 0 or new_len >= 9:
                returned_data = {"success": "false"}
            else:
                ring = [i % int(new_len) for i in range(16)]
                refresh()
            response = app.response_class(
                response=json.dumps(returned_data),
                status=200,
                mimetype="application/json",
            )
            return response

    RepeatedTimer(interval=10, target=resize).start()

    return app
