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
  cursor.execute("USE defaultdb")
  cursor.execute("SELECT * FROM BancoX")
  print(cursor.fetchall())
finally:
  connection.close()