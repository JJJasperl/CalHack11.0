# app.py

import os
import json
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable not set.")

# ---- WebSocket Chatbox Functionality ----

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)

@socketio.on('audio-stop')
def handle_audio_stop(audio_blob):
    sid = request.sid
    print(f"Received 'audio-stop' from SID {sid}, blob size: {len(audio_blob)} bytes")

    # Save the Blob to a file for inspection
    audio_filename = f"received_audio_{sid}.l16"
    with open(audio_filename, "wb") as f:
        f.write(audio_blob)
    print(f"Saved audio data to {audio_filename}")

    def deepgram_transcribe():
        deepgram_url = 'https://api.deepgram.com/v1/listen'
        headers = {
            'Authorization': f'Token {DEEPGRAM_API_KEY}',
            'Content-Type': 'audio/l16; rate=16000; channels=1',  # Must match frontend
        }

        try:
            response = requests.post(deepgram_url, headers=headers, data=audio_blob)
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
                if transcript:
                    print(f"Transcription for SID {sid}: {transcript}")
                    # Use socketio.emit instead of emit
                    socketio.emit('transcript', {'transcript': transcript}, room=sid)
                else:
                    print(f"No transcript found for SID {sid}")
                    socketio.emit('transcript', {'transcript': 'No transcript available.'}, room=sid)
            else:
                print(f"Deepgram API Error for SID {sid}: {response.status_code} - {response.text}")
                socketio.emit('transcript', {'transcript': 'Error with Deepgram transcription.'}, room=sid)
        except Exception as e:
            print(f"Exception during Deepgram transcription for SID {sid}: {e}")
            socketio.emit('transcript', {'transcript': 'Exception during transcription.'}, room=sid)

    # Run Deepgram transcription in a separate thread to avoid blocking
    thread = Thread(target=deepgram_transcribe)
    thread.start()

# ---- Shopping Cart API Functionality ----

# Assuming you have a ShoppingCart class defined somewhere
from cart.cart_handler import ShoppingCart
cart = ShoppingCart()  # Initialize the shopping cart

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