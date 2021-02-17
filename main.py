from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (

    InvalidSignatureError

)
from linebot.models import (

    MessageEvent, TextMessage, TextSendMessage,

)
import os
import psycopg2
from psycopg2.extras import DictCursor


app = Flask(__name__)
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# connection確立時に読みこむ
@app.route('/')
# DB接続
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# tableにクエリを投げる
def get_response_message(mes_from):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM poke_stat WHERE name='{}'".format(mes_from))
            rows = cur.fetchall()
            return rows

# リクエストの処理
@app.route("/callback", methods=['POST'])
def callback():
    #リクエストヘッダーから署名検証
    signature = request.headers['X-Line-Signature']
    #リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# ユーザーへの応答
@handler.add(MessageEvent, message=TextMessage)

# メッセージイベント
def handle_message(event):
    rows = get_response_message(event.message.text)

    # webhook検証対策
    if event.reply_token == "00000000000000000000000000000000":
        return
    # テキストチェック
    if len(rows) == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="そのようなポケモンは存在しません")
    )
    else:
        r = rows[0]
        reply_message = f'{r[1]}\n\n'\
                        f'全国図鑑No.{r[0]}\n'\
                        f'タイプ1 {r[2]}\n'\
                        f'タイプ2 {r[3] if r[3] else "なし"}\n'\
                        f'とくせい1 {r[4]}\n'\
                        f'とくせい2 {r[5] if r[5] else "なし"}\n'\
                        f'隠れとくせい {r[6] if r[6] else "なし"}\n'\
                        f'HP {r[7]}\n'\
                        f'こうげき {r[8]}\n'\
                        f'ぼうぎょ {r[9]}\n'\
                        f'とくこう {r[10]}\n'\
                        f'とくぼう {r[11]}\n'\
                        f'すばやさ {r[12]}\n'\
                        f'種族値合計 {r[13]}\n'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

if __name__ == "__main__":

    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
