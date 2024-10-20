import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client'; // Import Socket.IO client
import './ChatBox.css';

const Chatbox = () => {
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const audioContextRef = useRef(null);
  const socketRef = useRef(null); // Rename for clarity
  const mediaStreamRef = useRef(null);

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

    socket.on('transcript', (data) => { // Listen for 'transcript' event
      const transcript = data.transcript;
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

      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(audioContext.destination);

      processor.onaudioprocess = (e) => {
        if (!isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0); // Get audio data from the first channel
        // Convert Float32Array to a transferable format, e.g., Int16
        const int16Data = floatTo16BitPCM(inputData);
        // Send the audio data as binary
        if (socketRef.current && socketRef.current.connected) {
          socketRef.current.emit('audio-stream', int16Data);
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

  // Utility function to convert Float32Array to Int16Array
  const floatTo16BitPCM = (input) => {
    const buffer = new ArrayBuffer(input.length * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < input.length; i++) {
      let s = Math.max(-1, Math.min(1, input[i]));
      view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
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