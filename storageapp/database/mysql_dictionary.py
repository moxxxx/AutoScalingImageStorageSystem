DBKEY = "DBKEY"
DBVALUE = "DBVALUE"

import mysql.connector


def warning(msg):
    print(msg)


class MySqlDictionary:
    def __init__(self, host, user, password, database, table):
        self.db_key = DBKEY
        self.db_value = DBVALUE
        self.table = table

        self.url = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }

    def construct(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(
            f"""CREATE TABLE {self.table} ({self.db_key} text, {self.db_value} text)"""
        )

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def get(self, key):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

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

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return ret[0][0]

    def put(self, key, value):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(
            f"DELETE FROM {self.table} WHERE {self.db_key} = %s", (key,)
        )
        self.cursor.execute(
            f"INSERT INTO {self.table} ({self.db_key}, {self.db_value}) VALUES (%s, %s)",
            (key, value),
        )

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def remove(self, key):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(
            f"DELETE FROM {self.table} WHERE {self.db_key} = %s", (key,)
        )

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def keys(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(f"SELECT {self.db_key} FROM {self.table}")
        ret = [e[0] for e in self.cursor]

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return ret

    def values(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(f"SELECT {self.db_value} FROM {self.table}")
        ret = [e[0] for e in self.cursor]

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return ret

    def clear(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(f"DELETE FROM {self.table}")

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def items(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(f"SELECT * FROM {self.table}")
        ret = [e for e in self.cursor]

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return ret

    def length(self):
        self.cnx = mysql.connector.connect(**self.url)
        self.cursor = self.cnx.cursor()

        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
        ret = [e[0] for e in self.cursor]

        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return ret[0]
