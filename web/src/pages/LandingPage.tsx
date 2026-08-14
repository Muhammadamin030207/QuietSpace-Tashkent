import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { AIResult, Stats } from '@api';
import { api } from '../lib/api';

export default function LandingPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [aiInput, setAiInput] = useState('');
  const [aiResult, setAiResult] = useState<AIResult | null>(null);
  const [aiBusy, setAiBusy] = useState(false);

  useEffect(() => {
    api
      .stats()
      .then(setStats)
      .catch(() => undefined);
  }, []);

  const askAI = async () => {
    const q = aiInput.trim();
    if (!q || aiBusy) return;
    setAiBusy(true);
    setAiResult(null);
    try {
      const result = await api.aiChat(q, { channel: 'web' });
      setAiResult(result);
    } catch {
      setAiResult({ reply: '⚠️ AI xizmati hozircha ishlamayapti. Keyinroq urinib ko\'ring.', place_ids: [], places: [] });
    } finally {
      setAiBusy(false);
    }
  };

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-40 pointer-events-none"
          style={{
            background:
              'radial-gradient(600px 300px at 20% 20%, rgba(139,92,246,0.25), transparent), radial-gradient(600px 300px at 80% 30%, rgba(24,229,240,0.2), transparent)',
          }}
        />
        <div className="max-w-6xl mx-auto px-4 py-20 sm:py-28 text-center relative">
          <h1 className="font-heading text-4xl sm:text-6xl font-bold leading-tight">
            Toshkentda <span className="text-cyan">tinch ishlash</span> joyini{' '}
            <span className="text-violet">toping</span>
          </h1>
          <p className="text-muted text-lg mt-5 max-w-2xl mx-auto">
            QuietSpace — kafelar, kutubxonalar, kovorkinglar va bepul zonalarning real
            ma'lumotlari: Wi-Fi tezligi, shovqin darajasi, rozetkalar, jonli bandlik.
          </p>

          <div className="max-w-xl mx-auto mt-8">
            <div className="flex gap-2 bg-card border border-border rounded-pill p-2 shadow-glowCyan/30">
              <input
                value={aiInput}
                onChange={(e) => setAiInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && askAI()}
                placeholder="AI'dan so'rang: «Chilonzorda jim kafe top»…"
                className="flex-1 bg-transparent px-4 outline-none text-sm placeholder:text-muted"
              />
              <button onClick={askAI} disabled={aiBusy} className="btn-primary !py-2">
                {aiBusy ? 'Izlamoqda…' : "AI so'ra"}
              </button>
            </div>

            {aiResult && (
              <div className="card mt-4 text-left">
                <p className="text-sm whitespace-pre-wrap">{aiResult.reply}</p>
                {aiResult.places.length > 0 && (
                  <div className="mt-3 grid gap-2">
                    {aiResult.places.slice(0, 4).map((p) => (
                      <Link
                        key={p.id}
                        to={`/app/places/${p.id}`}
                        className="flex justify-between bg-bg2 border border-border rounded-card px-4 py-3 text-sm hover:border-cyan/50"
                      >
                        <span className="font-medium">{p.name}</span>
                        <span className="text-muted">
                          {p.district} · ★ {Number(p.rating).toFixed(1)}
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-center gap-8 mt-12">
            <div className="text-center">
              <p className="font-heading text-3xl font-bold text-cyan">{stats?.places_count ?? '…'}</p>
              <p className="text-muted text-sm">joylar</p>
            </div>
            <div className="text-center">
              <p className="font-heading text-3xl font-bold text-violet">{stats?.reviews_count ?? '…'}</p>
              <p className="text-muted text-sm">sharhlar</p>
            </div>
            <div className="text-center">
              <p className="font-heading text-3xl font-bold text-success">4</p>
              <p className="text-muted text-sm">toifa</p>
            </div>
          </div>

          <div className="flex justify-center gap-4 mt-10">
            <Link to="/app" className="btn-primary">🗺 Xaritani ochish</Link>
            <Link to="/business" className="btn-ghost">Joy qo'shish</Link>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-6xl mx-auto px-4 py-14">
        <h2 className="font-heading text-2xl font-bold mb-6">Qanday joylarni topamiz?</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: '☕', name: 'Kafelar', color: '#F5B841', desc: 'Wi-Fi va rozetkali, ishlashga mos' },
            { icon: '📚', name: 'Kutubxonalar', color: '#18E5F0', desc: 'Juda tinch, jamiyatda muhit' },
            { icon: '💼', name: 'Kovorkinglar', color: '#8B5CF6', desc: 'Professional ish muhiti' },
            { icon: '🆓', name: 'Bepul zonalar', color: '#39FF88', desc: 'Hech qanday xarajatsiz' },
          ].map((c) => (
            <div key={c.name} className="card hover:border-cyan/40 transition-colors">
              <div
                className="w-12 h-12 rounded-card flex items-center justify-center text-2xl mb-3"
                style={{ backgroundColor: `${c.color}22` }}
              >
                {c.icon}
              </div>
              <h3 className="font-heading font-semibold" style={{ color: c.color }}>{c.name}</h3>
              <p className="text-muted text-sm mt-1">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-border bg-bg2/40">
        <div className="max-w-6xl mx-auto px-4 py-14 grid gap-8 md:grid-cols-3">
          <div>
            <p className="text-2xl mb-2">🤖</p>
            <h3 className="font-heading font-semibold">AI yordamchi</h3>
            <p className="text-muted text-sm mt-1">
              «Menga rozetkasi bor, jim joy kerak» — AI buni tushunadi va real joylarni
              topib beradi.
            </p>
          </div>
          <div>
            <p className="text-2xl mb-2">📍</p>
            <h3 className="font-heading font-semibold">Jonli bandlik</h3>
            <p className="text-muted text-sm mt-1">
              Foydalanuvchilar «Men shu yerdaman» deb belgilaydi — borishingizdan oldin
              bo'sh yoki to'la ekanini bilasiz.
            </p>
          </div>
          <div>
            <p className="text-2xl mb-2">📊</p>
            <h3 className="font-heading font-semibold">Real sharhlar</h3>
            <p className="text-muted text-sm mt-1">
              Wi-Fi, shovqin va qulaylik bo'yicha alohida reytinglar. AI har bir joy
              uchun xulosa yaratadi.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
