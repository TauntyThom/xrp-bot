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

# Use 99% of USDT balance to buy XRP
def calculate_quantity(symbol="XRPUSDT", allocation_pct=0.99):
    try:
        balance = client.get_asset_balance(asset='USDT')
        usdt = float(balance['free']) * allocation_pct
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])

        # Binance minimum notional is ~$10, and quantities must have 1 decimal for XRP
        quantity = round(usdt / price, 1)

        # Avoid quantity too low to be accepted
        return quantity if quantity * price >= 10 else 0
    except Exception as e:
        print("Error calculating quantity:", e)
        return 0

# Sell 99% of available XRP
def get_xrp_balance():
    try:
        balance = client.get_asset_balance(asset='XRP')
        xrp = float(balance['free']) * 0.99
        return round(xrp, 1)
    except Exception as e:
        print("Error fetching XRP balance:", e)
        return 0

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = data.get("signal")
    print("Received signal:", signal)

    if signal and signal.upper() == "BUY":
        print("🟢 Processing BUY")
        quantity = calculate_quantity()
        print("Calculated quantity:", quantity)

        if quantity > 0:
            try:
                order = client.create_order(
                    symbol="XRPUSDT",
                    side="BUY",
                    type="MARKET",
                    quantity=quantity
                )
                print("✅ Buy order placed:", order)
            except Exception as e:
                print("❌ Buy order error:", str(e))
        else:
            print("⚠️ Quantity was zero — no order placed")

    elif signal and signal.upper() == "SELL":
        print("🔴 Processing SELL")
        quantity = get_xrp_balance()
        print("Sell quantity:", quantity)

        if quantity > 0:
            try:
                order = client.create_order(
                    symbol="XRPUSDT",
                    side="SELL",
                    type="MARKET",
                    quantity=quantity
                )
                print("✅ Sell order placed:", order)
            except Exception as e:
                print("❌ Sell order error:", str(e))
        else:
            print("⚠️ Sell quantity was zero — no order placed")

    return "OK"
