// App.js
import React, { useState } from 'react';
import './App.css';

function App() {
    const [messages, setMessages] = useState([
        { sender: 'McDonald', text: "Welcome to McDonald! I'm the audio ordering system. How can I help you today?" },
        { sender: 'Customer', text: "I'd like to order a Whopper" },
        { sender: 'McDonald', text: "Great! Would you like to add anything else to your order?" },
        { sender: 'Customer', text: "No thanks" },
        { sender: 'McDonald', text: "Your total is $4.19. Please pull forward to pay." }
    ]);

    const [orderItems, setOrderItems] = useState([
        { id: 1, name: 'Whopper', price: 4.19 },
    ]);

    return (
        <div className="App">
            <header className="header">
                <div className="header-left">
                    <div className="header-icon">

                        <div className="logo" style={{backgroundImage: 'url("/logo.png")'}}></div>

                    </div>
                    <h2 className="header-title">McDonald's</h2>
                </div>
            </header>

            <div className="chat-section">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.sender === 'Customer' ? 'customer' : 'burger-king'}`}>
                        <p style={{backgroundColor: "#ffffff", padding: "10px"}}>
                            <div
                                className="header-profile"
                                style={{
                                    backgroundImage: message.sender === 'Customer' ? 'url("https://cdn.usegalileo.ai/stability/efeedeee-8267-40b2-b2e7-18038a00fe5e.png")' : 'url("/m.png")'}}
                            ></div></p>
                        <p>{message.text}</p>
                    </div>
                ))}
                <div className="input-section">
                    <input type="text" placeholder="Type a message" />
                    <button>Send</button>
                </div>
            </div>

            <div className="order-section">
                <h3>Your Order</h3>
                {orderItems.map((item, index) => (
                    <div key={index} className="order-item">
                        <input type="radio" />
                        <p>{item.name}</p>
                        <p>${item.price.toFixed(2)}</p>
                    </div>
                ))}
                <div className="promo-buttons">
                    <button>Cancel</button>

                    <button>Apply</button>
                </div>
            </div>
        </div>
    );
}

export default App;
