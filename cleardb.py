import mysql.connector
from urllib.parse import urlparse
import os

# Heroku の環境変数からデータベース接続情報を取得
url = urlparse(os.getenv('CLEARDB_DATABASE_URL'))

# 接続情報を文字列にキャスト
host = str(url.hostname)
user = str(url.username)
password = str(url.password)
database = str(url.path[1:])  # 先頭の '/' を取り除く

try:
    # データベース接続を試みる
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    print("Successfully connected to the database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if conn.is_connected():
        conn.close()
        print("MySQL connection is closed")

