import pymysql
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=os.getenv("db"),
  host=os.getenv("host"),
  password=os.getenv("password"),
  read_timeout=timeout,
  port= int(os.getenv("port")),
  user=os.getenv("user"),
  write_timeout=timeout,
)
  
try:
  cursor = connection.cursor()
  cursor.execute("DROP TABLE mytest")
  cursor.execute("CREATE TABLE mytest (id INTEGER PRIMARY KEY)")
  cursor.execute("INSERT INTO mytest (id) VALUES (1), (2)")
  cursor.execute("SELECT * FROM mytest")
  print(cursor.fetchall())
finally:
  connection.close()