import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Satyam@123",
    database="scoreme_system"
)

cursor = db.cursor()