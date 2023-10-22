import os
import autoscaler

if __name__ == "__main__":
    autoscaler.create_autoscaler(web_host=os.environ["WEB_HOST"],
                                 web_port=os.environ["WEB_PORT"], ip_list=eval(os.environ["CACHE_LIST"])).run(
        host="localhost",
        port=os.environ["AUTO_SCALER_PORT"],
        debug=False,
    )

