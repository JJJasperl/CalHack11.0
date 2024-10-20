// public/audio-processor.js

class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      this.port.onmessage = (event) => {
        // Handle messages from the main thread if needed
      };
    }
  
    process(inputs, outputs, parameters) {
      const input = inputs[0];
      if (input.length > 0) {
        const channelData = input[0];
        // Convert Float32Array to Int16Array
        const int16Data = this.float32ToInt16(channelData);
        // Send the processed audio data to the main thread
        this.port.postMessage(int16Data.buffer);
      }
      return true; // Keep processor alive
    }
  
    float32ToInt16(float32) {
      const int16 = new Int16Array(float32.length);
      for (let i = 0; i < float32.length; i++) {
        let s = Math.max(-1, Math.min(1, float32[i]));
        int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }
      return int16;
    }
  }
  
  registerProcessor('audio-processor', AudioProcessor);