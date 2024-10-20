from flask import Flask, jsonify, request
from flask_cors import CORS
from cart.cart_handler import ShoppingCart

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize shopping cart (for simplicity, in-memory cart)
cart = ShoppingCart()

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
    app.run(debug=True)