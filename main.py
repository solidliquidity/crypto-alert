from portfolio import fetch_portfolio, rebalance_portfolio, convert_crypto
from stream import stream_prices, price_alert
import asyncio

target_allocation = {
    "BTC": 0.50,  # 50% BTC
    "ETH": 0.30,  # 30% ETH
    "BNB": 0.20   # 20% BNB
}

# List of trading pairs you want to track
symbols = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]  # Add more pairs if needed

# WebSocket URL for Binance's price stream
ws_url = f"wss://stream.binance.com:9443/ws/{'/'.join([s+'@ticker' for s in symbols])}"

# Store live prices in a dictionary
live_prices = {}

# Set alert for BTC at $50,000
price_alert("BTC/USDT", 50000)

# Run the WebSocket stream
asyncio.run(stream_prices())