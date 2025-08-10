import websocket
import json
import time
import threading
import requests
import os
import sys

# Secrets from environment variables
CHAT_ID = os.getenv("TELEGRAM_CHAT")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
WS_URL = os.getenv("WS_URL")

if not all([CHAT_ID, BOT_TOKEN, WS_URL]):
    print("❌ Missing required environment variables", file=sys.stderr)
    sys.exit(1)

def send_telegram(msg):
    """Send a message to Telegram chat"""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)

def on_message(ws, message):
    print(f"📩 Incoming message: {message}")
    try:
        data = json.loads(message)
        print(f"📦 Parsed data: {data}")
    except json.JSONDecodeError:
        return

    # Example condition – adjust according to actual data
    if isinstance(data, dict) and data.get("type") == "new_round":
        send_telegram("⚠️ Event detected — 10s delay...")
        time.sleep(10)
        send_telegram("🎯 Event triggered!")

def on_open(ws):
    send_telegram("🚀 Connected to WebSocket — waiting for events")

def on_close(ws, close_status_code, close_msg):
    print("🔴 Connection closed. Reconnecting in 5s...")
    time.sleep(5)
    reconnect()

def on_error(ws, error):
    print(f"⚠️ WebSocket error: {error}")
    time.sleep(5)
    reconnect()

def run_bot():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

def reconnect():
    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    send_telegram("🤖 Service started — listening...")
    reconnect()
    while True:  # Continuous loop to keep service alive
        time.sleep(60)
