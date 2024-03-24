import mysql.connector
from PIL import Image
import io


# 画像ファイルをバイナリデータに変換する関数
# def convert_image_to_binary(image_path):
#     with open(image_path, 'rb') as file:
#         binary_data = file.read()
#     return binary_data

# MySQLに接続
conn = mysql.connector.connect(
    host="us-cluster-east-01.k8s.cleardb.net",
    user="b6ebe5836a9814",
    password="9c68da67",
    database="heroku_5d81e4bbe09030e"
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
# def insert_image_data(product, category, maker, size, features, image_path):
#     binary_data = convert_image_to_binary(image_path)
#     insert_query = """
#     INSERT INTO tray_product (product, category, maker, size, features, image)
#     VALUES (%s, %s, %s, %s, %s, %s)
#     """
#     cursor.execute(insert_query, (product, category, maker, size, features, binary_data))
#     conn.commit()

# # 画像データを含むデータを挿入
# image_path = r'c:\Users\akhr0\OneDrive\デスクトップ\トレー写真\MFPかぐら丼17-17.jpg' 
# # 挿入するデータをセットアップ
# tray_data = ("MFPかぐら丼17-17", "丼", "エフピコ", "170×170×44", "丼ぶり ごはん160g 四角", image_path)

# # データ挿入関数を呼び出し
# insert_image_data(*tray_data)

# 接続を閉じる
cursor.close()
conn.close()