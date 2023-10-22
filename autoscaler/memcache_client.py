import requests


class MemcacheClient:
    def __init__(self, ip):
        self.ip = ip

    def get(self, key):
        url = "http://" + self.ip + "/get/"
        ret = requests.post(url, data={"key": key})
        assert ret.status_code == 200
        return ret.text

    def get_keys(self):
        url = "http://" + self.ip + "/get_keys/"
        ret = requests.post(url)
        assert ret.status_code == 200
        return ret.text

    def put_image(self, key, user_image):
        url = "http://" + self.ip + "/put_image/"
        ret = requests.post(url, data={"key": key, "user_image": user_image})
        assert ret.status_code == 200
        return ret.text

    def invalidate_image(self, key):
        url = "http://" + self.ip + "/invalidate_image/"
        ret = requests.post(url, data={"key": key})
        assert ret.status_code == 200
        return ret.text

    def clear_cache(self):
        url = "http://" + self.ip + "/clear_cache/"
        ret = requests.post(url)
        assert ret.status_code == 200
        return ret.text

    def get_hit_miss(self):
        url = "http://" + self.ip + "/get_hit_miss/"
        ret = requests.post(url)
        assert ret.status_code == 200
        return ret.text

    def reset_hit_miss(self):
        url = "http://" + self.ip + "/reset_hit_miss/"
        ret = requests.post(url)
        assert ret.status_code == 200
        return ret.text

    def refresh_configuration(self, capacity, policy):
        url = "http://" + self.ip + "/refresh_configuration/"
        ret = requests.post(url, data={"capacity": capacity, "policy": policy})
        assert ret.status_code == 200
        return ret.text
