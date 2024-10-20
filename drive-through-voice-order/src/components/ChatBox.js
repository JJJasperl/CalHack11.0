// src/components/ChatBox.js

import React, { useState } from 'react';
import './ChatBox.css';

function ChatBox({ addToCart }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = () => {
    const customerMessage = { sender: 'customer', text: inputMessage };
    setMessages((prevMessages) => [...prevMessages, customerMessage]);

    // Simulate AI agent's response and recognized product
    const aiMessage = { sender: 'agent', text: `Adding ${inputMessage} to your cart.` };
    setMessages((prevMessages) => [...prevMessages, aiMessage]);

    // Simulate recognized products (this could come from the backend in a real app)
    const recognizedProduct = { name: inputMessage, price: 10 }; // Example price
    addToCart(recognizedProduct);

    // Clear the input
    setInputMessage('');
  };

  return (
    <div className="ChatBox">
      <div className="ChatBox-messages">
        {messages.map((message, index) => (
          <div key={index} className={`ChatBox-message ${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="ChatBox-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your order..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default ChatBox;