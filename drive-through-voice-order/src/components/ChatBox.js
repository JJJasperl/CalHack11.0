// src/components/ChatBox.js

import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client'; // Import Socket.IO client
import './ChatBox.css';

const Chatbox = () => {
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const audioContextRef = useRef(null);
  const socketRef = useRef(null); // Socket.IO connection
  const mediaStreamRef = useRef(null);
  const audioChunks = useRef([]); // To accumulate audio data
  const audioProcessorRef = useRef(null); // To keep track of the processor

  // Initialize Socket.IO and Audio Context
  useEffect(() => {
    // Initialize Socket.IO connection to backend
    const socket = io('http://localhost:5000'); // Use HTTP URL
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Socket.IO Connection Established');
    });

    socket.on('disconnect', () => {
      console.log('Socket.IO Connection Closed');
    });

    socket.on('transcript', (data) => {
      const transcript = data.transcript;
      console.log('Received transcript:', transcript);
      setMessages((prevMessages) => [...prevMessages, { type: 'server', text: transcript }]);
    });

    socket.on('connect_error', (err) => {
      setError('Socket.IO Error: Could not connect to server.');
      console.error('Socket.IO Error:', err);
    });

    // Clean up Socket.IO on component unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      // Load the AudioWorklet module
      await audioContext.audioWorklet.addModule('/audio-processor.js');

      // Create an instance of the AudioWorkletNode
      const audioWorkletNode = new AudioWorkletNode(audioContext, 'audio-processor');
      audioProcessorRef.current = audioWorkletNode;

      // Listen for messages from the processor
      audioWorkletNode.port.onmessage = (event) => {
        const int16Buffer = event.data;
        const uint8Array = new Uint8Array(int16Buffer);
        audioChunks.current.push(uint8Array);
        console.log('Accumulating audio chunk:', uint8Array.length);
      };

      // Connect the nodes
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(audioWorkletNode);
      audioWorkletNode.connect(audioContext.destination);

      setIsRecording(true);
      console.log('Recording started');
    } catch (err) {
      setError('Error accessing microphone');
      console.error('Microphone access error:', err);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    console.log('Recording stopped');

    // Stop the audio stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }

    // Clean up the AudioContext and AudioWorkletNode
    if (audioContextRef.current) {
      audioContextRef.current.close().then(() => {
        audioContextRef.current = null;
      });
    }

    if (audioProcessorRef.current) {
      audioProcessorRef.current.port.onmessage = null;
      audioProcessorRef.current.disconnect();
      audioProcessorRef.current = null;
    }

    // Emit 'audio-stop' with the accumulated audio data
    if (socketRef.current && socketRef.current.connected && audioChunks.current.length > 0) {
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/l16' });
      socketRef.current.emit('audio-stop', audioBlob);
      console.log('Emitting audio-stop with blob size:', audioBlob.size);
      audioChunks.current = []; // Reset the chunks
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