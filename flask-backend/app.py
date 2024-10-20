import os
import requests
import json
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread
from cart.cart_handler import ShoppingCart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Initialize the shopping cart
cart = ShoppingCart()

# ---- WebSocket Chatbox Functionality ----

# WebSocket event for receiving audio and sending it to Deepgram
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('audio-stream')
def handle_audio_stream(data):
    # This function will receive audio data from the client and send it to Deepgram
    def deepgram_stream():
        deepgram_url = 'https://api.deepgram.com/v1/listen/stream'
        headers = {
            'Authorization': f'Token {DEEPGRAM_API_KEY}',
            'Content-Type': 'audio/webm',
        }

        # Send the audio to Deepgram
        response = requests.post(deepgram_url, headers=headers, data=data, stream=True)

        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                transcript = decoded_line.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
                if transcript:
                    # Emit the transcript back to the frontend via WebSocket
                    emit('transcript', {'transcript': transcript}, broadcast=True)

    # Run the Deepgram streaming in a separate thread
    thread = Thread(target=deepgram_stream)
    thread.start()

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