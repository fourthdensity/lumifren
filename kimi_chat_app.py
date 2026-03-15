import os
import requests
import json
import redis
import time
from flask import Flask, render_template, request, jsonify, Blueprint, Response, stream_with_context, make_response
from datetime import datetime
import hashlib
from dotenv import load_dotenv
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from collections import deque

# --- Logging Setup ---
class DequeHandler(logging.Handler):
    def __init__(self, deque_obj):
        super().__init__()
        self.deque_obj = deque_obj

    def emit(self, record):
        try:
            msg = self.format(record)
            self.deque_obj.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": record.levelname,
                "message": msg
            })
        except Exception:
            self.handleError(record)

app_logs = deque(maxlen=100)
log_handler = DequeHandler(app_logs)
log_handler.setFormatter(logging.Formatter('%(message)s'))
logger = logging.getLogger("kimi")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def log_info(msg):
    print(msg)
    logger.info(msg)

# Load configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Security Settings
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
APP_USER = os.getenv("APP_USER", "admin")
APP_PASS = os.getenv("APP_PASS", "kimi2026")

# --- Performance Optimizations ---

# 1. Connection Pooling for LLM Proxy
http_session = requests.Session()
# Define a high-performance adapter
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(
    pool_connections=100,  # Number of connection pools to cache
    pool_maxsize=100,      # Max number of connections to save in the pool
    max_retries=retries,
    pool_block=False       # Don't block if pool is full, create a new connection instead
)
http_session.mount("http://", adapter)
http_session.mount("https://", adapter)

# Configuration from ENV
KIMI_PROXY_URL = os.getenv("KIMI_PROXY_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshotai/kimi-k2.5")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

PROVIDERS = {
    "nvidia": {
        "url": KIMI_PROXY_URL,
        "key": KIMI_API_KEY,
        "model": KIMI_MODEL
    },
    "github": {
        "url": "https://models.inference.ai.azure.com/chat/completions",
        "key": GITHUB_TOKEN,
        "model": GITHUB_MODEL
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key": GEMINI_API_KEY,
        "model": GEMINI_MODEL
    }
}

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# 2. Redis Connection Pooling
try:
    redis_pool = redis.ConnectionPool(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=0, 
        decode_responses=True,
        max_connections=50,
        socket_keepalive=True,
        socket_timeout=5
    )
    redis_client = redis.Redis(connection_pool=redis_pool)
    redis_client.ping()
    REDIS_AVAILABLE = True
    log_info(f"[OK] Redis connected to {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    REDIS_AVAILABLE = False
    redis_client = None
    log_info(f"[WARN] Redis connection failed: {e}")

# Admin Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Performance Metrics
METRICS = {
    'latencies': [],
    'total_requests': 0,
    'cache_hits': 0,
    'start_time': datetime.now()
}

# Authentication Helpers
def check_auth(username, password):
    return username == APP_USER and password == APP_PASS

def authenticate():
    return make_response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Kimi Admin Login Required"'}
    )

@app.before_request
def global_auth():
    if ENABLE_AUTH:
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

# In-memory fallback
MEMORY_STORE = {}
CONVERSATION_HISTORY = {}
CACHE_STORE = {}

@app.route('/')
def index():
    return render_template('index.html')

def get_cache_key(session_id, message):
    return hashlib.md5(f"{session_id}:{message}".encode()).hexdigest()

# Tool Definitions
MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save an important fact or preference to long-term memory for future sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The concise fact or piece of information to remember."
                    }
                },
                "required": ["fact"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search long-term memory for relevant facts or context about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term or topic to look up."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    METRICS['total_requests'] += 1
    
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    use_memory = data.get('use_memory', True)
    stream = data.get('stream', True)
    provider_name = data.get('provider', 'nvidia')
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    provider = PROVIDERS.get(provider_name, PROVIDERS['nvidia'])

    cache_key = f"cache:{get_cache_key(session_id, message)}"
    if REDIS_AVAILABLE:
        cached_res = redis_client.get(cache_key)
        if cached_res:
            METRICS['cache_hits'] += 1
            METRICS['latencies'].append((time.time() - start_time) * 1000)
            return jsonify(json.loads(cached_res))

    if session_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[session_id] = []

    def generate():
        full_reply = ""
        try:
            # Use enhanced RAG context when memory is enabled
            memory_context = get_memory_context_enhanced(session_id, message) if use_memory else ""
            
            system_prompt = "You are Kimi, a helpful AI assistant. "
            if REDIS_AVAILABLE:
                system_prompt += "You have access to long-term memory via Redis. Use save_memory to store important facts and search_memory to retrieve context. "
            
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            if memory_context:
                messages.append({"role": "system", "content": f"Automatic Context: {memory_context}"})
            
            for msg in CONVERSATION_HISTORY[session_id][-10:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": message})

            # Send immediate visual feedback
            yield f"data: {json.dumps({'status': f'Contacting {provider_name.capitalize()} API...'})}\n\n"

            if memory_context:
                yield f"data: {json.dumps({'memory_context_count': len(memory_context.splitlines())})}\n\n"

            # --- Unified Streaming & Tool Loop ---
            max_iterations = 5
            for iteration in range(max_iterations):
                log_info(f"[STREAM] Starting iteration {iteration+1} for {session_id}")
                
                current_model = provider['model']
                current_url = provider['url']
                current_key = provider['key']

                payload = {
                    "model": current_model,
                    "messages": messages,
                    "max_tokens": 2048,
                    "temperature": 1.0,
                    "stream": True,
                    "tools": MEMORY_TOOLS,
                    "tool_choice": "auto"
                }
                
                # Kimi-specific thinking toggle (only for Kimi models on NVIDIA)
                if provider_name == "nvidia" and "kimi" in current_model.lower():
                    payload["extra_body"] = {"chat_template_kwargs": {"thinking": False}}

                # --- API Call with Retry & Fallback Logic ---
                max_retries = 1
                response = None
                
                for attempt in range(max_retries + 1):
                    try:
                        log_info(f"[STREAM] Calling {provider_name}/{current_model} (Attempt {attempt+1})...")
                        response = http_session.post(current_url, 
                                                   headers={"Authorization": f"Bearer {current_key}"}, 
                                                   json=payload, 
                                                   timeout=90, 
                                                   stream=True)
                        response.raise_for_status()
                        break 
                    except Exception as e:
                        if attempt < max_retries and provider_name == "nvidia":
                            log_info(f"[WARN] {current_model} failed: {e}. Retrying with fallback model...")
                            # Fallback to a super stable model on NVIDIA
                            current_model = "meta/llama-3.3-70b-instruct"
                            payload["model"] = current_model
                            if "extra_body" in payload: del payload["extra_body"]
                            yield f"data: {json.dumps({'status': f'Primary model slow, switching to {current_model}...'})}\n\n"
                        else:
                            log_info(f"[ERROR] API failed: {e}")
                            yield f"data: {json.dumps({'error': f'{provider_name.capitalize()} API error: {str(e)}'})}\n\n"
                            return
                
                if not response: return
                
                current_tool_calls = {}
                assistant_msg_for_history = {"role": "assistant", "content": ""}
                first_token_in_iter = False

                for line in response.iter_lines():
                    if not line: continue
                    line_str = line.decode('utf-8')
                    if not line_str.startswith('data: '): continue
                    
                    data_payload = line_str[6:].strip()
                    if data_payload == "[DONE]": break
                    
                    try:
                        chunk_json = json.loads(data_payload)
                        if 'choices' not in chunk_json or not chunk_json['choices']: continue
                        
                        choice = chunk_json['choices'][0]
                        delta = choice.get('delta', {})

                        if not first_token_in_iter:
                            log_info(f"[STREAM] First chunk received for iteration {iteration+1}")
                            first_token_in_iter = True

                        if 'tool_calls' in delta:
                            for tc_delta in delta['tool_calls']:
                                idx = tc_delta.get('index', 0)
                                if idx not in current_tool_calls:
                                    current_tool_calls[idx] = {
                                        "id": tc_delta.get("id"),
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    }
                                
                                if tc_delta['function'].get('name'):
                                    current_tool_calls[idx]["function"]["name"] += tc_delta['function']['name']
                                if tc_delta['function'].get('arguments'):
                                    current_tool_calls[idx]["function"]["arguments"] += tc_delta['function']['arguments']

                        content = delta.get('content', '')
                        reasoning = delta.get('reasoning_content', '')
                        
                        if content or reasoning:
                            chunk_data = {}
                            if content:
                                chunk_data['content'] = content
                                full_reply += content
                                assistant_msg_for_history["content"] += content
                            if reasoning:
                                chunk_data['reasoning'] = reasoning
                            
                            yield f"data: {json.dumps(chunk_data)}\n\n"

                    except Exception as e:
                        log_info(f"[ERROR] Stream parse error: {e}")
                        continue

                if current_tool_calls:
                    tool_calls_list = list(current_tool_calls.values())
                    messages.append({
                        "role": "assistant",
                        "content": assistant_msg_for_history["content"] or None,
                        "tool_calls": tool_calls_list
                    })

                    for tc in tool_calls_list:
                        f_name = tc['function']['name']
                        f_args = json.loads(tc['function']['arguments'] or "{}")
                        
                        log_info(f"[TOOL] Executing {f_name}({f_args})")
                        
                        if f_name == "save_memory":
                            fact = f_args.get("fact")
                            store_memory(session_id, "User fact", fact)
                            result = "Memory saved successfully."
                            yield f"data: {json.dumps({'status': f'Saving memory: {fact[:30]}...'})}\n\n"
                        elif f_name == "search_memory":
                            query = f_args.get("query")
                            yield f"data: {json.dumps({'status': f'Searching memory for \"{query}\"...'})}\n\n"
                            result = "No specific memories found."
                            if REDIS_AVAILABLE:
                                keys = redis_client.keys(f"memory:{session_id}:*")
                                found = [redis_client.get(k) for k in keys if query.lower() in redis_client.get(k).lower()]
                                if found: result = "\n".join(found[-5:])
                        
                        messages.append({
                            "tool_call_id": tc['id'],
                            "role": "tool",
                            "name": f_name,
                            "content": result,
                        })
                    continue 
                else:
                    break

            CONVERSATION_HISTORY[session_id].append({"role": "user", "content": message})
            CONVERSATION_HISTORY[session_id].append({"role": "assistant", "content": full_reply})
            if use_memory: store_memory(session_id, message, full_reply)

            cache_data = {
                'reply': full_reply, 
                'session_id': session_id, 
                'cached': True,
                'latency': round((time.time() - start_time) * 1000, 2)
            }
            if REDIS_AVAILABLE:
                redis_client.setex(cache_key, 3600, json.dumps(cache_data))

        except Exception as e:
            log_info(f"[ERROR] Generate error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    if stream:
        resp = Response(stream_with_context(generate()), mimetype='text/event-stream')
        resp.headers['X-Accel-Buffering'] = 'no'
        resp.headers['Cache-Control'] = 'no-cache'
        resp.headers['Connection'] = 'keep-alive'
        return resp
    
    return jsonify({'error': 'Streaming required'}), 400

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@admin_bp.route('/api/stats')
def api_stats():
    sessions = []
    total_memories = 0
    for s_id, history in CONVERSATION_HISTORY.items():
        if REDIS_AVAILABLE and redis_client:
            mem_count = len(redis_client.keys(f"memory:{s_id}:*"))
        else:
            mem_count = len(MEMORY_STORE.get(s_id, []))
        
        total_memories += mem_count
        sessions.append({
            'session_id': s_id,
            'messages': len(history),
            'memories': mem_count
        })

    avg_latency = sum(METRICS['latencies']) / len(METRICS['latencies']) if METRICS['latencies'] else 0
    last_latency = METRICS['latencies'][-1] if METRICS['latencies'] else 0

    return jsonify({
        'sessions_count': len(CONVERSATION_HISTORY),
        'total_memories': total_memories,
        'redis_available': REDIS_AVAILABLE,
        'avg_latency': avg_latency,
        'last_latency': last_latency,
        'total_requests': METRICS['total_requests'],
        'sessions': sessions[-5:],
        'uptime_seconds': (datetime.now() - METRICS['start_time']).total_seconds()
    })

@admin_bp.route('/api/logs')
def get_logs():
    return jsonify(list(app_logs))

@app.route('/api/settings', methods=['POST'])
def update_settings():
    global KIMI_MODEL, KIMI_PROXY_URL, ENABLE_AUTH
    data = request.json
    if 'model' in data: KIMI_MODEL = data['model']
    if 'proxy_url' in data: KIMI_PROXY_URL = data['proxy_url']
    if 'enable_auth' in data: ENABLE_AUTH = data['enable_auth']

    # Update providers dict
    PROVIDERS['nvidia']['model'] = KIMI_MODEL
    PROVIDERS['nvidia']['url'] = KIMI_PROXY_URL

    log_info(f"[ADMIN] Settings updated: {data}")
    return jsonify({"status": "updated"})

app.register_blueprint(admin_bp)


def get_memory_context(session_id, current_message):
    context = []
    if REDIS_AVAILABLE and redis_client:
        session_keys = redis_client.keys(f"memory:{session_id}:*")
        imported_keys = redis_client.keys("memory:imported:*")
        if session_keys:
            for key in session_keys[-5:]:
                mem = redis_client.get(key)
                if mem: context.append(mem)
        if imported_keys:
            for key in imported_keys[-5:]:
                mem = redis_client.get(key)
                if mem: context.append(mem)
    else:
        if session_id in MEMORY_STORE:
            context = MEMORY_STORE[session_id][-5:]
    return "\n".join(context) if context else ""

def store_memory(session_id, user_message, assistant_reply):
    memory_entry = f"Q: {user_message}\nA: {assistant_reply[:200]}..."
    timestamp = datetime.now().isoformat()
    if REDIS_AVAILABLE and redis_client:
        key = f"memory:{session_id}:{timestamp}"
        redis_client.setex(key, 30*24*60*60, memory_entry)
        log_info(f"[DEBUG] Stored memory in Redis: {key}")
        # Also create embedding for semantic search
        embed_and_store(session_id, user_message, assistant_reply, timestamp)
    else:
        if session_id not in MEMORY_STORE:
            MEMORY_STORE[session_id] = []
        MEMORY_STORE[session_id].append(memory_entry)
        if len(MEMORY_STORE[session_id]) > 50:
            MEMORY_STORE[session_id] = MEMORY_STORE[session_id][-50:]
        log_info(f"[DEBUG] Stored memory in-memory")

# ============================================================
# GEMINI EMBEDDINGS & SEMANTIC SEARCH (RAG)
# ============================================================
import numpy as np
from threading import Thread

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 3072  # Gemini embedding dimension (gemini-embedding-001)

def get_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    """Generate embedding using Gemini API."""
    if not GEMINI_API_KEY:
        log_info("[EMBED] No Gemini API key configured")
        return None
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBEDDING_MODEL}:embedContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        payload = {
            "model": f"models/{EMBEDDING_MODEL}",
            "content": {"parts": [{"text": text[:8000]}]},  # Truncate to avoid limits
            "taskType": task_type
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", {}).get("values", [])
            log_info(f"[EMBED] Generated embedding with {len(embedding)} dimensions")
            return embedding
        else:
            log_info(f"[EMBED] Error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        log_info(f"[EMBED] Exception: {e}")
        return None

def embed_and_store(session_id, user_message, assistant_reply, timestamp):
    """Embed a conversation turn and store in Redis (async)."""
    def _embed_task():
        try:
            # Combine Q&A for context
            combined_text = f"User asked: {user_message}\nAssistant replied: {assistant_reply[:500]}"
            embedding = get_embedding(combined_text, "RETRIEVAL_DOCUMENT")
            
            if embedding and REDIS_AVAILABLE and redis_client:
                # Store embedding as JSON in Redis
                embed_key = f"embed:{session_id}:{timestamp}"
                embed_data = {
                    "session_id": session_id,
                    "user_message": user_message,
                    "assistant_reply": assistant_reply[:500],
                    "timestamp": timestamp,
                    "embedding": embedding
                }
                redis_client.setex(embed_key, 30*24*60*60, json.dumps(embed_data))
                log_info(f"[EMBED] Stored embedding: {embed_key}")
        except Exception as e:
            log_info(f"[EMBED] Store error: {e}")
    
    # Run in background thread to not block response
    Thread(target=_embed_task, daemon=True).start()

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

def semantic_search(query, session_id=None, top_k=5, threshold=0.5):
    """Search for semantically similar past conversations."""
    if not REDIS_AVAILABLE or not redis_client:
        return []
    
    # Get query embedding
    query_embedding = get_embedding(query, "RETRIEVAL_QUERY")
    if not query_embedding:
        log_info("[EMBED] Failed to get query embedding")
        return []
    
    results = []
    
    # Get all embeddings (optionally filter by session)
    pattern = f"embed:{session_id}:*" if session_id else "embed:*"
    embed_keys = redis_client.keys(pattern)
    log_info(f"[EMBED] Found {len(embed_keys)} embedding keys matching pattern: {pattern}")
    
    for key in embed_keys:
        try:
            # Handle bytes keys from Redis
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            data = redis_client.get(key_str)
            if data:
                # Handle bytes data
                data_str = data.decode('utf-8') if isinstance(data, bytes) else data
                embed_data = json.loads(data_str)
                stored_embedding = embed_data.get("embedding", [])
                
                similarity = cosine_similarity(query_embedding, stored_embedding)
                
                if similarity >= threshold:
                    results.append({
                        "session_id": embed_data.get("session_id"),
                        "user_message": embed_data.get("user_message"),
                        "assistant_reply": embed_data.get("assistant_reply"),
                        "timestamp": embed_data.get("timestamp"),
                        "similarity": round(similarity, 4)
                    })
        except Exception as e:
            log_info(f"[EMBED] Error processing key {key}: {e}")
            continue
    
    # Sort by similarity and return top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    log_info(f"[EMBED] Returning {len(results)} results")
    return results[:top_k]

def get_rag_context(session_id, current_message, top_k=3):
    """Get relevant context from past conversations for RAG."""
    relevant = semantic_search(current_message, session_id=None, top_k=top_k, threshold=0.4)
    
    if not relevant:
        return ""
    
    context_parts = []
    for item in relevant:
        context_parts.append(f"[Previous conversation ({item['similarity']:.0%} relevant)]")
        context_parts.append(f"User: {item['user_message']}")
        context_parts.append(f"Assistant: {item['assistant_reply'][:200]}...")
        context_parts.append("")
    
    return "\n".join(context_parts)

# Enhanced memory context with RAG
def get_memory_context_enhanced(session_id, current_message):
    """Get memory context with semantic search enhancement."""
    # Get basic memory context
    basic_context = get_memory_context(session_id, current_message)
    
    # Get RAG context from semantic search
    rag_context = get_rag_context(session_id, current_message)
    
    if rag_context and basic_context:
        return f"Recent Memory:\n{basic_context}\n\nRelevant Past Conversations:\n{rag_context}"
    elif rag_context:
        return f"Relevant Past Conversations:\n{rag_context}"
    else:
        return basic_context

# API Endpoints for Semantic Search
@app.route('/api/search', methods=['POST'])
def api_semantic_search():
    """Search past conversations semantically."""
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id')  # Optional: filter by session
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.4)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    results = semantic_search(query, session_id, top_k, threshold)
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/api/embeddings/stats', methods=['GET'])
def embedding_stats():
    """Get embedding statistics."""
    if not REDIS_AVAILABLE or not redis_client:
        return jsonify({'error': 'Redis not available'}), 500
    
    embed_keys = redis_client.keys("embed:*")
    sessions = set()
    for key in embed_keys:
        # Handle bytes keys
        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
        parts = key_str.split(":")
        if len(parts) >= 2:
            sessions.add(parts[1])
    
    return jsonify({
        'total_embeddings': len(embed_keys),
        'sessions_with_embeddings': len(sessions),
        'embedding_model': EMBEDDING_MODEL,
        'embedding_dimension': EMBEDDING_DIM
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = []
    for s_id, history in CONVERSATION_HISTORY.items():
        if REDIS_AVAILABLE and redis_client:
            mem_count = len(redis_client.keys(f"memory:{s_id}:*"))
        else:
            mem_count = len(MEMORY_STORE.get(s_id, []))
        sessions.append({'session_id': s_id, 'messages': len(history), 'memories': mem_count})
    return jsonify(sessions)

@app.route('/api/sessions/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    if session_id in CONVERSATION_HISTORY: del CONVERSATION_HISTORY[session_id]
    if REDIS_AVAILABLE and redis_client:
        for key in redis_client.keys(f"memory:{session_id}:*"): redis_client.delete(key)
    elif session_id in MEMORY_STORE: del MEMORY_STORE[session_id]
    return jsonify({'status': 'cleared'})

@app.route('/api/settings', methods=['GET'])
def settings():
    return jsonify({
        'model': KIMI_MODEL,
        'proxy_url': KIMI_PROXY_URL,
        'redis_enabled': REDIS_AVAILABLE,
        'enable_auth': ENABLE_AUTH,
        'memory_backend': 'redis' if REDIS_AVAILABLE else 'in-memory',
        'providers': list(PROVIDERS.keys())
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    # Only return the Gemini key for frontend voice features
    return jsonify({
        'gemini_api_key': GEMINI_API_KEY
    })

if __name__ == '__main__':
    log_info("\n" + "="*60)
    log_info("Kimi Chat Interface (Multi-Provider)")
    log_info("="*60)
    log_info(f"Chat UI: http://portalv2:5001")
    log_info(f"Admin UI: http://portalv2:5001/admin/dashboard")
    log_info(f"NVIDIA API: {KIMI_PROXY_URL}")
    log_info(f"Memory Backend: {'Redis' if REDIS_AVAILABLE else 'In-Memory'}")
    log_info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    log_info("="*60 + "\n")
    # Bind to all interfaces to allow Tailscale access
    app.run(debug=True, host='0.0.0.0', port=5001)
