import requests
import time
import json

api_key = "your_nvidia_api_key_here"
url = "https://integrate.api.nvidia.com/v1/chat/completions"

def test_model(model_name, extra_body=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": True,
        "max_tokens": 10
    }
    if extra_body:
        payload["extra_body"] = extra_body

    print(f"\n--- Testing {model_name} ---")
    start = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        print(f"Headers received: {time.time() - start:.2f}s")
        
        for line in response.iter_lines():
            if line:
                print(f"First chunk received: {time.time() - start:.2f}s")
                break
    except Exception as e:
        print(f"Error: {e}")

test_model("meta/llama-3.1-8b-instruct")
test_model("moonshotai/kimi-k2.5", {"chat_template_kwargs": {"thinking": False}})

# NEW TEST: Kimi without extra_body and WITHOUT tools (payload default)
def test_model_no_tools(model_name):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_name, "messages": [{"role": "user", "content": "Hi"}], "stream": True, "max_tokens": 10}
    print(f"\n--- Testing {model_name} (NO TOOLS) ---")
    start = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        print(f"Headers: {time.time() - start:.2f}s")
        for line in response.iter_lines():
            if line:
                print(f"First chunk: {time.time() - start:.2f}s")
                break
    except Exception as e: print(f"Error: {e}")

test_model_no_tools("moonshotai/kimi-k2.5")
