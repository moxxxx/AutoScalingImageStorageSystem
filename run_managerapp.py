import os
import managerapp

if __name__ == "__main__":
    managerapp.create_managerapp(
        auto_scaler_host=os.environ["AUTO_SCALER_HOST"],
        auto_scaler_port=os.environ["AUTO_SCALER_PORT"],
        image_storage_host=os.environ["IMAGE_STORAGE_HOST"],
        image_storage_port=os.environ["IMAGE_STORAGE_PORT"],
    ).run(host="localhost", port=os.environ["MANAGER_PORT"], debug=False)
