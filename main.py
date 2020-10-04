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
app = Flask(__name__)
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
@app.route("/callback", methods=['POST'])

def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:

        handler.handle(body, signature)

    except InvalidSignatureError:

        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)

# オウム返し用のメッセージイベント

def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    line_bot_api.reply_message(

        event.reply_token,

        TextSendMessage(text=event.message.text)

    )

if __name__ == "__main__":

    port = int(os.getenv("PORT"))

    app.run(host="0.0.0.0"  , port=port)
