import mysql.connector
from flask import Flask, request, render_template
import openai
import os
from urllib.parse import urlparse
import re

import base64

app = Flask(__name__)



openai.api_key = os.getenv("OPENAI_API_KEY")

def get_db_connection():
    # 環境変数からデータベースのURLを取得し、解析
    url = urlparse(os.environ['DATABASE_URL'])

    # 接続情報を用いてMySQLデータベースに接続
    conn = mysql.connector.connect(
        host=url.hostname,  # ホスト名
        user=url.username,  # ユーザー名
        password=url.password,  # パスワード
        database=url.path[1:],  # データベース名 (先頭の '/' を取り除く)
    )
    return conn

def get_product_info_with_image():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product, category, maker, size, features, image FROM tray_product")
    product_info_with_images = []
    for (product, category, maker, size, features, image) in cursor.fetchall():
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        product_info_with_images.append((product, category, maker, size, features, image_base64))
    cursor.close()
    conn.close()
    return product_info_with_images

def get_product_info_by_ids(ids):
    conn = get_db_connection()
    cursor = conn.cursor()
    # SQLクエリにおいて、WHERE句で複数のIDを指定するために、%sをIDの数だけ繰り返します
    query = "SELECT product, category, maker, size, features, image FROM tray_product WHERE id IN ({})".format(', '.join(['%s'] * len(ids)))
    cursor.execute(query, ids)
    products_info = []
    for (product, category, maker, size, features, image) in cursor.fetchall():
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        products_info.append((product, category, maker, size, features, image_base64))
    cursor.close()
    conn.close()
    return products_info


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_question = request.form.get('question', '')

        # マークダウンファイルから商品情報を読み込む
        with open('product_info.md', 'r', encoding='utf-8') as file:
            product_info_md = file.read()

        # 商品情報をユーザーの質問の前に追加
        full_prompt = f"{product_info_md}\n\n{user_question}"
        
        # プロンプト設定
        try:
            response_format_instruction  = "以下の情報を基に、該当するすべての商品名とIDを教えてください。またおすすめの理由も教えてください: 商品ID：[ID] 商品名：[商品名]"
            full_prompt = f"{product_info_md}\n\n{response_format_instruction}\n\n{user_question}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは食品容器の営業マンです"},
                    {"role": "system", "content": "以下の形式で該当するすべての商品名とIDを教えてください: 「商品ID：[ID] 商品名：[商品名]」"},
                    {"role": "system", "content": "おすすめの理由も教えてください"},
                    {"role": "user", "content": full_prompt}
                ]
            )
            answer = response.choices[0].message['content'].strip() if response.choices else "回答を取得できませんでした。"
             # 正規表現を使用してIDを抽出
            ids = re.findall(r'商品ID：(\d+)', answer)
            
             # ここでデータベースから製品情報を取得
            if ids:
                product_info = get_product_info_by_ids(ids)
            else:
                product_info = []
        except Exception as e:
            answer = f"エラーが発生しました: {str(e)}"
            ids = []  # エラーが発生した場合は空リストを用意
            product_info = []

            
        return render_template('answer.html', question=user_question, answer=answer, ids=ids, product_info=product_info)
    return render_template('index.html')





@app.route('/sql_data')
def sql_data():
    # Correct function call
    product_info_with_images = get_product_info_with_image()
    # Pass the correct variable to the template
    return render_template('sql_data.html', product_info=product_info_with_images)


if __name__ == '__main__':
    app.run(debug=True)

# ---------------------------------------------------------------------------------------------------------------------------------------#


# import mysql.connector
# from flask import Flask, request, render_template,redirect
# import openai
# import os
# from urllib.parse import urlparse
# import re

# import base64

# from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user
# from werkzeug.security import generate_password_hash,check_password_hash

# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# login_manager = LoginManager()
# login_manager.init_app(app)

# class User(UserMixin):
#     def __init__(self,userid):
#         self.id = userid

# # ログイン実装
# @login_manager.user_loader
# def load_user(userid):
#     return User(userid)

# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect('/login')

# @app.route("/logout",methods=['GET'])
# def logout():
#     logout_user()
#     return redirect('/login')

# @app.route("/signup", methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         userid = request.form.get('userid')
#         password = request.form.get('password')
#         # pass_hash = generate_password_hash(password, method='sha256')
#         pass_hash = generate_password_hash(password, method='pbkdf2:sha256')

        
#         # データベース接続の取得 (関数名が間違っている可能性があるため修正)
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO user(username, password) VALUES (%s, %s)",  # パラメータのプレースホルダーを?から%sに変更（MySQL用）
#             (userid, pass_hash)
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return redirect('/login')
#     return render_template('signup.html')  # GETリクエスト用のレンダリングを追加


# @app.route("/login",methods=['GET','POST'])
# def login():
#     error_message = ''
#     userid = ''
    
#     if request.method == 'POST':
#         userid = request.form.get('userid')
#         password = request.form.get('password')
#         #ログインチェック
#         if(userid == 'test01' and password == 'password'):
#             user = User(userid)
#             login_user(user)
#             return redirect('/')
#         else:
#             error_message ='入力されたIDもしくはパスワードが誤ってます'
        
#     return render_template('login.html',userid=userid,error_message=error_message)
    


# openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_db_connection():
#     # 環境変数からデータベースのURLを取得し、解析
#     url = urlparse(os.environ['DATABASE_URL'])

#     # 接続情報を用いてMySQLデータベースに接続
#     conn = mysql.connector.connect(
#         host=url.hostname,  # ホスト名
#         user=url.username,  # ユーザー名
#         password=url.password,  # パスワード
#         database=url.path[1:],  # データベース名 (先頭の '/' を取り除く)
#     )
#     return conn

# def get_product_info_with_image():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT product, category, maker, size, features, image FROM tray_product")
#     product_info_with_images = []
#     for (product, category, maker, size, features, image) in cursor.fetchall():
#         image_base64 = base64.b64encode(image).decode('utf-8') if image else None
#         product_info_with_images.append((product, category, maker, size, features, image_base64))
#     cursor.close()
#     conn.close()
#     return product_info_with_images

# def get_product_info_by_ids(ids):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     # SQLクエリにおいて、WHERE句で複数のIDを指定するために、%sをIDの数だけ繰り返します
#     query = "SELECT product, category, maker, size, features, image FROM tray_product WHERE id IN ({})".format(', '.join(['%s'] * len(ids)))
#     cursor.execute(query, ids)
#     products_info = []
#     for (product, category, maker, size, features, image) in cursor.fetchall():
#         image_base64 = base64.b64encode(image).decode('utf-8') if image else None
#         products_info.append((product, category, maker, size, features, image_base64))
#     cursor.close()
#     conn.close()
#     return products_info


# @app.route('/', methods=['GET', 'POST'])
# @login_required
# def home():
#     if request.method == 'POST':
#         user_question = request.form.get('question', '')

#         # マークダウンファイルから商品情報を読み込む
#         with open('product_info.md', 'r', encoding='utf-8') as file:
#             product_info_md = file.read()

#         # 商品情報をユーザーの質問の前に追加
#         full_prompt = f"{product_info_md}\n\n{user_question}"
        
#         # プロンプト設定
#         try:
#             response_format_instruction  = "以下の情報を基に、該当するすべての商品名とIDを教えてください。またおすすめの理由も教えてください: 商品ID：[ID] 商品名：[商品名]"
#             full_prompt = f"{product_info_md}\n\n{response_format_instruction}\n\n{user_question}"
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "あなたは食品容器の営業マンです"},
#                     {"role": "system", "content": "以下の形式で該当するすべての商品名とIDを教えてください: 「商品ID：[ID] 商品名：[商品名]」"},
#                     {"role": "system", "content": "おすすめの理由も教えてください"},
#                     {"role": "user", "content": full_prompt}
#                 ]
#             )
#             answer = response.choices[0].message['content'].strip() if response.choices else "回答を取得できませんでした。"
#              # 正規表現を使用してIDを抽出
#             ids = re.findall(r'商品ID：(\d+)', answer)
            
#              # ここでデータベースから製品情報を取得
#             if ids:
#                 product_info = get_product_info_by_ids(ids)
#             else:
#                 product_info = []
#         except Exception as e:
#             answer = f"エラーが発生しました: {str(e)}"
#             ids = []  # エラーが発生した場合は空リストを用意
#             product_info = []

            
#         return render_template('answer.html', question=user_question, answer=answer, ids=ids, product_info=product_info)
#     return render_template('index.html')





# @app.route('/sql_data')
# @login_required
# def sql_data():
#     # Correct function call
#     product_info_with_images = get_product_info_with_image()
#     # Pass the correct variable to the template
#     return render_template('sql_data.html', product_info=product_info_with_images)


# if __name__ == '__main__':
#     app.run(debug=True)