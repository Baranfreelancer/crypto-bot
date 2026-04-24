import requests
import time

# =========================
# 🔴 BURAYI DOLDUR
# =========================
BOT_TOKEN = "8765491306:AAEH7Ok3c7ijrB-vt9ZItR37Dqpj9kdadaI"
CHAT_ID = "8443986702"
# =========================

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "1h"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

SMA_SHORT = 10
SMA_LONG = 20


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def get_prices(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 50
    }
    r = requests.get(BINANCE_URL, params=params)
    data = r.json()
    return [float(x[4]) for x in data]


def sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


def signal(symbol):
    prices = get_prices(symbol)

    sma10 = sma(prices, SMA_SHORT)
    sma20 = sma(prices, SMA_LONG)

    price = prices[-1]

    if sma10 is None or sma20 is None:
        return

    if sma10 > sma20:
        sig = "🟢 BUY"
    elif sma10 < sma20:
        sig = "🔴 SELL"
    else:
        sig = "⚪ HOLD"

    text = f"""
📊 SIGNAL

Coin: {symbol}
Price: {price}
SMA10: {sma10:.2f}
SMA20: {sma20:.2f}
Signal: {sig}
"""

    print(text)
    send_telegram(text)


print("Bot başladı...")

send_telegram("🤖 Bot aktif! Sinyal sistemi çalışıyor.")

while True:
    for s in SYMBOLS:
        try:
            signal(s)
        except Exception as e:
            print("Hata:", e)

    time.sleep(60)
