import mysql.connector
import os

db = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    port=int(os.environ.get("MYSQL_PORT", 3306)),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", "Satyam@123"),
    database=os.environ.get("MYSQL_DATABASE", "scoreme_system")
)

cursor = db.cursor()