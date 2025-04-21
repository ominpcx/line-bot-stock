from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 請替換為你自己的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = "mc9Lu69WuEF2c36LwiDAJ5IgXInG99mcMAUrrIMp2XhduFqN1s1rTuzDNHWcKlkHXuuRB80llaVUCNrxr8mqHS/SEOXbIcLIW3egn8UFRTH+FSCtjibf+3arFZvvgh/74qcPP3sx31fgFxu7rofMZAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "0eefb4a8ff80e2eb09ee39adc5f93b4b"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply_text = f"你說的是：{user_text}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
