import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Cart.css';  // New CSS file for styling

const Cart = () => {
  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(0);

  // Fetch the current cart when the component mounts
  useEffect(() => {
    fetchCart();

    // Set up an interval to poll the backend every few seconds
    const interval = setInterval(() => {
      fetchCart();
    }, 5000); // Poll every 5 seconds

    // Clean up the interval on component unmount
    return () => clearInterval(interval);
  }, []);

  // Function to fetch the current cart
  const fetchCart = async () => {
    try {
      const response = await axios.get('http://localhost:5000/cart');
      setCart(response.data.cart);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  return (
    <div className="cart-container">
      <h1 className="cart-title">Your Shopping Cart</h1>

      {/* Display the cart items */}
      <div className="cart-items">
        {cart.length > 0 ? (
          cart.map((item, index) => (
            <div key={index} className="cart-item">
              <span className="cart-item-name">{item.product}</span>
              <span className="cart-item-quantity">x{item.quantity}</span>
              <span className="cart-item-total">${(item.price * item.quantity).toFixed(2)}</span>
              {item.additional_info && (
                <span className="cart-item-info">({item.additional_info})</span>
              )}
            </div>
          ))
        ) : (
          <p className="cart-empty">Your cart is empty</p>
        )}
      </div>

      {/* Display the total */}
      <div className="cart-total">
        <h2>Total: ${total.toFixed(2)}</h2>
      </div>
    </div>
  );
};

export default Cart;