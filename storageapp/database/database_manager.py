from .mysql_dictionary_cursor import MySqlDictionary
from .constants import *


class DatabaseManager:
    def __init__(
        self,
        cursor,
        database,
    ):
        self.cursor = cursor
        self.database = database

    def construct(self):
        cursor = self.cursor
        cursor.execute(f"""CREATE DATABASE {self.database}""")
        cursor.execute(f"""USE {self.database}""")

        dic = MySqlDictionary(cursor, table=METADATA_TABLE)
        dic.construct()
        dic.put(FRONTEND_NEXT_PATH_ID, 1)
        dic.put(MEMCACHE_CAPACITY, 128)
        dic.put(MEMCACHE_POLICY, "LRU")  # or "Random"

        dic = MySqlDictionary(cursor, table=IMAGE_PATHS_TABLE)
        dic.construct()

        cursor.execute(
            f"""CREATE TABLE {STATIS_TABLE}
({STATIS_KEY_ID} int,
 {STATIS_KEY_TIME} int,
 {STATIS_KEY_NUM_ITEMS} int,
 {STATIS_KEY_TOTAL_SIZE} int,
 {STATIS_KEY_TOTAL_REQUEST} int,
 {STATIS_KEY_MISS_RATE} float,
 {STATIS_KEY_HIT_RATE} float)"""
        )

    def destruct(self):
        cursor = self.cursor
        cursor.execute(f"""DROP DATABASE {self.database}""")
