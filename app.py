from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import threading
import time
import requests

app = Flask(__name__)

# === 替換為你自己的 LINE 憑證 ===
LINE_CHANNEL_ACCESS_TOKEN = "mc9Lu69WuEF2c36LwiDAJ5IgXInG99mcMAUrrIMp2XhduFqN1s1rTuzDNHWcKlkHXuuRB80llaVUCNrxr8mqHS/SEOXbIcLIW3egn8UFRTH+FSCtjibf+3arFZvvgh/74qcPP3sx31fgFxu7rofMZAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "0eefb4a8ff80e2eb09ee39adc5f93b4b"
LINE_USER_ID = "U5de10eb0ddd73b88f37037d0ab03f42b"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === 股票參數設定 ===
stock_symbol = "2881.TW"
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
    user_text = event.message.text
    if user_text.lower() == "股價":
        try:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock_symbol}"
            response = requests.get(url)
            price = response.json()["quoteResponse"]["result"][0]["regularMarketPrice"]
            reply = f"📈 {stock_symbol} 現價：{price} 元"
        except Exception as e:
            reply = f"讀取股價失敗：{e}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"你說的是：{user_text}")
        )

# === 背景執行：定時檢查股價並推播 ===
def stock_price_broadcast():
    while True:
        try:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock_symbol}"
            response = requests.get(url)
            result = response.json()["quoteResponse"]["result"]
            if not result:
                print(f"查無股票 {stock_symbol}")
                time.sleep(60)
                continue

            price = result[0]["regularMarketPrice"]
            print(f"{stock_symbol} 現價：{price}")

            if price >= take_profit and not already_notified["take_profit"]:
                alert = f"🎯 {stock_symbol} 已達停利價：{price} 元（目標 {take_profit}）"
                line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=alert))
                already_notified["take_profit"] = True

            elif price <= stop_loss and not already_notified["stop_loss"]:
                alert = f"⚠️ {stock_symbol} 已跌破停損價：{price} 元（目標 {stop_loss}）"
                line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=alert))
                already_notified["stop_loss"] = True

        except Exception as e:
            print(f"推播錯誤: {e}")

        time.sleep(60)  # 每 60 秒檢查一次

if __name__ == "__main__":
    # 啟動背景執行緒
    threading.Thread(target=stock_price_broadcast, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
