import threading
import json
import time
import os
from flask import Flask, jsonify
import websocket

last_price = None  # variabil global actualizat în timp real

# Când primim un mesaj de la WebSocket
def on_message(ws, message):
    global last_price
    try:
        data = json.loads(message)
        print("📨 Mesaj primit:", data)
        if 'topic' in data and 'data' in data and 'last' in data['data']:
            last_price = float(data['data']['last'])
            print("✅ Preț actualizat:", last_price)
    except Exception as e:
        print("❌ Eroare la procesarea mesajului:", e)

# Când se deschide conexiunea WebSocket
def on_open(ws):
    print("🟢 WebSocket deschis!")
    payload = {
        "op": "subscribe",
        "args": ["futures/ticker:BTCUSDT.P"]
    }
    ws.send(json.dumps(payload))
    print("📡 Subscris la BTCUSDT.P")

# Când apare o eroare WebSocket
def on_error(ws, error):
    print("❌ Eroare WebSocket:", error)

# Funcție de pornire/reconectare WebSocket
def start_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://ws.btcc.com/ws/futures",
                on_message=on_message,
                on_open=on_open,
                on_error=on_error
            )
            ws.run_forever()
        except Exception as e:
            print("❗ Excepție în bucla WebSocket:", e)
        time.sleep(5)

# Pornim WebSocket-ul într-un thread separat
ws_thread = threading.Thread(target=start_ws)
ws_thread.daemon = True
ws_thread.start()

# Flask app pentru Render
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ BTCC WebSocket Server activ!"

@app.route("/price")
def price():
    if last_price:
        return jsonify({"last_price": last_price})
    else:
        return jsonify({"error": "Preț indisponibil"}), 503

# Pornire server Flask (Render așteaptă portul din variabila PORT)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

