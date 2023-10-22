import json
import random

import requests
from flask import Flask, request, flash, redirect, url_for
from flask import render_template


def create_managerapp(auto_scaler_host, auto_scaler_port, image_storage_host, image_storage_port):
    managerapp = Flask(__name__)
    managerapp.secret_key = "%016x" % random.randint(0, 16 ** 16 - 1)
    AUTO_SCALER_HOST = auto_scaler_host
    AUTO_SCALER_PORT = auto_scaler_port
    IMAGE_STORAGE_HOST = image_storage_host
    IMAGE_STORAGE_PORT = image_storage_port

    @managerapp.route("/")
    def main():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/cache_pool_status/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        ec2_list = list(data['ec2_list'])
        status_list = list(data['status_list'])
        mode = data['mode']
        node_num = data['node_num']
        max_missrate = data['max_missrate']
        min_missrate = data['min_missrate']
        expand_ratio = data['expand_ratio']
        shrink_ratio = data['shrink_ratio']
        return render_template("index.html", ec2_list=ec2_list, status_list=status_list, node_num=node_num, mode=mode,
                               max_missrate=max_missrate, min_missrate=min_missrate, expand_ratio=expand_ratio,
                               shrink_ratio=shrink_ratio)

    @managerapp.route("/clear_cache/", methods=["POST"])
    def clear_cache():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/clear_cache/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have deleted all keys and values from the memcache.")
        else:
            flash("Error!", "Something Wrong")
        return redirect(url_for("show_statistics"))

    @managerapp.route("/clear_all/", methods=["POST"])
    def clear_all():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/clear_cache/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if data['success'] == 'true':
            url = "http://" + IMAGE_STORAGE_HOST + ":" + str(IMAGE_STORAGE_PORT) + "/delete_all/"
            ret = requests.post(url)
            data = json.loads(ret.content)
            if data['success'] == 'true':
                flash("Completed!", "You have deleted all keys and values.")
            else:
                flash("Error!", "Something Wrong")
        else:
            flash("Error!", "Something Wrong")
        return redirect(url_for("show_statistics"))

    @managerapp.route("/config/", methods=["POST"])
    def config():
        capacity = request.form.get("capacity")
        if (not capacity.isdigit()) or (int(capacity) > 1024):
            flash("Error!", "Please enter an integer between 1 and 1024")
            return redirect(url_for("show_statistics"))
        policy = request.form.get("policy")
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/refresh_configuration/"
        ret = requests.post(url, data={'capacity': capacity, 'policy': policy})
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have successfully configured the memcache.")
        else:
            flash("Error!", "Something Wrong")
        return redirect(url_for("show_statistics"))

    @managerapp.route('/manual_grow_pool_size/', methods=['POST'])
    def manual_grow_pool_size():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/manual_grow_pool_size/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have successfully configured the memcache.")
        else:
            flash("Sorry!", "There can be a maximum of 8 Nodes")
        return redirect(url_for("main"))

    @managerapp.route('/manual_shrink_pool_size/', methods=['POST'])
    def manual_shrink_pool_size():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/manual_shrink_pool_size/"
        ret = requests.post(url)
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have successfully configured the memcache.")
        else:
            flash("Sorry!", "There is at least 1 node")
        return redirect(url_for("main"))

    @managerapp.route('/change_mode/', methods=['POST', 'GET'])
    def change_mode():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/change_mode/"
        requests.post(url)
        return redirect(url_for("main"))

    @managerapp.route('/show_statistics/', methods=['POST', 'GET'])
    def show_statistics():
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/show_statistics/"
        ret = requests.post(url)
        temp_data = (json.loads(ret.content))['data_list']
        data_list = [{'time_now': data['time_now'],
                      'miss_rate': 0 if float(data['hit'] + data['miss']) == 0.0 else float(data['miss']) / float(
                          data['hit'] + data['miss']),
                      'hit_rate': 0 if float(data['hit'] + data['miss']) == 0.0 else float(data['hit']) / float(
                          data['hit'] + data['miss']),
                      'num_items': data['num_items'],
                      'total_size': float(data['total_size']),
                      'request_per_min': int(data['hit']) + int(data['miss'])
                      } for data in temp_data]
        return render_template("statistic.html", data_list=data_list)

    @managerapp.route('/update_policy/', methods=['POST'])
    def update_policy():
        max_missrate = request.form.get("max_missrate")
        if (not type(eval(max_missrate)) == float) or (float(max_missrate) > 1.0) or (float(max_missrate) <= 0.0):
            flash("Error!", "0.0 < Max Missrate <= 1.0")
            return redirect(url_for("main"))
        min_missrate = request.form.get("min_missrate")
        if (not type(eval(min_missrate)) == float) or (float(min_missrate) >= 1.0) or (float(min_missrate) < 0.0):
            flash("Error!", "0.0 <= Min Missrate < 1.0")
            return redirect(url_for("main"))
        if float(min_missrate) >= float(max_missrate):
            flash("Error!", "Min Missrate should be smaller than Max Missrate.")
            return redirect(url_for("main"))
        expand_ratio = request.form.get("expand_ratio")
        if (not type(eval(expand_ratio)) == float) or (float(expand_ratio) > 8.0) or (float(expand_ratio) < 1.0):
            flash("Error!", "1.0 <= Expand Ratio <= 8.0")
            return redirect(url_for("main"))
        shrink_ratio = request.form.get("shrink_ratio")
        if (not type(eval(shrink_ratio)) == float) or (float(shrink_ratio) > 1.0) or (float(shrink_ratio) <= 0.0):
            flash("Error!", "0.0 < Shrink Ratio <= 1.0")
            return redirect(url_for("main"))
        url = "http://" + AUTO_SCALER_HOST + ":" + str(AUTO_SCALER_PORT) + "/update_policy/"
        ret = requests.post(url, data={'max_missrate': max_missrate, 'min_missrate': min_missrate,
                                       'expand_ratio': expand_ratio, 'shrink_ratio': shrink_ratio})
        data = json.loads(ret.content)
        if data['success'] == 'true':
            flash("Completed!", "You have successfully updated auto-scaling policy.")
        else:
            flash("Error!", "Update failed.")
        return redirect(url_for("main"))


    return managerapp
