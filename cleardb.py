import mysql.connector
from urllib.parse import urlparse
import os

# 画像ファイルをバイナリデータに変換する関数
def convert_image_to_binary(image_path):
    with open(image_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

# Heroku の環境変数からデータベース接続情報を取得
url = urlparse(os.getenv('CLEARDB_DATABASE_URL'))
conn = mysql.connector.connect(
    host=url.hostname,
    user=url.username,  # 修正: 'username' から 'user' へ
    password=url.password,
    database=url.path[1:]  # 先頭の '/' を除去
)

# カーソルを取得
cursor = conn.cursor()

# テーブル作成のクエリを実行
create_table_query = """
CREATE TABLE IF NOT EXISTS tray_product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product VARCHAR(128) NOT NULL,
    category VARCHAR(128) NOT NULL,
    maker VARCHAR(128) NOT NULL,
    size VARCHAR(128) NOT NULL,
    features VARCHAR(255) NOT NULL,
    image BLOB    
)
"""
cursor.execute(create_table_query)  # この行を追加

# 変更をコミット
conn.commit()  # テーブル作成は変更を伴うため、コミットが必要

# 接続を閉じる
cursor.close()
conn.close()
