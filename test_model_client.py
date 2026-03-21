from model_client import chat_with_model

# Example conversation
messages = [
    {"role": "user", "content": "Hello, who are you?"}
]

try:
    reply = chat_with_model(messages)
    print("Model reply:", reply)
except Exception as e:
    print("Error:", e)
