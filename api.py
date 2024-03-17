import mysql.connector
from flask import Flask, request, render_template
import openai
import os

import base64

app = Flask(__name__)

# データベース接続設定
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="tray_data"
    )
    return conn

def get_product_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maker, category, product, purpose FROM tray_product")
    product_info = cursor.fetchall()
    cursor.close()
    conn.close()
    return product_info
def get_product_info_with_image():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maker, category, product, purpose, image FROM tray_product")
    product_info_with_images = []
    for maker, category, product, purpose, image in cursor.fetchall():
        if image:
            image_base64 = base64.b64encode(image).decode('utf-8')
        else:
            image_base64 = None
        product_info_with_images.append((maker, category, product, purpose, image_base64))
    cursor.close()
    conn.close()
    return product_info_with_images

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_question = request.form.get('question', '')

        # データベースから画像を含む商品情報を取得
        product_info_with_images = get_product_info_with_image()

        # データベースから取得した商品情報をマークダウン形式で整形（画像は除外）
        product_info_md = '\n'.join([f"- メーカー: {maker}, ジャンル: {category}, 商品: {product}, 用途: {purpose}" for maker, category, product, purpose, _ in product_info_with_images])

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

        # answer.html テンプレートをレンダリングして、画像を含む商品情報、ユーザーの質問、ChatGPTからの回答を渡す
        return render_template('answer.html', product_info_with_images=product_info_with_images, question=user_question, answer=answer)
    
    # GETリクエストの場合、またはPOSTリクエストでない場合は通常のindex.htmlを表示
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
