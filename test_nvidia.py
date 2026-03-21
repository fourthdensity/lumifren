import os
import requests
import json

api_key = "your_nvidia_api_key_here"
base_url = "https://integrate.api.nvidia.com/v1/chat/completions"

payload = {
  "model": "moonshotai/kimi-k2.5",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.5,
  "top_p": 1,
  "max_tokens": 10
}

headers = {
  "Authorization": f"Bearer {api_key}",
  "Content-Type": "application/json"
}

response = requests.post(base_url, headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
