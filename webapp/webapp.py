from flask import Flask, jsonify
from flask import render_template, url_for, request, redirect, json, flash
import os
import requests
import shutil
import random


class Notification:
    timestamp = "12:34:56"
    size_now = 0


def create_webapp(image_storage_host, image_storage_port, auto_scaler_host, auto_scaler_port, image_directory):
    LOCAL_FOLDER = image_directory
    IMAGE_STORAGE_HOST = image_storage_host
    IMAGE_STORAGE_PORT = image_storage_port
    AUTO_SCALER_HOST = auto_scaler_host
    AUTO_SCALER_PORT = auto_scaler_port

    noti = Notification()

    webapp = Flask(__name__)
    webapp.secret_key = "%016x" % random.randint(0, 16 ** 16 - 1)

    def valid(name):
        if name[0].isdigit():
            return False
        for c in name:
            if not (c.isalnum() or c == '_'):
                return False
        return True

    @webapp.route("/")
    def main():
        return render_template("index.html")

    @webapp.route("/get/", methods=["POST"])
    def get():
        key = request.form.get("key")
        if not (valid(key) and len(key) <= 20):
            flash("Error!", "INVALID KEY.")
            return redirect(url_for("main"))
        if (key is None) or (len(key) < 1):
            flash("Error!", "Please input a key.")
            return redirect(url_for("main"))
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/get/"
        ret = requests.post(url, data={"key": key})
        data = json.loads(ret.content)
        if data["success"] == "true":
            user_image = data["content"]
        else:
            url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/get/"
            ret = requests.post(url, data={"key": key})
            data = json.loads(ret.content)
            if data["success"] == "true":
                user_image = data["content"]
                url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/put_image/"
                requests.post(url, data={"key": key, "user_image": user_image})
            else:
                flash("Something Wrong!", "The key queried does not exist.")
                return redirect(url_for("main"))
        data = {"success": "true", "key": key}
        response = webapp.response_class(
            response=json.dumps(data), status=400, mimetype="application/json"
        )
        return render_template("showImage.html", key=key, user_image=user_image, response=response)

    @webapp.route("/upload/", methods=["POST"])
    def upload():
        try:
            key = request.form.get("key")

            if not (valid(key) and len(key) <= 20):
                flash("Error!", "INVALID KEY.")
                return redirect(url_for("main"))

            file = request.files["file"]
            suffix = file.filename.split(".")[1]
            image_type_list = ['bmp', 'dib', 'png', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm', 'tif', 'tiff']

            if not suffix in image_type_list:
                flash("Error!", "Image format you uploaded is not recognized.")
                return redirect(url_for("main"))

            filepath = os.path.join(LOCAL_FOLDER, key)
            file.save(filepath)

            url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/upload/"
            ret = requests.post(url, {"key": key})
            data = json.loads(ret.content)

            if data['success'] == 'true':
                url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/invalidate_image/"
                requests.post(url, {"key": key})
                flash("Cong!", "Upload success.")
            else:
                flash("Error!", "Something Wrong.")

            return redirect(url_for("main"))
        except:
            flash("Error!", "Something Wrong.")
            return redirect(url_for("main"))

    @webapp.route("/database/", methods=["POST", "GET"])
    def show_database():
        url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/database/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        key_list = list(data['key'])
        return render_template("database.html", key_list=key_list)

    @webapp.route("/delete_all/", methods=["POST"])
    def delete_all():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/clear_cache/"
        requests.post(url)
        url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/delete_all/"
        ret = requests.post(url)
        data = json.loads(ret.content)

        shutil.rmtree(LOCAL_FOLDER)
        os.mkdir(LOCAL_FOLDER)

        if data['success'] == 'true':
            flash("Completed!", "You have deleted all keys and values from the application.")
        else:
            flash("Error!", "Something Wrong.")
        return redirect(url_for("show_database"))

    @webapp.route("/memcache/", methods=["POST", "GET"])
    def show_memcache():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/get_keys/"
        ret = requests.post(url)
        content = json.loads(ret.content)
        key_list = list(content["key"])
        return render_template("memcache.html", key_list=key_list)

    @webapp.route("/clear_cache/", methods=["POST"])
    def clear_cache():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/clear_cache/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have deleted all keys and values from the memcache.")
        else:
            flash("Error!", "Something Wrong")
        return redirect(url_for("show_memcache"))

    @webapp.route('/notification/', methods=["POST", "GET"])
    def notification():
        return jsonify({
            'size_now': noti.size_now,
            'timestamp': noti.timestamp,
        })

    @webapp.route('/update_notification/', methods=["POST"])
    def update_notification():
        noti.size_now = request.form['size_now']
        noti.timestamp = request.form['timestamp']
        returned_data = {'success': 'true'}
        response = webapp.response_class(
            response=json.dumps(returned_data), status=200, mimetype="application/json"
        )
        return response

    @webapp.route("/api/getNumNodes/", methods=["POST"])
    def api_get_num_nodes():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/cache_pool_status/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if 'node_num' in data.keys():
            num_nodes = int(data['node_num'])
            return {
                "success": "true",
                "numNodes": num_nodes
            }
        else:
            return {
                "success": "false",
                "numNodes": -1
            }

    @webapp.route("/api/getRate", methods=["POST"])
    def api_get_rate():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/get_last_min/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        hit = int(data['hit'])
        miss = int(data['miss'])
        rate = request.args.get('rate')
        if rate == 'hit':
            return {
                "success": "true",
                "rate": "hit",
                "value": (float(hit) / float(hit + miss) if hit + miss != 0 else -1)
            }
        elif rate == 'miss':
            return {
                "success": "true",
                "rate": "miss",
                "value": (float(miss) / float(hit + miss) if hit + miss != 0 else -1)
            }
        else:
            return {
                "success": "false",
                "rate": "false",
                "value": 0.0
            }

    @webapp.route("/api/configure_cache", methods=["POST"])
    def api_config_cache():
        mode = request.args.get('mode')
        numNodes = request.args.get('numNodes')
        cacheSize = request.args.get('cacheSize')
        policy = request.args.get('policy')
        expRatio = request.args.get('expRatio')
        shrinkRatio = request.args.get('shrinkRatio')
        maxMiss = request.args.get('maxMiss')
        minMiss = request.args.get('minMiss')

        if not mode is None:
            url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/get_mode/"
            ret = requests.post(url)
            current_mode = (json.loads(ret.content))['mode']
            if not mode == current_mode:
                url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/change_mode/"
                requests.post(url)
        if not numNodes is None:
            if not numNodes.isdigit():
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "message": "illegal parameter"
                    }
                }
            numNodes = int(numNodes)
            if numNodes > 8 or numNodes < 1:
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "message": "illegal parameter"
                    }
                }
            url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/set_node_num/"
            requests.post(url, data={'node_num': int(numNodes)})
        if not cacheSize is None:
            if policy is None:
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "message": "illegal parameter"
                    }
                }
            cacheSize = int(cacheSize)
            url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/refresh_configuration/"
            requests.post(url, data={'capacity': cacheSize, 'policy': policy})
        if not expRatio is None:
            if (maxMiss is None) or (minMiss is None) or (shrinkRatio is None) or (mode is 'manual'):
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "message": "illegal parameter"
                    }
                }
            expRatio = float(expRatio)
            shrinkRatio = float(shrinkRatio)
            maxMiss = float(maxMiss)
            minMiss = float(minMiss)
            if maxMiss <= minMiss or maxMiss > 1.0 or maxMiss <= 0.0 or minMiss >= 1.0 or minMiss < 0.0 \
                    or expRatio > 8.0 or expRatio < 1.0 or shrinkRatio > 1.0 or shrinkRatio <= 0.0:
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "message": "illegal parameter"
                    }
                }
            url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/update_policy/"
            requests.post(url, data={'max_missrate': maxMiss, 'min_missrate': minMiss,
                                     'expand_ratio': expRatio, 'shrink_ratio': shrinkRatio})
        return {
            "success": "true",
            "mode": mode,
            "numNodes": numNodes,
            "cacheSize": cacheSize,
            "policy": policy
        }

    @webapp.route("/api/delete_all/", methods=["POST"])
    def api_delete_all():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/clear_cache/"
        requests.post(url)
        url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/delete_all/"
        requests.post(url)

        shutil.rmtree(LOCAL_FOLDER)
        os.mkdir(LOCAL_FOLDER)

        return {
            "success": "true"
        }

    @webapp.route("/api/upload/", methods=["POST"])
    def api_upload():
        try:
            key = request.form['key']
            file = request.files["file"]

            if not (valid(key) and len(key) <= 20):
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "key": key,
                        "message": "illegal key"
                    }
                }

            suffix = file.filename.split(".")[1]
            image_type_list = ['bmp', 'dib', 'png', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm', 'tif', 'tiff']

            if not suffix in image_type_list:
                return {
                    "success": "false",
                    "error": {
                        "code": 403,
                        "key": key,
                        "message": "illegal image type"
                    }
                }

            filepath = os.path.join(LOCAL_FOLDER, key)
            file.save(filepath)

            url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/upload/"
            ret = requests.post(url, data={"key": key})
            data = json.loads(ret.content)

            if data['success'] == 'true':
                url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/invalidate_image/"
                requests.post(url, {"key": key})
                return {"success": "true", "key": key}
            else:
                return {"success": "false", "key": key}

        except:
            return {"success": "false", "key": key}

    @webapp.route("/api/list_keys/", methods=["POST"])
    def api_list_keys():
        url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/database/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        key_list = list(data['key'])
        return {
            "success": "true",
            "keys": key_list
        }

    @webapp.route("/api/key/<key_value>", methods=["POST"])
    def api_get(key_value):
        if not (valid(key_value) and len(key_value) <= 20):
            return {
                "success": "false",
                "error": {
                    "code": 403,
                    "message": "illegal key"
                }
            }
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/get/"
        ret = requests.post(url, data={"key": key_value})
        data = json.loads(ret.content)
        if data["success"] == "true":
            user_image = data["content"]
        else:
            url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/get/"
            ret = requests.post(url, data={"key": key_value})
            data = json.loads(ret.content)
            if data["success"] == "true":
                user_image = data["content"]
                url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/put_image/"
                requests.post(url, data={"key": key_value, "user_image": user_image})
            else:
                return {
                    "success": "false",
                    "error": {
                        "code": 404,
                        "message": "key value not exist"
                    }
                }
        return {
            "success": "true",
            "key": key_value,
            "content": user_image
        }

    return webapp
