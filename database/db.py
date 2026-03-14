import mysql.connector
import os

# Get all values
host = os.environ.get("MYSQL_HOST")
port_str = os.environ.get("MYSQL_PORT", "3306")
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
database = os.environ.get("MYSQL_DATABASE")

# Safe port conversion
try:
    port = int(port_str) if port_str and port_str.strip() else 3306
except ValueError:
    port = 3306

print(f"Connecting to: {host}:{port} db={database}")

db = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

cursor = db.cursor()