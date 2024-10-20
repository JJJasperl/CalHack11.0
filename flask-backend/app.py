import os
import requests
import json
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread
from cart.cart_handler import ShoppingCart
import websocket


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Initialize the shopping cart
cart = ShoppingCart()

# ---- WebSocket Chatbox Functionality ----



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Global variables to manage Deepgram connections
deepgram_connections = {}
deepgram_lock = Lock()

def on_deepgram_message(sid, message):
    data = json.loads(message)
    transcript = data.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
    if transcript:
        socketio.emit('transcript', {'transcript': transcript}, room=sid)

def deepgram_on_error(ws, error):
    print(f"Deepgram WebSocket Error for SID {ws.sid}: {error}")
    socketio.emit('transcript', {'transcript': 'Error with Deepgram transcription.'}, room=ws.sid)

def deepgram_on_close(ws, close_status_code, close_msg):
    print(f"Deepgram WebSocket Closed for SID {ws.sid}: {close_status_code}, {close_msg}")

def deepgram_on_open(ws):
    print(f"Deepgram WebSocket Opened for SID {ws.sid}")
    # Send the configuration message
    settings = {
        "config": {
            "encoding": "linear16",
            "sample_rate": 16000,
            "channels": 1,
            "language": "en-US"
        },
        "interim_results": False
    }
    ws.send(json.dumps(settings))

def deepgram_thread(sid):
    ws_url = f'wss://api.deepgram.com/v1/listen?access_token={DEEPGRAM_API_KEY}&multichannel=false'
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=lambda ws, msg: on_deepgram_message(sid, msg),
        on_error=lambda ws, err: deepgram_on_error(ws, err),
        on_close=lambda ws, code, msg: deepgram_on_close(ws, code, msg),
        on_open=lambda ws: deepgram_on_open(ws)
    )
    ws.sid = sid  # Assign the Socket.IO session ID to the WebSocketApp
    ws.run_forever()

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)
    # Close the Deepgram WebSocket connection if exists
    with deepgram_lock:
        if request.sid in deepgram_connections:
            deepgram_connections[request.sid].close()
            del deepgram_connections[request.sid]

@socketio.on('audio-stream')
def handle_audio_stream(data):
    sid = request.sid
    with deepgram_lock:
        if sid not in deepgram_connections:
            # Start a new Deepgram connection for this client
            deepgram_ws = websocket.WebSocketApp(
                f'wss://api.deepgram.com/v1/listen?access_token={DEEPGRAM_API_KEY}',
                on_message=lambda ws, msg: on_deepgram_message(sid, msg),
                on_error=lambda ws, err: deepgram_on_error(ws, err),
                on_close=lambda ws, code, msg: deepgram_on_close(ws, code, msg),
                on_open=lambda ws: deepgram_on_open(ws)
            )
            deepgram_connections[sid] = deepgram_ws
            # Run WebSocket in a separate thread
            thread = Thread(target=deepgram_ws.run_forever)
            thread.start()
            print(f"Started Deepgram WebSocket for SID {sid}")

        # Send audio data to Deepgram
        try:
            deepgram_connections[sid].send(data, opcode=websocket.ABNF.OPCODE_BINARY)
            print(f"Sent audio chunk to Deepgram for SID {sid}: {len(data)} bytes")
        except Exception as e:
            print(f"Error sending audio to Deepgram for SID {sid}: {e}")
            emit('transcript', {'transcript': 'Error sending audio to Deepgram.'})

# ---- Shopping Cart API Functionality ----

@app.route('/')
def index():
    return "Welcome to the Voice Ordering System!"

# API to add a product to the cart
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product = data.get('product')
    price = data.get('price')
    quantity = data.get('quantity', 1)  # Default quantity is 1 if not provided
    additional_info = data.get('additional_info', '')

    # Add the product to the shopping cart
    cart.add_item(product, price, quantity, additional_info)
    return jsonify({"message": "Product added to cart", "cart": cart.get_cart(), "total": cart.get_total()}), 200

# API to get the current cart
@app.route('/cart', methods=['GET'])
def get_cart():
    return jsonify({"cart": cart.get_cart(), "total": cart.get_total()}), 200

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)