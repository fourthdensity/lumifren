import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

ACTIVE_MODEL = config.get('active_model', 'gpt-4.1')

# Dummy API keys and endpoints (replace with your real ones)
OPENAI_ENDPOINT = 'https://api.openai.com/v1/chat/completions'
GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'


def chat_with_model(messages, model=None):
    model = model or ACTIVE_MODEL
    if model == 'gpt-4.1':
        return chat_with_gpt(messages)
    elif model == 'gemini-3-pro':
        return chat_with_gemini(messages)
    else:
        raise ValueError(f"Unknown model: {model}")


def chat_with_gpt(messages):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-4.1',
        'messages': messages,
        'max_tokens': 2048
    }
    response = requests.post(OPENAI_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def chat_with_gemini(messages):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    # Gemini expects a different payload structure
    payload = {
        'contents': [{
            'role': m['role'],
            'parts': [{'text': m['content']}] if 'content' in m else []
        } for m in messages]
    }
    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['candidates'][0]['content']['parts'][0]['text']
