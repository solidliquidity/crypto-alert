import asyncio
import websockets
import json
import pandas as pd
import time
import ccxt
import time

# Connect to Binance API
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret'
})

async def stream_prices(ws_url, live_prices):
    async with websockets.connect(ws_url) as ws:
        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)
                
                # Extract relevant data
                symbol = data['s']  # Symbol
                price = float(data['c'])  # Last price
                
                # Update dictionary
                live_prices[symbol] = price

                # Convert to DataFrame for easy viewing
                df = pd.DataFrame(live_prices.items(), columns=["Pair", "Price"])
                df.sort_values(by="Pair", inplace=True)

                # Print the updated table
                print("\033c", end="")  # Clear terminal output
                print(df)

            except Exception as e:
                print(f"Error: {e}")
                break

def price_alert(symbol, target_price):
    """Alert when a crypto price reaches a target."""
    while True:
        price = exchange.fetch_ticker(symbol)['last']
        print(f"Current {symbol} price: ${price:.2f}")

        if price >= target_price:
            print(f"🚀 ALERT! {symbol} hit ${target_price}")
            break

        time.sleep(10)  # Check every 10 seconds

