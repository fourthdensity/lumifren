import { useState, useRef, useEffect } from 'react';
import { GoogleGenAI, LiveServerMessage, Modality } from '@google/genai';
import { Mic, MicOff, Loader2, MessageSquare, Volume2 } from 'lucide-react';

export default function VoiceConversation() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcript, setTranscript] = useState<{ role: 'user' | 'model', text: string }[]>([]);
  const sessionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const nextStartTimeRef = useRef<number>(0);

  const connect = async () => {
    setIsConnecting(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });
      
      // Live API output is typically 24kHz
      audioContextRef.current = new AudioContext({ sampleRate: 24000 });
      nextStartTimeRef.current = audioContextRef.current.currentTime;

      const sessionPromise = ai.live.connect({
        model: "gemini-2.5-flash-native-audio-preview-09-2025",
        callbacks: {
          onopen: () => {
            setIsConnected(true);
            setIsConnecting(false);
            startMic();
          },
          onmessage: async (message: LiveServerMessage) => {
            if (message.serverContent?.modelTurn?.parts) {
              for (const part of message.serverContent.modelTurn.parts) {
                if (part.inlineData) {
                  playAudio(part.inlineData.data);
                }
                if (part.text) {
                  setTranscript(prev => [...prev, { role: 'model', text: part.text! }]);
                }
              }
            }
            if (message.serverContent?.interrupted) {
              stopAllAudio();
            }
          },
          onerror: (error) => {
            console.error('Live API Error:', error);
            disconnect();
          },
          onclose: () => {
            setIsConnected(false);
            setIsConnecting(false);
          },
        },
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: { prebuiltVoiceConfig: { voiceName: "Zephyr" } },
          },
          systemInstruction: "You are a helpful conversational assistant. Keep your responses concise and friendly.",
        },
      });
      sessionRef.current = await sessionPromise;
    } catch (err) {
      console.error('Connection failed:', err);
      setIsConnecting(false);
    }
  };

  const disconnect = () => {
    if (sessionRef.current) {
      sessionRef.current.close();
    }
    stopMic();
    setIsConnected(false);
  };

  const startMic = async () => {
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = audioContextRef.current!.createMediaStreamSource(streamRef.current);
      processorRef.current = audioContextRef.current!.createScriptProcessor(4096, 1, 1);

      source.connect(processorRef.current);
      processorRef.current.connect(audioContextRef.current!.destination);

      processorRef.current.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        const pcmData = convertFloat32ToInt16(inputData);
        const base64Data = arrayBufferToBase64(pcmData.buffer);
        
        if (sessionRef.current) {
          sessionRef.current.sendRealtimeInput({
            media: { data: base64Data, mimeType: `audio/pcm;rate=${audioContextRef.current!.sampleRate}` }
          });
        }
      };
    } catch (err) {
      console.error('Mic access failed:', err);
    }
  };

  const stopMic = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (processorRef.current) {
      processorRef.current.disconnect();
    }
  };

  const activeSourcesRef = useRef<AudioBufferSourceNode[]>([]);

  const playAudio = async (base64Audio: string) => {
    if (!audioContextRef.current) return;
    
    // Convert base64 to Int16Array (raw PCM)
    const binaryData = atob(base64Audio);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i);
    }
    const pcmData = new Int16Array(bytes.buffer);
    
    // Convert Int16 to Float32 for Web Audio API
    const float32Data = new Float32Array(pcmData.length);
    for (let i = 0; i < pcmData.length; i++) {
      float32Data[i] = pcmData[i] / 32768.0;
    }

    // Create AudioBuffer
    const audioBuffer = audioContextRef.current.createBuffer(1, float32Data.length, audioContextRef.current.sampleRate);
    audioBuffer.getChannelData(0).set(float32Data);

    // Schedule playback
    const source = audioContextRef.current.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContextRef.current.destination);
    
    const startTime = Math.max(nextStartTimeRef.current, audioContextRef.current.currentTime);
    source.start(startTime);
    nextStartTimeRef.current = startTime + audioBuffer.duration;
    
    activeSourcesRef.current.push(source);
    source.onended = () => {
      activeSourcesRef.current = activeSourcesRef.current.filter(s => s !== source);
    };
  };

  const stopAllAudio = () => {
    activeSourcesRef.current.forEach(source => {
      try {
        source.stop();
      } catch (e) {
        // Source might have already stopped
      }
    });
    activeSourcesRef.current = [];
    if (audioContextRef.current) {
      nextStartTimeRef.current = audioContextRef.current.currentTime;
    }
  };

  const convertFloat32ToInt16 = (buffer: Float32Array) => {
    let l = buffer.length;
    let buf = new Int16Array(l);
    while (l--) {
      buf[l] = Math.min(1, buffer[l]) * 0x7FFF;
    }
    return buf;
  };

  const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  };

  return (
    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-blue-100 rounded-xl">
          <Mic className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Live Conversation</h2>
          <p className="text-sm text-gray-500">Real-time voice chat with Gemini</p>
        </div>
      </div>

      <div className="space-y-6">
        <div className="h-48 overflow-y-auto bg-gray-50 rounded-xl p-4 border border-gray-100 space-y-2">
          {transcript.length === 0 ? (
            <p className="text-gray-400 text-center text-sm mt-16 italic">
              Connect and start speaking...
            </p>
          ) : (
            transcript.map((entry, i) => (
              <div key={i} className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-2 rounded-lg text-sm ${
                  entry.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-gray-700'
                }`}>
                  {entry.text}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex flex-col items-center gap-4">
          <button
            onClick={isConnected ? disconnect : connect}
            disabled={isConnecting}
            className={`w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-lg ${
              isConnected 
                ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            } ${isConnecting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isConnecting ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : isConnected ? (
              <MicOff className="w-8 h-8" />
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </button>
          
          <div className="text-center">
            <p className={`font-medium ${isConnected ? 'text-emerald-600' : 'text-gray-600'}`}>
              {isConnected ? 'Live Session Active' : 'Disconnected'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {isConnected ? 'Gemini is listening...' : 'Click to start conversation'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
