import pymysql; import os


timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=db,
  host=host,
  password=password,
  read_timeout=timeout,
  port=port,
  user=user,
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