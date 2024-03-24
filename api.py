# ------------------------------------------------------------------------------#

import mysql.connector
from flask import Flask, request, render_template
import openai
import os

import base64

app = Flask(__name__)

# app.config['mysql+pymysql://root:@localhost/tray_data'] = os.environ['mysql://b6ebe5836a9814:9c68da67@us-cluster-east-01.k8s.cleardb.net/heroku_5d81e4bbe09030e?reconnect=true']

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_question = request.form.get('question', '')

        # マークダウンファイルから商品情報を読み込む
        with open('product_info.md', 'r', encoding='utf-8') as file:
            product_info_md = file.read()

        # 商品情報をユーザーの質問の前に追加
        full_prompt = f"{product_info_md}\n\n{user_question}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "これはChatGPTとの対話です。"},
                    {"role": "user", "content": full_prompt}
                ]
            )
            answer = response.choices[0].message['content'].strip() if response.choices else "回答を取得できませんでした。"
        except Exception as e:
            answer = f"エラーが発生しました: {str(e)}"
        return render_template('answer.html', question=user_question, answer=answer)
    return render_template('index.html')


# ---------------------------------------------------------------------------------------------------------------------------------------#
# SQLからの読み込み
# def get_db_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",  
#         database="tray_data"
#     )
#     return conn
def get_db_connection():
    conn = mysql.connector.connect(
        host="us-cluster-east-01.k8s.cleardb.net",
        user="b6ebe5836a9814",
        password="9c68da67",  
        database="heroku_5d81e4bbe09030e"
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

@app.route('/sql_data')
def sql_data():
    # Correct function call
    product_info_with_images = get_product_info_with_image()
    # Pass the correct variable to the template
    return render_template('sql_data.html', product_info=product_info_with_images)


if __name__ == '__main__':
    app.run(debug=True)

# ---------------------------------------------------------------------------------------------------------------------------------------#

# ------------------------------------------------------------------------------#
# 下記マークダウンからの抽出

# import mysql.connector
# from flask import Flask, request, render_template
# import openai
# import os

# import base64

# app = Flask(__name__)

# openai.api_key = os.getenv("OPENAI_API_KEY")

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         user_question = request.form.get('question', '')

#         # マークダウンファイルから商品情報を読み込む
#         with open('product_info.md', 'r', encoding='utf-8') as file:
#             product_info_md = file.read()

#         # 商品情報をユーザーの質問の前に追加
#         full_prompt = f"{product_info_md}\n\n{user_question}"

#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "これはChatGPTとの対話です。"},
#                     {"role": "user", "content": full_prompt}
#                 ]
#             )
#             answer = response.choices[0].message['content'].strip() if response.choices else "回答を取得できませんでした。"
#         except Exception as e:
#             answer = f"エラーが発生しました: {str(e)}"
#         return render_template('answer.html', question=user_question, answer=answer)
#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run(debug=True)
# ---------------------------------------------------------------------------------------------------------------------------------------#