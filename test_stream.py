import os
import requests
import json
import time

api_key = "your_nvidia_api_key_here"
base_url = "https://integrate.api.nvidia.com/v1/chat/completions"

payload = {
  "model": "moonshotai/kimi-k2.5",
  "messages": [{"role": "user", "content": "Explain relativity briefly."}],
  "temperature": 0.5,
  "top_p": 1,
  "max_tokens": 100,
  "stream": True
}

headers = {
  "Authorization": f"Bearer {api_key}",
  "Content-Type": "application/json"
}

start = time.time()
response = requests.post(base_url, headers=headers, json=payload, stream=True)
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    if 'reasoning_content' in delta and delta['reasoning_content']:
                        print(f"R[{time.time() - start:.2f}s]: {delta['reasoning_content']}")
                    if 'content' in delta and delta['content']:
                        print(f"C[{time.time() - start:.2f}s]: {delta['content']}")
            except Exception as e:
                print(f"Error parsing at line: {line_str} - {e}")
