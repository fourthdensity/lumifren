import { useRef, useState, useCallback } from 'react';
import { GoogleGenAI, Modality } from '@google/genai';

export type TTSVoice = 'Puck' | 'Charon' | 'Kore' | 'Fenrir' | 'Zephyr';

export interface TTSError {
  message: string;
  type: 'network' | 'api' | 'quota' | 'unknown';
}

export function useTTS() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<TTSError | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const nextStartTimeRef = useRef<number>(0);

  const playPcmChunk = useCallback((base64Data: string) => {
    if (!audioContextRef.current) return;

    const binaryData = atob(base64Data);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i);
    }
    const pcmData = new Int16Array(bytes.buffer);
    
    const float32Data = new Float32Array(pcmData.length);
    for (let i = 0; i < pcmData.length; i++) {
      float32Data[i] = pcmData[i] / 32768.0;
    }

    const audioBuffer = audioContextRef.current.createBuffer(1, float32Data.length, 24000);
    audioBuffer.getChannelData(0).set(float32Data);

    const source = audioContextRef.current.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContextRef.current.destination);
    
    const startTime = Math.max(nextStartTimeRef.current, audioContextRef.current.currentTime);
    source.start(startTime);
    nextStartTimeRef.current = startTime + audioBuffer.duration;
  }, []);

  const speak = useCallback(async (text: string, voice: TTSVoice = 'Kore') => {
    if (!text.trim()) return;
    
    setIsStreaming(true);
    setError(null);

    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext({ sampleRate: 24000 });
    }
    nextStartTimeRef.current = audioContextRef.current.currentTime;
    
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });
      
      const responseStream = await ai.models.generateContentStream({
        model: "gemini-2.5-flash-preview-tts",
        contents: [{ parts: [{ text: `Please speak the following text: ${text}` }] }],
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: { voiceName: voice },
              },
          },
        },
      });

      for await (const chunk of responseStream) {
        const inlineData = chunk.candidates?.[0]?.content?.parts?.[0]?.inlineData;
        if (inlineData) {
          playPcmChunk(inlineData.data);
        }
      }
    } catch (err: any) {
      console.error('TTS Error:', err);
      
      let errorInfo: TTSError = {
        message: 'An unexpected error occurred. Please try again.',
        type: 'unknown'
      };

      const errorMessage = err.message?.toLowerCase() || '';
      
      if (errorMessage.includes('fetch') || errorMessage.includes('network')) {
        errorInfo = {
          message: 'Network error. Please check your internet connection.',
          type: 'network'
        };
      } else if (errorMessage.includes('quota') || errorMessage.includes('429')) {
        errorInfo = {
          message: 'API quota exceeded. Please wait a moment before trying again.',
          type: 'quota'
        };
      } else if (errorMessage.includes('api key') || errorMessage.includes('401') || errorMessage.includes('403')) {
        errorInfo = {
          message: 'Invalid API configuration. Please check your Gemini API key.',
          type: 'api'
        };
      }

      setError(errorInfo);
      throw err;
    } finally {
      setIsStreaming(false);
    }
  }, [playPcmChunk]);

  const stop = useCallback(() => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return { speak, stop, isStreaming, error };
}
