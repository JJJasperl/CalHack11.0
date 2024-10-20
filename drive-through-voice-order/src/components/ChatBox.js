import React, { useState, useEffect, useRef } from 'react';
import './ChatBox.css';

const Chatbox = () => {
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const audioContextRef = useRef(null);
  const webSocketRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Initialize WebSocket and Audio Context
  useEffect(() => {
    // Initialize WebSocket connection to backend
    const websocket = new WebSocket('ws://localhost:5000');
    webSocketRef.current = websocket;

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const transcript = data.transcript;

      // Add the transcript to chatbox
      setMessages((prevMessages) => [...prevMessages, { type: 'server', text: transcript }]);
    };

    websocket.onerror = (err) => {
      setError('WebSocket Error: Could not connect to server.');
      console.error('WebSocket Error:', err);
    };

    websocket.onopen = () => {
      console.log('WebSocket Connection Established');
    };

    websocket.onclose = () => {
      console.log('WebSocket Connection Closed');
    };

    // Cleanup WebSocket on component unmount
    return () => {
      websocket.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(audioContext.destination);

      processor.onaudioprocess = (e) => {
        if (!isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0); // Get audio data from the first channel
        const inputBuffer = new Float32Array(inputData);

        // Send the audio data in real-time to the WebSocket server
        if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
          webSocketRef.current.send(inputBuffer);
        }
      };

      setIsRecording(true);
    } catch (err) {
      setError('Error accessing microphone');
      console.error('Microphone access error:', err);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);

    // Stop the audio stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }

    // Clean up the AudioContext and ScriptProcessor
    if (audioContextRef.current) {
      audioContextRef.current.close().then(() => {
        audioContextRef.current = null;
      });
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-messages">
        {messages.map((message, index) => (
          <div key={index} className={`chatbox-message ${message.type}`}>
            {message.text}
          </div>
        ))}
      </div>

      {error && <p className="chatbox-error">{error}</p>}

      <div className="chatbox-controls">
        <button
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          className="chatbox-voice-button"
        >
          {isRecording ? 'Recording...' : 'Hold to Speak'}
        </button>
      </div>
    </div>
  );
};

export default Chatbox;