from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (

    InvalidSignatureError

)
from linebot.models import (

    MessageEvent, TextMessage, TextSendMessage, CarouselTemplate, CarouselColumn

)
import os
import psycopg2
from psycopg2.extras import DictCursor


app = Flask(__name__)
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
DATABASE_URL = os.environ.get('DATABASE_URL')

# connection確立時に読みこむ
@app.route('/')
# DB接続
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# ポケモン名の問い合わせを行い、完全一致・部分一致する
def get_response_name(mes_from):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT name FROM poke_stat \
                WHERE name = '{0}' or name LIKE '{0}%' or name LIKE 'メガ{0}%'".format(mes_from))
            rows = cur.fetchall()
            return rows

# 対象となるポケモンの行を返す。
def get_response_message(mes_from):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM poke_stat WHERE name = '{}'".format(mes_from))
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

    # 入力された名前に完全一致・部分一致するname要素を取得する。
    name_rows = get_response_name(event.message.text)
    # webhook検証対策
    if event.reply_token == "00000000000000000000000000000000":
        return
    # テキストチェック
    if len(name_rows) == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="そのようなポケモンは存在しません")
    )
    else:
    # 取得したname要素の行を取得し、返す。
        for i in range(len(name_rows)):
            val_rows = get_response_message(name_rows[i])
            r = val_rows[0]
            url_no = ('{0:04d}'.format(r[0]))
            reply_message = f'{r[1]}\n\n'\
                            f'全国図鑑No.{r[0]}\n'\
                            f'タイプ1 {r[2]}\n'\
                            f'タイプ2 {r[3] if r[3] else "なし"}\n'\
                            f'特性1 {r[4]}\n'\
                            f'特性2 {r[5] if r[5] else "なし"}\n'\
                            f'隠れ特性 {r[6] if r[6] else "なし"}\n'\
                            f'H  {r[7]}\n'\
                            f'A  {r[8]}\n'\
                            f'B  {r[9]}\n'\
                            f'C  {r[10]}\n'\
                            f'D  {r[11]}\n'\
                            f'S  {r[12]}\n'\
                            f'T  {r[13]}\n'\
                            f'https://swsh.pokedb.tokyo/pokemon/show/{url_no}-00?season=15&rule=0'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_message)
            )

if __name__ == "__main__":

    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
