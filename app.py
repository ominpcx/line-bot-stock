from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

# 請替換為你的 LINE Channel Access Token 和 Secret
LINE_CHANNEL_ACCESS_TOKEN = "mc9Lu69WuEF2c36LwiDAJ5IgXInG99mcMAUrrIMp2XhduFqN1s1rTuzDNHWcKlkHXuuRB80llaVUCNrxr8mqHS/SEOXbIcLIW3egn8UFRTH+FSCtjibf+3arFZvvgh/74qcPP3sx31fgFxu7rofMZAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "0eefb4a8ff80e2eb09ee39adc5f93b4b"

# 設定 Messaging API
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    print(f"收到訊息：{user_text}")
    print(f"用戶 ID：{user_id}")

    if user_text.lower() == "id":
        reply_text = f"你的 LINE User ID 是：{user_id}"
    else:
        reply_text = f"你說的是：{user_text}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
