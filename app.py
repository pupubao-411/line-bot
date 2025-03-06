from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境變數（這些值會從 Render 設定，不要直接寫在程式碼中）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 記錄群組內「笑死」的次數
laugh_counter = {}

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot is running on Render."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text  
    group_id = event.source.group_id if hasattr(event.source, 'group_id') else event.source.user_id

    if group_id not in laugh_counter:
        laugh_counter[group_id] = 0

    if "笑死" in user_message:
        laugh_counter[group_id] += 1

    if user_message == "笑死次數":
        reply_message = f"這個群組已經說了 {laugh_counter[group_id]} 次『笑死』！"
    else:
        reply_message = f"你說了: {user_message}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
