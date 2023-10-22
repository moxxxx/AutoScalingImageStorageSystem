import os
import webapp

if __name__ == "__main__":
    webapp.create_webapp(
        image_storage_host=os.environ["IMAGE_STORAGE_HOST"],
        image_storage_port=os.environ["IMAGE_STORAGE_PORT"],
        auto_scaler_host=os.environ["AUTO_SCALER_HOST"],
        auto_scaler_port=os.environ["AUTO_SCALER_PORT"],
        image_directory=os.environ["IMAGE_DIRECTORY"]
    ).run(host="localhost", port=os.environ["WEB_PORT"], debug=False)
