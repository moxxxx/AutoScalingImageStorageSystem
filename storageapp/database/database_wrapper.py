from .mysql_dictionary import MySqlDictionary
from .constants import *
import time
import mysql.connector
import threading


class DatabaseWrapper:
    """DatabaseWrapper provides an interface for database interactions.
    DatabaseWrapper is not thread-safe and should be unique for each process."""

    def __init__(self, host, user, password, database):
        self.image_paths = MySqlDictionary(
            host, user, password, database, IMAGE_PATHS_TABLE
        )
        self.metadata = MySqlDictionary(host, user, password, database, METADATA_TABLE)
        self.lock = threading.Lock()

    def get_filepath(self, key):
        """get the image's local filename"""
        with self.lock:
            ret = self.image_paths.get(key)
            return ret

    def add_image(self, key):
        """register a new image"""
        with self.lock:
            ret = self.image_paths.get(key)
            if ret != None:
                return ret

            next_path_id = int(self.metadata.get(FRONTEND_NEXT_PATH_ID))
            next_path = "image_%016x" % (next_path_id + 0x8000000000000000)
            self.image_paths.put(key, next_path)

            self.metadata.put(FRONTEND_NEXT_PATH_ID, next_path_id + 1)
            return next_path

    def clear_images(self):
        """drop all records"""
        with self.lock:
            self.image_paths.clear()
            self.metadata.put(FRONTEND_NEXT_PATH_ID, 1)

    def get_keys(self):
        """get all stored keys"""
        with self.lock:
            ret = self.image_paths.keys()
            return ret

    def put_config(self, capacity, policy):
        """put memcache config"""
        with self.lock:
            self.metadata.put(MEMCACHE_CAPACITY, capacity)
            self.metadata.put(MEMCACHE_POLICY, policy)

    def get_config(self):
        """get memcache config"""
        with self.lock:
            ret = [
                int(self.metadata.get(MEMCACHE_CAPACITY)),
                self.metadata.get(MEMCACHE_POLICY),
            ]
            return ret
