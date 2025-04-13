import MySQLdb

try:
    db = MySQLdb.connect(host="localhost", user="root", passwd="1234", db="flask_login")
    cursor = db.cursor()
    print("Connection successful!")
    cursor.close()
except MySQLdb.Error as e:
    print(f"Database error: {e}")
finally:
    if db:
        db.close()
