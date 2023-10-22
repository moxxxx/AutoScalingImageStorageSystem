import os

import mysql.connector

from storageapp.database.database_manager import DatabaseManager

cnx = mysql.connector.connect(
    host="database-1.coezjxuc7gcz.us-east-1.rds.amazonaws.com",
    user="admin",
    password="12345678",
)


manager = DatabaseManager(cnx.cursor(), "ece1779a2")

manager.destruct()
