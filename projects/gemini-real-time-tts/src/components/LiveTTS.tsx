import { useState } from 'react';
import { Loader2, Volume2, VolumeX } from 'lucide-react';
import { useTTS, TTSVoice } from '../hooks/useTTS';

export default function LiveTTS() {
  const [text, setText] = useState('');
  const [selectedVoice, setSelectedVoice] = useState<TTSVoice>('Kore');
  const { speak, isStreaming, error } = useTTS();

  const voices: TTSVoice[] = ['Puck', 'Charon', 'Kore', 'Fenrir', 'Zephyr'];

  const handleSpeak = async () => {
    try {
      await speak(text, selectedVoice);
    } catch (err) {
      // Error is handled by the hook and exposed via the 'error' state
    }
  };

  return (
    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-emerald-100 rounded-xl">
          <Volume2 className="w-6 h-6 text-emerald-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Speech Generator</h2>
          <p className="text-sm text-gray-500">Convert your text to natural audio</p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-700">Select Voice</label>
          <div className="grid grid-cols-3 gap-2">
            {voices.map((voice) => (
              <button
                key={voice}
                onClick={() => setSelectedVoice(voice)}
                className={`px-3 py-2 text-xs rounded-lg border transition-all ${
                  selectedVoice === voice
                    ? 'bg-emerald-600 border-emerald-600 text-white shadow-sm'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-emerald-300'
                }`}
              >
                {voice}
              </button>
            ))}
          </div>
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full h-32 p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all resize-none text-gray-700 placeholder:text-gray-400"
          placeholder="Type something you want me to say..."
        />

        {error && (
          <div className={`flex items-center gap-2 text-sm p-3 rounded-lg ${
            error.type === 'quota' ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-600'
          }`}>
            <VolumeX className="w-4 h-4" />
            {error.message}
          </div>
        )}

        <button
          onClick={handleSpeak}
          disabled={isStreaming || !text.trim()}
          className={`w-full py-4 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
            isStreaming 
              ? 'bg-emerald-50 text-emerald-600 cursor-not-allowed' 
              : 'bg-emerald-600 text-white hover:bg-emerald-700 active:scale-[0.98] shadow-lg shadow-emerald-200'
          }`}
        >
          {isStreaming ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Streaming Audio...</span>
            </>
          ) : (
            <>
              <Volume2 className="w-5 h-5" />
              <span>Generate Speech</span>
            </>
          )}
        </button>

        {isStreaming && (
          <div className="flex justify-center gap-1 mt-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="w-1 bg-emerald-500 rounded-full animate-bounce"
                style={{
                  height: `${Math.random() * 20 + 10}px`,
                  animationDelay: `${i * 0.1}s`,
                  animationDuration: '0.6s'
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
