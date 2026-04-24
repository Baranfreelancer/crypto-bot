"""
Simple Crypto Trading Signal Bot
Uses Binance public API to analyze BTC, ETH, and SOL
Generates buy/sell signals based on SMA10 and SMA20
"""

import requests
import time
from collections import deque

# Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
BINANCE_URL = "https://api.binance.com/api/v3/klines"
SMA_SHORT = 10  # Short-term moving average
SMA_LONG = 20   # Long-term moving average
SLEEP_SECONDS = 60

# Store historical prices for SMA calculation
price_history = {symbol: deque(maxlen=SMA_LONG) for symbol in SYMBOLS}
last_signal = {symbol: "NONE" for symbol in SYMBOLS}


def fetch_klines(symbol, interval="1h", limit=30):
    """
    Fetch candlestick data from Binance
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        interval: Kline interval (e.g., "1h" for 1 hour)
        limit: Number of klines to fetch
    
    Returns:
        List of closing prices or None if request fails
    """
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(BINANCE_URL, params=params, timeout=5)
        response.raise_for_status()
        
        klines = response.json()
        # Extract closing prices (index 4 in each kline)
        closing_prices = [float(kline[4]) for kline in klines]
        return closing_prices
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average
    
    Args:
        prices: List of prices
        period: Number of periods for SMA
    
    Returns:
        SMA value or None if not enough data
    """
    if len(prices) < period:
        return None
    
    return sum(prices[-period:]) / period


def generate_signal(symbol):
    """
    Generate trading signal based on SMA crossover
    
    Args:
        symbol: Trading pair
    
    Returns:
        Tuple of (signal, current_price, sma10, sma20)
    """
    # Fetch latest kline data
    klines = fetch_klines(symbol)
    
    if klines is None or len(klines) == 0:
        return "ERROR", None, None, None
    
    # Add latest closing price to history
    current_price = klines[-1]
    price_history[symbol].append(current_price)
    
    # Calculate SMAs
    sma10 = calculate_sma(list(price_history[symbol]), SMA_SHORT)
    sma20 = calculate_sma(list(price_history[symbol]), SMA_LONG)
    
    # Need enough data points before generating signals
    if sma10 is None or sma20 is None:
        return "WAIT", current_price, sma10, sma20
    
    # Generate signal based on SMA crossover
    signal = "HOLD"
    
    # BUY signal: SMA10 crosses above SMA20
    if sma10 > sma20 and last_signal[symbol] != "BUY":
        signal = "BUY"
    
    # SELL signal: SMA10 crosses below SMA20
    elif sma10 < sma20 and last_signal[symbol] != "SELL":
        signal = "SELL"
    
    # Update last signal
    last_signal[symbol] = signal
    
    return signal, current_price, sma10, sma20


def print_report(symbol, signal, price, sma10, sma20):
    """
    Print formatted trading report
    
    Args:
        symbol: Trading pair
        signal: Trading signal (BUY, SELL, HOLD, etc.)
        price: Current price
        sma10: Short-term moving average
        sma20: Long-term moving average
    """
    if signal == "ERROR":
        print(f"[{symbol}] ❌ Error fetching data")
        return
    
    if signal == "WAIT":
        print(f"[{symbol}] ⏳ Waiting for data... ({len(price_history[symbol])}/{SMA_LONG} candles)")
        return
    
    # Format signal with emoji
    signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
    
    print(f"[{symbol}] {signal_emoji} {signal:<6} | Price: ${price:>12,.2f} | SMA10: ${sma10:>12,.2f} | SMA20: ${sma20:>12,.2f}")


def main():
    """
    Main loop: continuously fetch data and generate signals
    """
    print("=" * 100)
    print("🤖 Crypto Trading Signal Bot Started")
    print(f"Monitoring: {', '.join(SYMBOLS)}")
    print(f"Strategy: SMA{SMA_SHORT} / SMA{SMA_LONG} Crossover")
    print(f"Update interval: Every {SLEEP_SECONDS} seconds")
    print("=" * 100)
    print()
    
    try:
        while True:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Fetching latest data...")
            print("-" * 100)
            
            # Analyze each symbol
            for symbol in SYMBOLS:
                signal, price, sma10, sma20 = generate_signal(symbol)
                print_report(symbol, signal, price, sma10, sma20)
            
            print("-" * 100)
            print(f"Next update in {SLEEP_SECONDS} seconds...\n")
            
            # Wait before next update
            time.sleep(SLEEP_SECONDS)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 100)
        print("⛔ Bot stopped by user")
        print("=" * 100)


if __name__ == "__main__":
    main()
