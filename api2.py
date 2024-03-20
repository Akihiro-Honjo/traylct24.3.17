# MySQLからの抽出
# ------------------------------------------------------------------------------#

# import mysql.connector
# from flask import Flask, request, render_template
# import openai
# import os

# import base64



# app = Flask(__name__)

# # データベース接続設定
# def get_db_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",  
#         database="tray_data"
#     )
#     return conn

# # DBから商品情報取得
# def get_product_info_with_image():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT product, category, maker, size, features, image FROM tray_product")
#     product_info_with_images = []
#     for product, category, maker, size, features, image in cursor.fetchall():
#         if image:
#             image_base64 = base64.b64encode(image).decode('utf-8')
#         else:
#             image_base64 = None
#         product_info_with_images.append((product, category, maker, size, features, image_base64))
#     cursor.close()
#     conn.close()
#     return product_info_with_images

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         user_question = request.form.get('question', '')

#         # データベースから画像を含む商品情報を取得
#         product_info_with_images = get_product_info_with_image()

#         # データベースから取得した商品情報
#         product_info_md = '\n'.join([f"- 商品: {product}, ジャンル: {category}, メーカー: {maker}, サイズ:{size}, 特徴: {features}" for product, category, maker, size, features,_ in product_info_with_images])

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

#         # answer.html テンプレートをレンダリングして、画像を含む商品情報、ユーザーの質問、ChatGPTからの回答を渡す
#         return render_template('answer.html', product_info_with_images=product_info_with_images, question=user_question, answer=answer)
    
#     # GETリクエストの場合、またはPOSTリクエストでない場合は通常のindex.htmlを表示
#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run(debug=True)

# ------------------------------------------------------------------------------#
# 下記マークダウンからの抽出

# from flask import Flask, request, render_template
# import openai
# import os

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

import mysql.connector
from flask import Flask, request, render_template
import openai
import os
import base64

app = Flask(__name__)

# 環境変数からOpenAIのAPIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# データベース接続設定
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="tray_data"
    )
    return conn

# DBから商品情報取得
def get_product_info_with_image():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product, category, maker, size, features, image FROM tray_product")
    product_info_with_images = []
    for product, category, maker, size, features, image in cursor.fetchall():
        if image:
            image_base64 = base64.b64encode(image).decode('utf-8')
        else:
            image_base64 = None
        product_info_with_images.append((product, category, maker, size, features, image_base64))
    cursor.close()
    conn.close()
    return product_info_with_images

# マークダウンファイルから内容を読み込む
def get_markdown_content():
    with open('product_info.md', 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    return markdown_content

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_question = request.form.get('question', '')
        
        # データベースから画像を含む商品情報を取得
        product_info_with_images = get_product_info_with_image()
        
        # マークダウンファイルから内容を読み込む
        markdown_content = get_markdown_content()

        # 商品情報をテキストに変換し、マークダウン内容と組み合わせる
        product_info_text = '\n'.join([f"- 商品: {product}, ジャンル: {category}, メーカー: {maker}, サイズ:{size}, 特徴: {features}" for product, category, maker, size, features, _ in product_info_with_images])
        full_prompt = f"{markdown_content}\n{product_info_text}\n\n{user_question}"

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

        # answer.html テンプレートをレンダリングして、全情報とユーザーの質問、ChatGPTからの回答を渡す
        return render_template('answer.html', product_info_with_images=product_info_with_images, question=user_question, answer=answer)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


# import mysql.connector
# from flask import Flask, request, render_template
# import openai
# import os
# import base64

# app = Flask(__name__)

# # 環境変数からOpenAIのAPIキーを取得
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # データベース接続設定
# def get_db_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",  
#         database="tray_data"
#     )
#     return conn


# # DBから商品情報取得（IDも含む）
# def get_product_info_with_image():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id,product, category, maker, size, features, image FROM tray_product")  # IDを取得
#     product_info_with_images = []
#     for id, product, category, maker, size, features, image in cursor.fetchall():
#         if image:
#             image_base64 = base64.b64encode(image).decode('utf-8')
#         else:
#             image_base64 = None
#         product_info_with_images.append((id, product, category, maker, size, features, image_base64))  # IDを追加
#     cursor.close()
#     conn.close()
#     return product_info_with_images


# # マークダウンファイルから内容を読み込む
# def get_markdown_content():
#     with open('product_info.md', 'r', encoding='utf-8') as file:
#         markdown_content = file.read()
#     return markdown_content

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         user_question = request.form.get('question', '')
        
#         # データベースから画像を含む商品情報を取得
#         product_info_with_images = get_product_info_with_image()
        
#         # マークダウンファイルから内容を読み込む
#         markdown_content = get_markdown_content()

#         # 商品情報をテキストに変換し、マークダウン内容と組み合わせる
#         product_info_text = '\n'.join([f"- ID:{id}, 商品: {product}, ジャンル: {category}, メーカー: {maker}, サイズ:{size}, 特徴: {features}" for id, product, category, maker, size, features, _ in product_info_with_images])
#         full_prompt = f"{markdown_content}\n{product_info_text}\n\n{user_question}"

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

#         # answer.html テンプレートをレンダリングして、全情報とユーザーの質問、ChatGPTからの回答を渡す
#         return render_template('answer.html', product_info_with_images=product_info_with_images, question=user_question, answer=answer)
    
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)



# import mysql.connector
# from flask import Flask, request, render_template
# import openai
# import os
# import base64
# import spacy

# app = Flask(__name__)

# # spaCyの言語モデルをロード
# nlp = spacy.load("en_core_web_sm")




# # データベース接続設定
# def get_db_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",  
#         database="tray_data"
#     )
#     return conn


# # 質問からキーワードを抽出する関数
# def extract_keywords(question):
#     doc = nlp(question)
#     keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN", "ADJ"]]
#     return keywords

# # DBから商品情報取得（キーワードに基づく検索を追加）
# def get_product_info_with_image(keywords=None):
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     query = "SELECT product, category, maker, size, features, image FROM tray_product"
#     if keywords:
#         search_terms = ['%' + keyword + '%' for keyword in keywords]
#         query += " WHERE " + " OR ".join(["(product LIKE %s OR category LIKE %s OR maker LIKE %s OR features LIKE %s)"] * len(keywords))
#         cursor.execute(query, search_terms * 4)
#     else:
#         cursor.execute(query)
    
#     product_info_with_images = []
#     for product, category, maker, size, features, image in cursor.fetchall():
#         if image:
#             image_base64 = base64.b64encode(image).decode('utf-8')
#         else:
#             image_base64 = None
#         product_info_with_images.append((product, category, maker, size, features, image_base64))
#     cursor.close()
#     conn.close()
#     return product_info_with_images

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         user_question = request.form.get('question', '')
        
#         # ユーザーの質問からキーワードを抽出
#         keywords = extract_keywords(user_question)

#         # データベースから画像を含む商品情報を取得
#         product_info_with_images = get_product_info_with_image(keywords)

#         # データベースから取得した商品情報をマークダウン形式で整形
#         product_info_md = '\n'.join([f"- 商品: {product}, ジャンル: {category}, メーカー: {maker}, サイズ:{size}, 特徴: {features}" for product, category, maker, size, features, _ in product_info_with_images])

#         # 商品情報とユーザーの質問を組み合わせたフルプロンプトを作成
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

#         # answer.html テンプレートをレンダリングして、画像を含む商品情報、ユーザーの質問、ChatGPTからの回答を渡す
#         return render_template('answer.html', product_info_with_images=product_info_with_images, question=user_question, answer=answer)
    
#     # GETリクエストの場合、またはPOSTリクエストでない場合は通常のindex.htmlを表示
#     return render_template('index.html')



# if __name__ == '__main__':
#     app.run(debug=True)
