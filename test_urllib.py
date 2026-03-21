import urllib.request
import time
import json

api_key = "your_nvidia_api_key_here"
url = "https://integrate.api.nvidia.com/v1/chat/completions"
data = json.dumps({
    "model": "moonshotai/kimi-k2.5",
    "messages": [{"role": "user", "content": "Hi"}],
    "stream": True,
    "max_tokens": 10
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
})

start = time.time()
print("Sending request...")
try:
    with urllib.request.urlopen(req) as response:
        print(f"Headers received at {time.time() - start:.2f}s")
        first = False
        for line in response:
            if not first:
                print(f"First chunk at {time.time() - start:.2f}s")
                first = True
            break
except Exception as e:
    print(f"Error: {e}")
