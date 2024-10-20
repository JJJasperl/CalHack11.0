// src/components/ChatBox.js

import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client'; // Import Socket.IO client
import axios from 'axios';
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
    const socket = io('http://localhost:5001'); // Use HTTP URL
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
      addMessage('customer', transcript);
    });

    // Listen for AutoGen output event
    socket.on('autogen_output', (data) => {
      let autogenOutput = data.autogen_output;
      console.log('Frontend received AutoGen Output:', autogenOutput);
      console.log("type of autogen output:", typeof autogenOutput);
      addMessage('agent', autogenOutput);

      if (typeof autogenOutput === 'string') {
        autogenOutput = JSON.parse(autogenOutput);
      }
      console.log("type of autogen output 1:", typeof autogenOutput);
      console.log("autogen output 1:", autogenOutput.transcription, autogenOutput.items);


      const items = autogenOutput.items;
      console.log("items:");
      console.log(items);
      if (items) {
        Object.keys(items).forEach((productName) => {
          const item = items[productName];
          const payload = {
            product: productName,
            price: item.price,
            quantity: item.quantity,
            additional_info: item.comment,
          };
          console.log(payload);
          // Send the item to the backend to add to cart
          axios.post('http://localhost:5001/add-to-cart', payload)
              .then((response) => {
                console.log('Cart updated:', response.data);
              })
              .catch((error) => {
                console.error('Error updating cart:', error);
              });
        });
      }


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

  // Utility function to write a string to DataView
  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  // Utility function to convert Float32Array to Int16Array and encode as WAV
  const encodeWAV = (samples, sampleRate) => {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    /* RIFF identifier */
    writeString(view, 0, 'RIFF');
    /* file length */
    view.setUint32(4, 36 + samples.length * 2, true);
    /* RIFF type */
    writeString(view, 8, 'WAVE');
    /* format chunk identifier */
    writeString(view, 12, 'fmt ');
    /* format chunk length */
    view.setUint32(16, 16, true);
    /* sample format (raw) */
    view.setUint16(20, 1, true);
    /* channel count */
    view.setUint16(22, 1, true);
    /* sample rate */
    view.setUint32(24, sampleRate, true);
    /* byte rate (sample rate * block align) */
    view.setUint32(28, sampleRate * 2, true);
    /* block align (channel count * bytes per sample) */
    view.setUint16(32, 2, true);
    /* bits per sample */
    view.setUint16(34, 16, true);
    /* data chunk identifier */
    writeString(view, 36, 'data');
    /* data chunk length */
    view.setUint32(40, samples.length * 2, true);

    // Write the PCM samples
    let offsetPosition = 44;
    for (let i = 0; i < samples.length; i++, offsetPosition += 2) {
      let s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offsetPosition, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([view], { type: 'audio/wav' });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      console.log('AudioContext Sample Rate:', audioContext.sampleRate); // Log sample rate

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

    // Convert accumulated audio chunks to a single Float32Array
    const float32Audio = decodeAudioChunks(audioChunks.current);
    audioChunks.current = []; // Reset the chunks

    // Encode to WAV using the actual sample rate
    const sampleRate = audioContextRef.current ? audioContextRef.current.sampleRate : 16000;
    const wavBlob = encodeWAV(float32Audio, sampleRate);

    // Emit 'audio-stop' with the WAV blob
    if (socketRef.current && socketRef.current.connected && wavBlob.size > 0) {
      socketRef.current.emit('audio-stop', wavBlob);
      console.log('Emitting audio-stop with WAV blob size:', wavBlob.size);
    }

    // Simulate agent response
    simulateAgentResponse();
  };

  // Function to decode accumulated Uint8Array chunks into Float32Array
  const decodeAudioChunks = (chunks) => {
    const buffer = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0));
    let offset = 0;
    chunks.forEach((chunk) => {
      buffer.set(chunk, offset);
      offset += chunk.length;
    });

    // Convert Uint8Array (little-endian) to Int16Array
    const int16Array = new Int16Array(buffer.buffer, buffer.byteOffset, buffer.byteLength / 2);

    // Convert Int16Array to Float32Array
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 0x8000;
    }

    return float32Array;
  };

  // Function to add a message to the chatbox
  const addMessage = (sender, text) => {
    console.log(`Adding message from ${sender}: ${text}`);
    setMessages((prevMessages) => [...prevMessages, { sender, text }]);
  };

  // Function to simulate agent response
  const simulateAgentResponse = () => {
    const agentResponse = "Thank you for your message! How can I assist you further?";
    // Simulate a delay before responding
    setTimeout(() => {
      addMessage('agent', agentResponse);
    }, 1000); // 1-second delay
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-messages" id="chatbox-messages">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`chatbox-message ${message.sender === 'customer' ? 'customer' : 'agent'}`}
        >
          {message.text}
        </div>
      ))}
      </div>

      {error && <p className="chatbox-error">{error}</p>}

      <div className="chatbox-controls">
      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        className={`chatbox-voice-button ${isRecording ? 'recording' : ''}`}
        aria-label="Hold to speak"
      >
        {isRecording ? 'Recording...' : 'Hold to Speak'}
      </button>
      </div>
    </div>
  );
};

export default Chatbox;