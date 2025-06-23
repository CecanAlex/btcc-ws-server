import threading
import json
import time
from flask import Flask, jsonify
import websocket

last_price = None

def on_message(ws, message):
    global last_price
    data = json.loads(message)
    if 'topic' in data and 'data' in data and 'last' in data['data']:
        last_price = float(data['data']['last'])

def on_open(ws):
    payload = {
        "op": "subscribe",
        "args": ["futures/ticker:BTCUSDT.P"]
    }
    ws.send(json.dumps(payload))

def start_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://ws.btcc.com/ws/futures",
                on_message=on_message,
                on_open=on_open
            )
            ws.run_forever()
        except Exception as e:
            print("Eroare WS:", e)
            time.sleep(5)

# Pornim WebSocket într-un thread separat
ws_thread = threading.Thread(target=start_ws)
ws_thread.daemon = True
ws_thread.start()

# Flask app
app = Flask(__name__)

@app.route("/price")
def price():
    if last_price:
        return jsonify({"last_price": last_price})
    else:
        return jsonify({"error": "Preț indisponibil"}), 503

@app.route("/")
def index():
    return "BTCC WebSocket Server activ!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
