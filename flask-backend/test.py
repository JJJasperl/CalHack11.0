# test_deepgram.py

import os
import requests

DEEPGRAM_API_KEY = 'afad644d7f54cb1c20aee67f2a4998686248a145'
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable not set.")

deepgram_url = 'https://api.deepgram.com/v1/listen'
headers = {
    'Authorization': f'Token {DEEPGRAM_API_KEY}',
    'Content-Type': 'audio/l16; rate=16000; channels=1',
}

# Replace 'path_to_sample.l16' with the path to a valid 16-bit PCM audio file
with open('./test.wav', 'rb') as f:
    audio_data = f.read()

response = requests.post(deepgram_url, headers=headers, data=audio_data)

if response.status_code == 200:
    result = response.json()
    print(result)
    transcript = result.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
    print('Transcript:', transcript)
else:
    print(f"Error: {response.status_code} - {response.text}")