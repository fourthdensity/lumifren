import os
import json
import httpx
import asyncio
import logging
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AGENT_API_URL = os.getenv("AGENT_API_URL", "http://localhost:8000")
USE_AGENTS = os.getenv("USE_AGENTS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lumifren-backend")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API configured")

app = FastAPI(title="Lumifren Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AGENT SERVICE INTEGRATION
# ============================================================================

class AgentService:
    """Client for lumifren-agents service (Foundry-powered)"""
    
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url
        self.timeout = timeout
        self.available = False
        # Async check in background is better, but we'll do simple check
        
    async def check_health(self):
        """Check if agent service is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=2)
                self.available = response.status_code == 200
                if self.available:
                    logger.info(f"✅ Agent service available at {self.base_url}")
        except Exception as e:
            logger.warning(f"⚠️ Agent service unavailable at {self.base_url}: {e}")
            self.available = False
        return self.available
    
    async def curate_memory(self, user_message: str, user_id: str) -> dict:
        """Get memory context from Foundry agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/curate-memory",
                    json={"user_message": user_message, "user_id": user_id},
                    timeout=self.timeout
                )
                return response.json()
        except Exception as e:
            logger.error(f"Memory curation failed: {e}")
            return {"summary": user_message}
    
    async def detect_tone(self, user_message: str, sentiment: str = "neutral") -> dict:
        """Get tone/personality guidance from Foundry agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/detect-tone",
                    json={"user_message": user_message, "sentiment_analysis": sentiment},
                    timeout=self.timeout
                )
                return response.json()
        except Exception as e:
            logger.error(f"Tone detection failed: {e}")
            return {"tone": "neutral", "sentiment": "neutral"}

    async def dev_assistant(self, message: str, context: str = "") -> dict:
        """Get technical assistance from Foundry dev agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/dev-assistant",
                    json={"code_context": context, "issue_description": message},
                    timeout=self.timeout
                )
                return response.json()
        except Exception as e:
            logger.error(f"Dev assistant failed: {e}")
            return {"suggestions": ["Service offline"], "explanation": "Could not reach dev agent."}

# Initialize agent service
agent_service = AgentService(AGENT_API_URL)

# ============================================================================
# REAL-TIME VOICE INTEGRATION (Gemini Multimodal Live)
# ============================================================================

@app.websocket("/ws/voice-real-time")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time voice conversation.
    Acts as a bridge to Gemini Multimodal Live API.
    """
    await websocket.accept()
    logger.info("🔊 Real-time voice WebSocket connected")
    
    # In a full implementation, we would connect to the Gemini Live API here
    # and stream audio chunks between the client and Google.
    
    try:
        while True:
            # Receive data from client (base64 audio or control)
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("type") == "audio_chunk":
                # Process audio chunk (e.g. forward to Gemini)
                # logger.debug("Received audio chunk from client")
                pass
            
            # Send status update for now
            await websocket.send_json({
                "type": "status",
                "message": "Lumifren is listening (Prototype mode)"
            })
            
    except WebSocketDisconnect:
        logger.info("🔊 Real-time voice WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health check"""
    agents_ok = await agent_service.check_health() if USE_AGENTS else False
    return {
        "status": "ok",
        "service": "Lumifren Backend",
        "agents_enabled": USE_AGENTS,
        "agents_available": agents_ok
    }

@app.post("/api/chat")
async def chat(message: str, user_id: str, voice: str = "Puck", foundry_agent: str = "memory"):
    """Main chat endpoint with agent augmentation"""
    
    logger.info(f"Chat request from {user_id} using {foundry_agent} agent")
    
    context = {"user_id": user_id, "voice": voice, "foundry_agent": foundry_agent}
    
    if USE_AGENTS:
        await agent_service.check_health()
        if agent_service.available:
            # We always curate memory and detect tone for the best experience
            context["memory"] = await agent_service.curate_memory(message, user_id)
            context["tone"] = await agent_service.detect_tone(message)
            
            # If user specifically asked for dev assistance
            if foundry_agent == "dev":
                context["dev"] = await agent_service.dev_assistant(message)
    
    try:
        response = await generate_gemini_response(message, context)
        return {
            "response": response,
            "user_id": user_id,
            "voice": voice, 
            "agents_used": USE_AGENTS and agent_service.available,
            "active_module": foundry_agent
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GEMINI GENERATION
# ============================================================================

async def generate_gemini_response(message: str, context: dict) -> str:
    """Generate response from Gemini with augmented context"""
    
    system_prompt = "You are Lumifren, a friendly AI companion. Be helpful and warm."
    
    if "tone" in context:
        tone_data = context["tone"]
        system_prompt += f"\nTONE GUIDANCE: The user's tone is {tone_data.get('tone', 'neutral')} with {tone_data.get('sentiment', 'neutral')} sentiment."
    
    if "memory" in context:
        memory_data = context["memory"]
        system_prompt += f"\n\nMEMORY CONTEXT (Summary of past interactions): {memory_data.get('summary', '')}"

    if "dev" in context:
        dev_data = context["dev"]
        system_prompt += f"\n\nTECHNICAL CONTEXT: You are in Developer Mode. Suggestions: {', '.join(dev_data.get('suggestions', []))}. Explanation: {dev_data.get('explanation', '')}"

    # Use Google SDK
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
    
    # Run in thread pool as genai SDK is synchronous
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: model.generate_content(message))
    
    return response.text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
