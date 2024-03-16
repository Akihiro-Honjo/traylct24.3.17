from flask import Flask, request, render_template
import openai
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
