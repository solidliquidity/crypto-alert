import ccxt
import pandas as pd

# Connect to Binance API
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_api_secret'
})

def fetch_portfolio():
    """Fetch live Binance portfolio balances."""
    balances = exchange.fetch_balance()
    
    # Filter non-empty balances
    assets = {k: v['free'] for k, v in balances['total'].items() if v['free'] > 0}

    # Fetch latest market prices
    prices = {symbol: exchange.fetch_ticker(symbol + "/USDT")['last'] for symbol in assets.keys() if symbol != 'USDT'}

    # Calculate USD value of each holding
    portfolio = {sym: {"Amount": assets[sym], 
                       "USD Value": assets[sym] * prices.get(sym, 1)} 
                 for sym in assets}

    return portfolio

def rebalance_portfolio(target_allocation):
    """Adjusts Binance portfolio to match target allocation."""
    portfolio = fetch_portfolio()
    total_value = sum(asset["USD Value"] for asset in portfolio.values())

    for asset, target_weight in target_allocation.items():
        if asset not in portfolio:
            print(f"Skipping {asset} (not in portfolio)")
            continue

        current_value = portfolio[asset]["USD Value"]
        target_value = total_value * target_weight
        diff = target_value - current_value

        if abs(diff) > 10:  # Ignore small differences
            symbol = asset + "/USDT"
            amount = abs(diff) / exchange.fetch_ticker(symbol)['last']
            
            if diff > 0:
                print(f"Buying {amount:.4f} {asset} (${diff:.2f})")
                exchange.create_market_buy_order(symbol, amount)
            else:
                print(f"Selling {amount:.4f} {asset} (${abs(diff):.2f})")
                exchange.create_market_sell_order(symbol, amount)

def convert_crypto(from_asset, to_asset, percentage):
    """Convert a percentage of one crypto into another."""
    balances = exchange.fetch_balance()
    from_balance = balances['free'].get(from_asset, 0)

    if from_balance > 0:
        amount_to_sell = from_balance * (percentage / 100)
        symbol = f"{from_asset}/USDT"
        price = exchange.fetch_ticker(symbol)['last']
        usdt_value = amount_to_sell * price

        # Buy the new asset
        new_symbol = f"{to_asset}/USDT"
        new_price = exchange.fetch_ticker(new_symbol)['last']
        amount_to_buy = usdt_value / new_price

        print(f"Converting {amount_to_sell:.4f} {from_asset} to {amount_to_buy:.4f} {to_asset}")
        exchange.create_market_sell_order(symbol, amount_to_sell)
        exchange.create_market_buy_order(new_symbol, amount_to_buy)

# Fetch and display portfolio
portfolio = fetch_portfolio()
df = pd.DataFrame.from_dict(portfolio, orient='index')
print("\n📊 Live Portfolio:")
print(df)
convert_crypto("ETH", "BTC", 50)
rebalance_portfolio()