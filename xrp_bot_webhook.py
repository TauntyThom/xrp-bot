from flask import Flask, request
import os
from binance.client import Client
from dotenv import load_dotenv

# Load .env keys
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Connect to Binance LIVE
client = Client(API_KEY, API_SECRET)

app = Flask(__name__)

# Calculate how much XRP to buy with ~10% of USDT balance
def calculate_quantity(symbol="XRPUSDT", allocation_pct=0.10):
    try:
        balance = client.get_asset_balance(asset='USDT')
        usdt = float(balance['free'])
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        quantity = round((usdt * allocation_pct) / price, 1)
        return quantity
    except Exception as e:
        print("Error calculating quantity:", e)
        return 0

# Calculate how much XRP to sell (all available)
def calculate_sell_quantity(symbol="XRP"):
    try:
        balance = client.get_asset_balance(asset=symbol)
        xrp_qty = float(balance['free'])
        # Binance may require a buffer for fees or minimum notional amount
        return round(xrp_qty * 0.99, 1)  # Sell 99% to avoid errors
    except Exception as e:
        print("Error calculating sell quantity:", e)
        return 0

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = data.get("signal")
    print("Received signal:", signal, "for XRPUSDT")

    if signal == "BUY":
        print("🟢 Processing BUY")
        quantity = calculate_quantity()
        print("Buy quantity:", quantity)

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
            print("⚠️ Buy quantity was zero — no order placed")

    elif signal == "SELL":
        print("🔴 Processing SELL")
        quantity = calculate_sell_quantity()
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
