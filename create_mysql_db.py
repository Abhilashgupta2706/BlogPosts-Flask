import mysql.connector

from decouple import config
# mydb = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     passwd='mysqlpasswrd',
# )

mydb = mysql.connector.connect(
    host=config("host"),
    user=config("user"),
    passwrd=config("passwrd")
)

my_cursor = mydb.cursor()
my_cursor.execute('CREATE DATABASE bwe0ewbvmzknevisoqez')
my_cursor.execute('SHOW DATABASES')
for db in my_cursor:
    print(db)
