from flask import Flask, request
import os
from binance.client import Client
from dotenv import load_dotenv

# Load .env keys
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Connect to Binance Testnet
client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'  # Testnet URL

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

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = data.get("signal")
    print("Received signal:", signal)

    if signal == "BUY":
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
                print("❌ Order error:", str(e))
        else:
            print("⚠️ Quantity was zero — no order placed")
    return "OK"
