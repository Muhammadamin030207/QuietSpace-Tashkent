import { useEffect, useRef, useState } from 'react';
import type { AIResult } from '@api';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface Msg {
  role: 'user' | 'ai';
  text: string;
  result?: AIResult;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [userPos, setUserPos] = useState<{ lat?: number; lng?: number }>({});
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (p) => setUserPos({ lat: p.coords.latitude, lng: p.coords.longitude }),
      () => undefined,
      { timeout: 5000 },
    );
    setMessages([
      {
        role: 'ai',
        text: 'Salom! 👋 Men QuietSpace AI yordamchisiman. Menga istalgan talabingizni yozing:\n\n"Chilonzorda rozetkasi bor, jim kafe top" yoki "eng tez Wi-Fi kovorking qayerda?"',
      },
    ]);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  const send = async () => {
    const text = input.trim();
    if (!text || typing) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', text }]);
    setTyping(true);
    try {
      const result = await api.aiChat(text, {
        userLat: userPos.lat,
        userLng: userPos.lng,
        channel: 'miniapp',
      });
      setMessages((m) => [...m, { role: 'ai', text: result.reply, result }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'ai', text: '⚠️ AI xizmati hozircha ishlamayapti. Keyinroq urinib ko\'ring.' },
      ]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <h1 className="font-heading font-bold text-lg">🤖 AI yordamchi</h1>
        <p className="text-muted text-xs">Tabiiy tilda qidiring — AI joylarni topib beradi</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
            <div
              className={`max-w-[85%] rounded-card px-4 py-2.5 text-sm whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-cyan text-bg font-medium'
                  : 'bg-card border border-border'
              }`}
            >
              {m.text}
              {m.result && m.result.places.length > 0 && (
                <div className="mt-3 space-y-2">
                  {m.result.places.map((p) => (
                    <Link
                      key={p.id}
                      to={`/place/${p.id}`}
                      className="block bg-bg2 border border-border rounded-card p-2.5"
                    >
                      <div className="font-medium text-text text-sm">
                        {p.category === 'cafe' ? '☕' : p.category === 'library' ? '📚' : p.category === 'coworking' ? '💼' : '🆓'}{' '}
                        {p.name}
                      </div>
                      <div className="text-muted text-xs mt-0.5">
                        {p.district} · ★ {Number(p.rating).toFixed(1)} · {p.address}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex justify-start">
            <div className="bg-card border border-border rounded-card px-4 py-2.5 text-sm text-muted animate-pulse">
              AI izlayapti…
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="p-3 border-t border-border flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Masalan: jim kafe top…"
          className="input flex-1"
        />
        <button onClick={send} className="btn-primary" disabled={typing || !input.trim()}>
          ➤
        </button>
      </div>
    </div>
  );
}
