import requests
import time
from collections import deque
import statistics

# =========================
# TOP 10 COINS (USDT)
# =========================
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "DOTUSDT",
    "MATICUSDT"
]

INTERVAL = "1h"
LIMIT = 50
SLEEP = 60

URL = "https://api.binance.com/api/v3/klines"

history = {s: deque(maxlen=LIMIT) for s in SYMBOLS}


# =========================
# DATA
# =========================
def get_data(symbol):
    try:
        r = requests.get(URL, params={
            "symbol": symbol,
            "interval": INTERVAL,
            "limit": LIMIT
        }, timeout=10)

        data = r.json()
        closes = [float(x[4]) for x in data]
        volumes = [float(x[5]) for x in data]
        return closes, volumes
    except:
        return None, None


# =========================
# INDICATORS
# =========================
def sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


def rsi(data, period=14):
    if len(data) < period + 1:
        return None

    gain, loss = 0, 0
    for i in range(-period, 0):
        diff = data[i] - data[i - 1]
        if diff > 0:
            gain += diff
        else:
            loss -= diff

    if loss == 0:
        return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def bollinger(data):
    if len(data) < 20:
        return None, None, None

    mid = sma(data, 20)
    std = statistics.stdev(data[-20:])
    return mid + 2*std, mid, mid - 2*std


# =========================
# SIGNAL ENGINE
# =========================
def signal_engine(prices):
    sma10 = sma(prices, 10)
    sma20 = sma(prices, 20)
    r = rsi(prices)
    upper, mid, lower = bollinger(prices)

    if not sma10 or not sma20:
        return "WAIT"

    signal = "HOLD"

    # trend
    if sma10 > sma20:
        signal = "BUY"
    elif sma10 < sma20:
        signal = "SELL"

    # filters
    if r:
        if r > 70:
            signal = "SELL (overbought)"
        elif r < 30:
            signal = "BUY (oversold)"

    # bollinger extremes
    if upper and prices[-1] > upper:
        signal = "SELL (bollinger)"

    if lower and prices[-1] < lower:
        signal = "BUY (bounce)"

    return signal


# =========================
# RUNNER
# =========================
def run():
    print("🚀 TOP 10 CRYPTO SCANNER STARTED\n")

    while True:
        print("=" * 80)

        for sym in SYMBOLS:
            prices, vol = get_data(sym)

            if not prices:
                print(sym, "error")
                continue

            history[sym] = deque(prices, maxlen=LIMIT)

            sig = signal_engine(list(history[sym]))

            print(f"{sym} | Price: {prices[-1]:.2f} | Signal: {sig}")

        print("=" * 80)
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
