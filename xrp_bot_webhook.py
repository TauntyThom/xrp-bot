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
    signal = data.get("signal", "").lower()
    symbol = data.get("symbol", "XRPUSDT").upper()
    print(f"Received signal: {signal.upper()} for {symbol}")

    if signal == "buy":
        print("🟢 Processing BUY")
        quantity = calculate_quantity(symbol)
        print("Calculated quantity:", quantity)

        if quantity > 0:
            try:
                order = client.create_order(
                    symbol=symbol,
                    side="BUY",
                    type="MARKET",
                    quantity=quantity
                )
                print("✅ Buy order placed:", order)
            except Exception as e:
                print("❌ Order error:", str(e))
        else:
            print("⚠️ Quantity was zero — no order placed")

    elif signal == "sell":
        print("🔴 Processing SELL")
        try:
            asset = symbol.replace("USDT", "")
            balance = client.get_asset_balance(asset=asset)
            quantity = round(float(balance['free']), 1)
            print("Sell quantity:", quantity)

            if quantity > 0:
                order = client.create_order(
                    symbol=symbol,
                    side="SELL",
                    type="MARKET",
                    quantity=quantity
                )
                print("✅ Sell order placed:", order)
            else:
                print("⚠️ No asset available to sell.")
        except Exception as e:
            print("❌ Sell order error:", str(e))

    else:
        print("⚠️ Unrecognized signal.")

    return "OK"
