/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useState } from 'react';
import LiveTTS from './components/LiveTTS';
import VoiceConversation from './components/VoiceConversation';
import FastChat from './components/FastChat';
import { Sparkles, Volume2, Mic, Bolt } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'tts' | 'voice' | 'chat'>('tts');

  const tabs = [
    { id: 'tts', label: 'Speech Gen', icon: Volume2, color: 'emerald' },
    { id: 'voice', label: 'Live Voice', icon: Mic, color: 'blue' },
    { id: 'chat', label: 'Fast Chat', icon: Bolt, color: 'amber' },
  ] as const;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">Gemini Voice Studio</h1>
          </div>
          
          <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700 hover:bg-white/50'
                }`}
              >
                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? `text-${tab.color}-600` : ''}`} />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="w-full flex justify-center"
          >
            {activeTab === 'tts' && <LiveTTS />}
            {activeTab === 'voice' && <VoiceConversation />}
            {activeTab === 'chat' && <FastChat />}
          </motion.div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl">
            <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-emerald-600" />
                Natural Speech
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Convert text to high-quality audio using Gemini's native TTS engine with streaming support.
              </p>
            </div>
            <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <Mic className="w-4 h-4 text-blue-600" />
                Live Conversation
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Experience low-latency voice interactions with the Gemini Live API for natural back-and-forth.
              </p>
            </div>
            <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <Bolt className="w-4 h-4 text-amber-600" />
                Instant Responses
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Get lightning-fast text responses using the optimized Gemini 3.1 Flash Lite model.
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="py-12 border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-slate-400">
            Built with Gemini 2.5 & 3.1 • Real-time AI Studio
          </p>
        </div>
      </footer>
    </div>
  );
}
