from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import threading
import time
import twstock

app = Flask(__name__)

# === LINE 憑證 ===
LINE_CHANNEL_ACCESS_TOKEN = "mc9Lu69WuEF2c36LwiDAJ5IgXInG99mcMAUrrIMp2XhduFqN1s1rTuzDNHWcKlkHXuuRB80llaVUCNrxr8mqHS/SEOXbIcLIW3egn8UFRTH+FSCtjibf+3arFZvvgh/74qcPP3sx31fgFxu7rofMZAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "0eefb4a8ff80e2eb09ee39adc5f93b4b"
LINE_USER_ID = "U5de10eb0ddd73b88f37037d0ab03f42b"  # 用於推播

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === 股票設定 ===
stock_symbol = "2881"
buy_price = 85.17
take_profit = 93.3
stop_loss = 79.8
already_notified = {"take_profit": False, "stop_loss": False}

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
    user_text = event.message.text.strip()
    print(f"收到訊息：{user_text}")

    if user_text.lower() == "id":
        reply = f"你的 LINE User ID 是：{event.source.user_id}"
    elif user_text.isdigit():
        stock = twstock.realtime.get(user_text)
        if stock["success"]:
            name = stock["info"]["name"]
            price = stock["realtime"]["latest_trade_price"]
            reply = f"📈 {name}（{user_text}）現價：{price} 元"
        else:
            reply = f"查無此股票代碼：{user_text}"
    else:
        reply = f"你說的是：{user_text}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# === 背景執行：定時推播 ===
def stock_price_broadcast():
    global already_notified

    while True:
        try:
            stock = twstock.realtime.get(stock_symbol)
            if stock["success"]:
                price = float(stock["realtime"]["latest_trade_price"])
                print(f"{stock_symbol} 現價：{price}")

                if price >= take_profit and not already_notified["take_profit"]:
                    alert = f"🎯 {stock_symbol} 已達停利價：{price} 元（目標 {take_profit}）"
                    line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=alert))
                    already_notified["take_profit"] = True

                elif price <= stop_loss and not already_notified["stop_loss"]:
                    alert = f"⚠️ {stock_symbol} 已跌破停損價：{price} 元（目標 {stop_loss}）"
                    line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=alert))
                    already_notified["stop_loss"] = True

            else:
                print("讀取失敗")

        except Exception as e:
            print(f"推播錯誤：{e}")

        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=stock_price_broadcast, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
