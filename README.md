# Lumifren 🔆

**Lumifren** is an advanced, multi-provider AI chat application with real-time voice integration, long-term semantic memory, and specialized Foundry agents. Originally built as Lumifren, Lumifren has evolved into a high-performance "Aether OS" inspired interface for seamless human-AI collaboration.

![Lumifren UI](https://raw.githubusercontent.com/your-username/lumifren/main/docs/assets/ui-preview.png) *(Placeholder for UI Preview)*

## 🚀 Key Features

-   **Multi-Model Support:** Connect to NVIDIA (Kimi K2.5), GitHub Copilot (GPT-4o), and Google Gemini (2.5 Flash) via a unified interface.
-   **Foundry Agent Integration:**
    -   **Memory Curator:** Automatically extracts and stores important facts from conversations into a Redis-backed long-term memory.
    -   **Tone Detector:** Analyzes user sentiment and mood to adjust response style and resonance.
    -   **Dev Assistant:** Provides technical diagnostic help and code analysis based on project context.
-   **Real-Time Voice Bridge:** Low-latency voice interaction powered by Gemini Multimodal Live, featuring a reactive neural visualizer and customizable vocal engines.
-   **Performance Optimized:** Integrated connection pooling, Redis caching, and streaming response support.
-   **Admin Command Center:** High-tech dashboard for monitoring system metrics, logs, and kernel configuration.

## 🛠️ Tech Stack

-   **Frontend:** HTML5/CSS3 (Aether OS Glassmorphism), Vanilla JS, WebSocket integration.
-   **Backend:** Python 3.11, Flask (Web UI), FastAPI (Agents & Backend Bridge).
-   **Memory:** Redis (Long-term semantic storage and caching).
-   **AI Infrastructure:** NVIDIA NIMs, Azure AI Foundry, Google Generative AI SDK.
-   **DevOps:** Docker & Docker Compose for unified environment management.

## 📦 Quick Start

### 1. Prerequisites
-   Docker Desktop installed and running.
-   Python 3.11+ installed.
-   API Keys for NVIDIA, GitHub, or Google Gemini.

### 2. Infrastructure Setup
Create a shared network for the containers:
```powershell
docker network create lumifren-network
```

Start the unified environment:
```powershell
docker compose up -d
```
This launches:
-   **Lumifren Backend** (Port 3000)
-   **Foundry Agents** (Port 8000)
-   **Redis Database** (Port 6379)
-   **Redis Dashboard** (Port 5000)

### 3. Application Start
Install dependencies and run the Flask app:
```powershell
pip install -r requirements.txt
python lumifren.py
```
Or use the unified script:
```powershell
.\start-chat.ps1
```

### 4. Open Interfaces
-   **Chat UI:** [http://localhost:5001](http://localhost:5001)
-   **Admin Dashboard:** [http://localhost:5001/admin/dashboard](http://localhost:5001/admin/dashboard)
-   **Redis Commander:** [http://localhost:5000](http://localhost:5000)

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
# Core Chat Settings
KIMI_API_KEY=your_nvidia_api_key_here
GITHUB_TOKEN=your_github_pat_here
GEMINI_API_KEY=your_gemini_api_key_here

# Foundry Settings
FOUNDRY_API_KEY=your_foundry_api_key_here
FOUNDRY_PROJECT_ENDPOINT=your_endpoint_here
```

## 🛡️ Security & Privacy

-   **Secret Management:** API keys are never hardcoded and must be provided via `.env`.
-   **Local First:** Conversations and memories are stored in your local Redis instance.
-   **Open Source:** This project is designed for transparency and community development.

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details. Sub-projects and skills may carry additional licenses (e.g., Apache 2.0).

---

Built with 🔆 by the Lumifren Team.
