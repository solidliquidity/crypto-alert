import asyncio
import websockets
import json

# Binance WebSocket URLs
SPOT_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
FUTURES_URL = "wss://fstream.binance.com/ws/btcusdt@trade"

async def stream_binance():
    """Stream BTC Spot & Futures Prices"""
    async with websockets.connect(SPOT_URL) as spot_ws, websockets.connect(FUTURES_URL) as futures_ws:
        while True:
            spot_data = await spot_ws.recv()
            futures_data = await futures_ws.recv()

            spot_price = json.loads(spot_data)['p']
            futures_price = json.loads(futures_data)['p']

            basis = (float(futures_price) - float(spot_price)) / float(spot_price) * 100

            print(f"📊 BTC Spot: ${spot_price} | BTC Perp: ${futures_price} | Basis: {basis:.2f}%")

            await asyncio.sleep(0.1)  # Adjust delay for lower CPU usage

asyncio.run(stream_binance())
