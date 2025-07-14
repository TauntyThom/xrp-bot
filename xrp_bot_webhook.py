from flask import Flask, request
import os
from binance.client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Connect to Binance client
client = Client(API_KEY, API_SECRET)
app = Flask(__name__)

# Minimum notional threshold for XRPUSDT on Binance (e.g. $10)
MIN_NOTIONAL = 11.0

# Calculate how much XRP to buy with ~10% of USDT balance
def calculate_quantity(symbol="XRPUSDT", allocation_pct=0.10):
    try:
        balance = client.get_asset_balance(asset='USDT')
        usdt = float(balance['free'])
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        quantity = round((usdt * allocation_pct) / price, 1)
        notional = quantity * price
        return quantity if notional >= MIN_NOTIONAL else 0
    except:
        return 0

# Get 99% of available XRP balance to avoid order failure
def get_xrp_balance():
    try:
        balance = client.get_asset_balance(asset='XRP')
        xrp = float(balance['free']) * 0.99
        price = float(client.get_symbol_ticker(symbol='XRPUSDT')['price'])
        notional = xrp * price
        return round(xrp, 1) if notional >= MIN_NOTIONAL else 0
    except:
        return 0

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = (data.get("signal") or "").upper()

    if signal == "BUY":
        quantity = calculate_quantity()
        if quantity > 0:
            try:
                client.create_order(
                    symbol="XRPUSDT",
                    side="BUY",
                    type="MARKET",
                    quantity=quantity
                )
            except:
                pass

    elif signal == "SELL":
        quantity = get_xrp_balance()
        if quantity > 0:
            try:
                client.create_order(
                    symbol="XRPUSDT",
                    side="SELL",
                    type="MARKET",
                    quantity=quantity
                )
            except:
                pass

    return "OK"
