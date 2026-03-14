import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"]
    )

# Global connection
db = get_connection()
cursor = db.cursor()