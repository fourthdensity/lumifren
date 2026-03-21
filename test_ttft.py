import requests
import time
import json
import sys

api_key = "your_nvidia_api_key_here"
url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "moonshotai/kimi-k2.5",
    "messages": [{"role": "user", "content": "Hi"}],
    "stream": True,
    "max_tokens": 50,
    "temperature": 1.0,
    "extra_body": {
        "chat_template_kwargs": {"thinking": False}
    }
}

print("Sending request...")
start = time.time()
response = requests.post(url, headers=headers, json=payload, stream=True)

print(f"Headers received at {time.time() - start:.2f}s")
first_token = False

for line in response.iter_lines():
    if line:
        if not first_token:
            print(f"First chunk received at {time.time() - start:.2f}s")
            first_token = True
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                delta = data['choices'][0].get('delta', {})
                content = delta.get('content', '') or delta.get('reasoning_content', '')
                if content:
                    sys.stdout.write(content)
                    sys.stdout.flush()
            except Exception as e:
                pass

print(f"\nFinished at {time.time() - start:.2f}s")
