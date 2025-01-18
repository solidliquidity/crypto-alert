import ccxt
import time

# Initialize exchange
exchange = ccxt.binance()
futures_exchange = ccxt.binance({'options': {'defaultType': 'future'}})

# Define trading thresholds
BASIS_ENTRY_THRESHOLD = 0.8  # Enter if basis > 0.8%
BASIS_EXIT_THRESHOLD = 0.1   # Exit if basis < 0.1%
FUNDING_THRESHOLD = 0.01     # 0.01% funding rate per 8 hours

# Store active trade state
active_trade = False

def get_btc_basis():
    """Fetch BTC spot and futures price, calculate basis."""
    spot_price = exchange.fetch_ticker('BTC/USDT')['last']
    futures_price = futures_exchange.fetch_ticker('BTC/USDT')['last']
    basis = (futures_price - spot_price) / spot_price * 100
    return spot_price, futures_price, basis

def get_funding_rate():
    """Fetch BTC perpetual funding rate."""
    funding = futures_exchange.fetch_funding_rate('BTC/USDT')
    return funding['fundingRate'] * 100  # Convert to percentage

def place_market_order(symbol, side, amount, is_futures=False):
    """Executes market order."""
    market = futures_exchange if is_futures else exchange
    try:
        order = market.create_market_order(symbol, side, amount)
        print(f"✅ Order executed: {side.upper()} {amount} {symbol}")
        return order
    except Exception as e:
        print(f"❌ Order failed: {e}")
        return None

def trade_basis():
    """Main trading function."""
    global active_trade

    spot, futures, basis = get_btc_basis()
    funding_rate = get_funding_rate()
    
    print(f"Spot: ${spot}, Futures: ${futures}, Basis: {basis:.2f}%, Funding: {funding_rate:.4f}%")
    
    # ENTRY: If basis is high & funding is positive
    if basis > BASIS_ENTRY_THRESHOLD and funding_rate > FUNDING_THRESHOLD and not active_trade:
        print("🔹 Entering basis trade: Short perps, Buy spot BTC")
        place_market_order('BTC/USDT', 'buy', 0.01)  # Buy spot BTC
        place_market_order('BTC/USDT', 'sell', 0.01, is_futures=True)  # Short perps
        active_trade = True
    
    # EXIT: If basis collapses
    elif basis < BASIS_EXIT_THRESHOLD and active_trade:
        print("✅ Exiting basis trade: Closing spot and futures positions")
        place_market_order('BTC/USDT', 'sell', 0.01)  # Sell spot BTC
        place_market_order('BTC/USDT', 'buy', 0.01, is_futures=True)  # Close short perps
        active_trade = False

# Run every 10 seconds
while True:
    trade_basis()
    time.sleep(10)
