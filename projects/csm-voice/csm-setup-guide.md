# 🎙️ How to Run CSM (Conversational Speech Model) Locally

A practical guide for running Sesame's CSM-1B text-to-speech model on your own hardware and routing it to a remote server.

---

## 📋 Quick Overview

**CSM-1B** is a 1-billion parameter conversational speech generation model from Sesame that produces high-quality, natural-sounding speech. It uses a Llama-3.2-1B backbone with an audio decoder that generates Mimi audio codes.

### Your Hardware
| Device | GPU | VRAM | Status |
|--------|-----|------|--------|
| Laptop | RTX 3070 | 8GB | ✅ Compatible (tight fit) |
| Desktop | RTX 2080 Ti | 11GB | ✅ Comfortable |

---

## ✅ Prerequisites Checklist

### System Requirements
- [ ] **OS**: Linux (Ubuntu 22.04+ recommended) or Windows 10/11
- [ ] **GPU**: NVIDIA CUDA-compatible GPU with 8GB+ VRAM
- [ ] **RAM**: 16GB+ system RAM recommended
- [ ] **Disk**: ~10GB free space (models + dependencies)
- [ ] **Python**: 3.10 (recommended, though 3.8+ may work)
- [ ] **CUDA**: 12.4 or 12.6 tested (other versions may work)

### Accounts & Access
- [ ] **Hugging Face account** (free): https://huggingface.co/join
- [ ] **Access to Llama-3.2-1B**: https://huggingface.co/meta-llama/Llama-3.2-1B
  - Click "Access Repository" and accept the license
- [ ] **Access to CSM-1B**: https://huggingface.co/sesame/csm-1b
  - Should be immediately available

---

## 🚀 Step-by-Step Installation

### Step 1: System Setup (Linux/Ubuntu)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.10 and essential packages
sudo apt install python3.10 python3.10-venv python3.10-pip git ffmpeg -y

# Verify NVIDIA drivers are installed
nvidia-smi
# Should show your GPU and driver version
```

**For Windows:**
- Install Python 3.10 from python.org
- Install Git for Windows
- Install ffmpeg (via chocolatey: `choco install ffmpeg` or from ffmpeg.org)
- Install CUDA Toolkit 12.x from NVIDIA

### Step 2: Clone Repository & Setup Environment

```bash
# Clone the CSM repository
git clone https://github.com/SesameAILabs/csm.git
cd csm

# Create Python virtual environment
python3.10 -m venv .venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch==2.4.0 torchaudio==2.4.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Install remaining requirements
pip install -r requirements.txt
```

**requirements.txt contents:**
```
torch==2.4.0
torchaudio==2.4.0
tokenizers==0.21.0
transformers==4.49.0
huggingface_hub==0.28.1
moshi==0.2.2
torchtune==0.4.0
torchao==0.9.0
silentcipher @ git+https://github.com/SesameAILabs/silentcipher@master
```

**Windows Note:** If you get Triton errors on Windows:
```bash
pip uninstall triton
pip install triton-windows
```

### Step 4: Environment Configuration

```bash
# Disable lazy compilation in Mimi (important!)
export NO_TORCH_COMPILE=1

# For persistent setting, add to ~/.bashrc or ~/.zshrc:
echo 'export NO_TORCH_COMPILE=1' >> ~/.bashrc
```

### Step 5: Hugging Face Authentication

```bash
# Login to Hugging Face (will prompt for token)
huggingface-cli login
```

**To get your token:**
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "read" access
3. Copy and paste when prompted

---

## 🧪 Testing the Installation

### Quick Test Script

Create `test_csm.py`:

```python
import torch
import torchaudio
from generator import load_csm_1b

# Check device
if torch.cuda.is_available():
    device = "cuda"
    print(f"✅ Using CUDA: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    device = "cpu"
    print("⚠️  CUDA not available, using CPU (will be slow)")

# Load model
print("\n🔄 Loading CSM-1B model...")
generator = load_csm_1b(device=device)
print(f"✅ Model loaded! Sample rate: {generator.sample_rate} Hz")

# Generate audio
print("\n🎙️  Generating speech...")
audio = generator.generate(
    text="Hello! This is a test of the Sesame CSM speech synthesis model.",
    speaker=0,
    context=[],
    max_audio_length_ms=10_000,
)

# Save audio
torchaudio.save("test_output.wav", audio.unsqueeze(0).cpu(), generator.sample_rate)
print("✅ Audio saved to test_output.wav")

# Check VRAM usage (if CUDA)
if device == "cuda":
    vram_used = torch.cuda.memory_allocated() / 1e9
    vram_reserved = torch.cuda.memory_reserved() / 1e9
    print(f"\n📊 VRAM Usage: {vram_used:.1f} GB allocated, {vram_reserved:.1f} GB reserved")
```

Run the test:
```bash
python test_csm.py
```

---

## 🎮 GPU-Specific Notes

### RTX 3070 (8GB VRAM) - Laptop

**Status:** ✅ Works with optimizations

**VRAM Usage Breakdown:**
- Model weights (BF16): ~2.5 GB
- Mimi audio tokenizer: ~1-2 GB
- SilentCipher watermarker: ~1 GB
- Activations/KV cache: ~1-2 GB
- **Total: ~6-7 GB at runtime**

**Optimization Tips:**
```python
# Use bfloat16 (already default in load_csm_1b)
# If still tight, you can try:
import torch

# Clear cache between generations
torch.cuda.empty_cache()

# Monitor VRAM
print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

**Expected Performance:**
- First generation: 10-30 seconds (includes model loading)
- Subsequent generations: 2-5 seconds for short text
- Context length: Keep under 1000 tokens to avoid OOM

### RTX 2080 Ti (11GB VRAM) - Desktop

**Status:** ✅ Comfortable operation

**Headroom:** ~3-4 GB spare VRAM

**Advantages:**
- Can handle longer context sequences
- More consistent generation times
- Room for batch processing

**Expected Performance:**
- First generation: 10-20 seconds
- Subsequent generations: 1-3 seconds for short text
- Context length: Can handle up to 1500+ tokens

### VRAM Reduction Techniques

If you hit OOM errors:

```python
# 1. Reduce max audio length
audio = generator.generate(
    text="Your text here",
    speaker=0,
    context=[],
    max_audio_length_ms=5_000,  # Instead of 10_000
)

# 2. Clear context between sessions
generated_segments = []  # Clear periodically

# 3. Use CPU offloading for watermarker (slower but saves VRAM)
# Edit generator.py to use device="cpu" for watermarker
```

---

## 🌐 Running CSM as an API Service

### Option 1: FastAPI Server (Recommended)

Create `csm_api.py`:

```python
import os
import io
import base64
import torch
import torchaudio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from generator import load_csm_1b, Segment

# Disable Triton compile
os.environ["NO_TORCH_COMPILE"] = "1"

app = FastAPI(title="CSM-1B TTS API")

# Global model instance
generator = None
device = "cuda" if torch.cuda.is_available() else "cpu"

class TTSRequest(BaseModel):
    text: str
    speaker: int = 0
    max_audio_length_ms: int = 10_000
    temperature: float = 0.9
    topk: int = 50

class TTSWithContextRequest(BaseModel):
    text: str
    speaker: int = 0
    context_texts: List[str] = []
    context_speakers: List[int] = []
    max_audio_length_ms: int = 10_000

@app.on_event("startup")
async def load_model():
    global generator
    print(f"🔄 Loading CSM-1B on {device}...")
    generator = load_csm_1b(device=device)
    print("✅ Model loaded!")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "device": device,
        "model": "csm-1b",
        "sample_rate": generator.sample_rate if generator else None
    }

@app.post("/tts")
def text_to_speech(req: TTSRequest):
    """Generate speech from text"""
    try:
        audio = generator.generate(
            text=req.text,
            speaker=req.speaker,
            context=[],
            max_audio_length_ms=req.max_audio_length_ms,
            temperature=req.temperature,
            topk=req.topk,
        )
        
        # Save to buffer
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio.unsqueeze(0).cpu(), generator.sample_rate, format="wav")
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="audio/wav", headers={
            "X-Sample-Rate": str(generator.sample_rate)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/file")
def text_to_speech_file(req: TTSRequest):
    """Generate speech and save to file"""
    try:
        audio = generator.generate(
            text=req.text,
            speaker=req.speaker,
            context=[],
            max_audio_length_ms=req.max_audio_length_ms,
        )
        
        output_path = "output.wav"
        torchaudio.save(output_path, audio.unsqueeze(0).cpu(), generator.sample_rate)
        
        return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/context")
def text_to_speech_with_context(req: TTSWithContextRequest):
    """Generate speech with conversational context"""
    try:
        # Build context segments
        segments = []
        for text, speaker in zip(req.context_texts, req.context_speakers):
            # Note: For context to work properly, you'd need the audio files
            # This is a simplified version
            segments.append(Segment(text=text, speaker=speaker, audio=torch.zeros(1)))
        
        audio = generator.generate(
            text=req.text,
            speaker=req.speaker,
            context=segments,
            max_audio_length_ms=req.max_audio_length_ms,
        )
        
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio.unsqueeze(0).cpu(), generator.sample_rate, format="wav")
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Install FastAPI:**
```bash
pip install fastapi uvicorn
```

**Run the server:**
```bash
python csm_api.py
```

**Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Generate speech
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the CSM API!", "speaker": 0}' \
  --output speech.wav
```

### Option 2: Gradio UI (Interactive)

Create `csm_gradio.py` (based on official HF Space):

```python
import os
import torch
import torchaudio
import gradio as gr
from generator import load_csm_1b, Segment

os.environ["NO_TORCH_COMPILE"] = "1"

device = "cuda" if torch.cuda.is_available() else "cpu"
generator = load_csm_1b(device=device)

def generate_speech(text, speaker_id, max_length_ms):
    """Simple speech generation"""
    audio = generator.generate(
        text=text,
        speaker=int(speaker_id),
        context=[],
        max_audio_length_ms=int(max_length_ms),
    )
    
    # Convert to numpy array for Gradio
    audio_np = audio.cpu().numpy()
    return (generator.sample_rate, audio_np)

# Create Gradio interface
with gr.Blocks(title="CSM-1B TTS") as demo:
    gr.Markdown("# 🎙️ CSM-1B Text-to-Speech")
    gr.Markdown(f"Running on: **{device.upper()}** | Sample rate: **{generator.sample_rate} Hz**")
    
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Text to speak",
                value="Hello! This is a test of the CSM speech model.",
                lines=3
            )
            speaker_id = gr.Dropdown(
                choices=[0, 1, 2, 3],
                value=0,
                label="Speaker ID",
                info="Different IDs produce different voices"
            )
            max_length = gr.Slider(
                minimum=1000,
                maximum=30000,
                value=10000,
                step=1000,
                label="Max Audio Length (ms)"
            )
            generate_btn = gr.Button("🎙️ Generate Speech", variant="primary")
        
        with gr.Column():
            audio_output = gr.Audio(label="Generated Speech", type="numpy")
    
    generate_btn.click(
        fn=generate_speech,
        inputs=[text_input, speaker_id, max_length],
        outputs=[audio_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

**Install Gradio:**
```bash
pip install gradio
```

**Run:**
```bash
python csm_gradio.py
```

Access at: http://localhost:7860

### Option 3: Simple Flask Server

For lightweight use:

```python
from flask import Flask, request, send_file
import torch
import torchaudio
import io
from generator import load_csm_1b

app = Flask(__name__)
device = "cuda" if torch.cuda.is_available() else "cpu"
generator = load_csm_1b(device=device)

@app.route('/tts', methods=['POST'])
def tts():
    text = request.json.get('text', '')
    speaker = request.json.get('speaker', 0)
    
    audio = generator.generate(
        text=text,
        speaker=speaker,
        context=[],
        max_audio_length_ms=10_000,
    )
    
    buffer = io.BytesIO()
    torchaudio.save(buffer, audio.unsqueeze(0).cpu(), generator.sample_rate, format="wav")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="audio/wav")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🔗 Routing to Remote Server

Now that you have CSM running locally, here are options to make it accessible from your remote agent server:

### Option 1: ngrok (Easiest)

**Best for:** Quick testing, temporary access

```bash
# Install ngrok
# Linux
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# macOS
brew install ngrok

# Sign up at https://ngrok.com and get authtoken
ngrok config add-authtoken YOUR_TOKEN

# Expose your CSM API (running on port 8000)
ngrok http 8000
```

**Pros:**
- ✅ Dead simple setup
- ✅ HTTPS out of the box
- ✅ Custom domains on paid plans

**Cons:**
- ❌ Free tier: 1 concurrent connection, random URLs
- ❌ Rate limited
- ❌ Session expires after 2 hours (free)

### Option 2: Cloudflare Tunnel (Recommended)

**Best for:** Permanent-ish setup, custom domains

```bash
# Install cloudflared
# Linux
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# macOS
brew install cloudflared

# Login
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create csm-api

# Configure (~/.cloudflared/config.yml)
# tunnel: YOUR_TUNNEL_ID
# credentials-file: ~/.cloudflared/YOUR_TUNNEL_ID.json
# ingress:
#   - hostname: csm.yourdomain.com
#     service: http://localhost:8000
#   - service: http_status:404

# Run tunnel
cloudflared tunnel route dns csm-api csm.yourdomain.com
cloudflared tunnel run csm-api
```

**Pros:**
- ✅ Free custom domain support
- ✅ No connection limits
- ✅ More stable than ngrok
- ✅ Can run as a service

**Cons:**
- ❌ Requires domain (or use temporary URLs)
- ❌ Slightly more setup

### Option 3: Reverse SSH Tunnel

**Best for:** You control both machines, secure

From your local machine (where CSM runs):
```bash
# Forward local port 8000 to remote server's port 8000
ssh -R 8000:localhost:8000 user@remote-server.com

# For persistent connection with autossh
autossh -M 0 -f -N -R 8000:localhost:8000 user@remote-server.com
```

On the remote server, edit `/etc/ssh/sshd_config`:
```
GatewayPorts yes
```

Then restart SSH: `sudo systemctl restart sshd`

**Pros:**
- ✅ No third-party services
- ✅ Full control
- ✅ Secure (SSH encrypted)

**Cons:**
- ❌ Requires remote server SSH access
- ❌ Connection drops need reconnection (use autossh)
- ❌ Setup on both ends

### Option 4: Local Network (If Same Network)

If both machines are on the same network:

```bash
# Find your local IP
ip addr show  # Linux
ifconfig      # macOS

# Run CSM API bound to all interfaces
# In your Python script:
# uvicorn.run(app, host="0.0.0.0", port=8000)

# Access from other machine
http://YOUR_LOCAL_IP:8000
```

**Pros:**
- ✅ Fastest (local network)
- ✅ No external services

**Cons:**
- ❌ Only works on same network

---

## 🔒 Security Considerations

1. **API Authentication**: Add API key middleware
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.post("/tts", dependencies=[Security(verify_api_key)])
def text_to_speech(req: TTSRequest):
    ...
```

2. **Rate Limiting**: Prevent abuse
```bash
pip install slowapi
```

3. **HTTPS Only**: Use Cloudflare or nginx reverse proxy with SSL

4. **IP Whitelisting**: Restrict access to your remote server's IP

5. **Watermark**: CSM automatically watermarks audio - keep it enabled for ethical use

---

## 🧪 Testing Your Setup

### 1. Local Test
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing one two three", "speaker": 0}' \
  --output test.wav

# Play the audio
ffplay test.wav  # Linux
afplay test.wav  # macOS
```

### 2. Remote Test (via ngrok/Cloudflare)
```bash
curl -X POST https://your-ngrok-or-cloudflare-url/tts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"text": "Hello from the remote server!", "speaker": 1}' \
  --output remote_test.wav
```

### 3. Integration Test with Agent
```python
import requests

def synthesize_speech(text, speaker=0):
    response = requests.post(
        "https://your-csm-url/tts",
        headers={"X-API-Key": "your-secret-key"},
        json={"text": text, "speaker": speaker},
    )
    return response.content  # WAV bytes

# Use in your agent
audio = synthesize_speech("Hello, I'm your AI assistant!")
```

---

## 🔧 Troubleshooting

### Issue: CUDA Out of Memory
**Solution:**
```python
# Reduce max audio length
generator.generate(..., max_audio_length_ms=5_000)

# Clear CUDA cache
torch.cuda.empty_cache()

# Monitor VRAM
nvidia-smi -l 1  # Watch in real-time
```

### Issue: "NO_TORCH_COMPILE not set"
**Solution:**
```bash
export NO_TORCH_COMPILE=1
# Add to ~/.bashrc for persistence
```

### Issue: Hugging Face Access Denied
**Solution:**
1. Visit https://huggingface.co/meta-llama/Llama-3.2-1B
2. Click "Access Repository" and accept license
3. Run `huggingface-cli login` again

### Issue: Slow First Generation
**Expected:** First run downloads models and compiles - takes 30-60s
**Solution:** Subsequent runs will be faster

### Issue: Audio Sounds Robotic
**Solution:** 
- Use context (provide example audio clips)
- Adjust temperature (0.8-0.9 is sweet spot)
- Try different speaker IDs

### Issue: Windows - Triton Errors
**Solution:**
```bash
pip uninstall triton
pip install triton-windows
```

### Issue: "ModuleNotFoundError: No module named 'silentcipher'"
**Solution:**
```bash
pip install git+https://github.com/SesameAILabs/silentcipher@master
```

---

## 🔌 Integration Ideas for Your Agent

### 1. TTS Skill for OpenClaw

Create `skills/csm-tts/SKILL.md`:

```markdown
# CSM TTS Skill

## Overview
Local CSM-1B text-to-speech via remote API

## Configuration
- API_URL: https://your-csm-url/tts
- API_KEY: your-secret-key
- DEFAULT_SPEAKER: 0

## Usage
When the user wants text spoken:
1. Send POST to API_URL with text
2. Save returned WAV to temp file
3. Play audio
```

### 2. Comparison to SAM TTS

| Feature | SAM TTS | CSM-1B |
|---------|---------|--------|
| Quality | Good | Excellent (more natural) |
| Latency | Low | Medium (2-5s generation) |
| VRAM | ~2GB | ~6-7GB |
| Context | No | Yes (conversational) |
| Voice Cloning | No | Partial (via prompts) |
| Cost | API $$$ | Free (local) |
| Setup | None | Complex |

### 3. Workflow Integration

```
User Request → Agent Logic → CSM API (local) → Audio File → Play/Store
                ↓
         (Fallback: SAM TTS if CSM offline)
```

### 4. Batch Processing

For generating multiple audio files:

```python
import asyncio
import aiohttp

async def generate_batch(texts):
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post("http://localhost:8000/tts", json={"text": t})
            for t in texts
        ]
        responses = await asyncio.gather(*tasks)
        return responses
```

---

## 📚 References

- **Official Repo:** https://github.com/SesameAILabs/csm
- **Model Card:** https://huggingface.co/sesame/csm-1b
- **HF Space:** https://huggingface.co/spaces/sesame/csm-1b
- **Llama-3.2-1B:** https://huggingface.co/meta-llama/Llama-3.2-1B
- **Mimi Codec:** https://huggingface.co/kyutai/mimi
- **Sesame Demo:** https://www.sesame.com/voicedemo

---

## 📝 Summary Checklist

- [ ] Prerequisites met (GPU, CUDA, Python 3.10)
- [ ] Hugging Face account with Llama access
- [ ] Repository cloned and environment set up
- [ ] Dependencies installed (PyTorch, moshi, etc.)
- [ ] `NO_TORCH_COMPILE=1` set
- [ ] Hugging Face CLI logged in
- [ ] Test script runs successfully
- [ ] API server implemented (FastAPI/Flask)
- [ ] Remote access configured (ngrok/Cloudflare/SSH)
- [ ] Security measures in place (API keys, HTTPS)
- [ ] Integration with agent tested

---

**Happy synthesizing! 🎙️**
