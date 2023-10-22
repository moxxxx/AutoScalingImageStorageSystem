DBKEY = "DBKEY"
DBVALUE = "DBVALUE"


def warning(msg):
    print(msg)


class MySqlDictionary:
    def __init__(self, cursor, table):
        self.db_key = DBKEY
        self.db_value = DBVALUE
        self.table = table
        self.cursor = cursor

    def construct(self):
        self.cursor.execute(
            f"""CREATE TABLE {self.table} ({self.db_key} text, {self.db_value} text)"""
        )

    def get(self, key):
        self.cursor.execute(
            f"SELECT {self.db_value} FROM {self.table} WHERE {self.db_key} = %s", (key,)
        )
        ret = [e for e in self.cursor]
        if len(ret) > 1:
            warning(
                f"Warning: MySqlDictionary: more than one row has key = {key}, whose values are {ret}."
            )
        if len(ret) == 0:
            return None
        return ret[0][0]

    def put(self, key, value):
        self.cursor.execute(
            f"DELETE FROM {self.table} WHERE {self.db_key} = %s", (key,)
        )
        self.cursor.execute(
            f"INSERT INTO {self.table} ({self.db_key}, {self.db_value}) VALUES (%s, %s)",
            (key, value),
        )

    def remove(self, key):
        self.cursor.execute(
            f"DELETE FROM {self.table} WHERE {self.db_key} = %s", (key,)
        )

    def keys(self):
        self.cursor.execute(f"SELECT {self.db_key} FROM {self.table}")
        ret = [e[0] for e in self.cursor]
        return ret

    def values(self):
        self.cursor.execute(f"SELECT {self.db_value} FROM {self.table}")
        ret = [e[0] for e in self.cursor]
        return ret

    def clear(self):
        self.cursor.execute(f"DELETE FROM {self.table}")

    def items(self):
        self.cursor.execute(f"SELECT * FROM {self.table}")
        ret = [e for e in self.cursor]
        return ret

    def length(self):
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
        ret = [e[0] for e in self.cursor]
        return ret[0]
