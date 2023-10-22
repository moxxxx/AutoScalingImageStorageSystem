import os
import storageapp

if __name__ == "__main__":
    storageapp.create_storageapp(
        rds_host=os.environ["RDS_HOST"],
        rds_user=os.environ["RDS_USER"],
        rds_password=os.environ["RDS_PASSWORD"],
        rds_database=os.environ["RDS_DATABASE"],
        bucket_name=os.environ["BUCKET_NAME"],
        local_folder=os.environ["IMAGE_DIRECTORY"]
    ).run(host="localhost", port=os.environ["IMAGE_STORAGE_PORT"], debug=False)
