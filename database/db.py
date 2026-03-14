import mysql.connector

db = mysql.connector.connect(
    host="interchange.proxy.rlwy.net",
    port=49694,
    user="root",
    password="EKxmtrcxMQyuZCpnWAqzBUHMjYfVQutn",
    database="railway"
)

cursor = db.cursor()