// src/App.js

import React, { useState } from 'react';
import ChatBox from './components/ChatBox';
import Cart from './components/Cart';
import './App.css';

function App() {
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);

  // Function to handle adding items to the cart
  const addToCart = (item) => {
    setCartItems((prevItems) => [...prevItems, item]);
    setTotalPrice((prevPrice) => prevPrice + item.price);
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="App-header">
        <h1>Friendly Restaurant</h1>
      </header>

      {/* Main Content */}
      <div className="App-content">
        {/* Left: ChatBox */}
        <div className="Chat-container">
          <ChatBox addToCart={addToCart} />
        </div>

        {/* Right: Cart */}
        <div className="Cart-container">
          <Cart cartItems={cartItems} totalPrice={totalPrice} />
        </div>
      </div>
    </div>
  );
}

export default App;