import { useState } from 'react';
import { api, isAuthed } from '../lib/api';
import { useNavigate } from 'react-router-dom';

const CATEGORIES = [
  { key: 'cafe', label: '☕ Kafe' },
  { key: 'library', label: '📚 Kutubxona' },
  { key: 'coworking', label: '💼 Kovorking' },
  { key: 'free_zone', label: '🆓 Bepul zona' },
];

export default function BusinessPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '', category_key: 'cafe', address: '', district: '',
    lat: '41.311081', lng: '69.279737',
    wifi_speed: 'medium', noise_level: 'quiet', price_level: '$',
    outlets_level: 'few', description: '',
  });
  const [status, setStatus] = useState<'idle' | 'ok' | 'err'>('idle');
  const [msg, setMsg] = useState('');

  const submit = async () => {
    if (!isAuthed()) {
      navigate('/register');
      return;
    }
    setStatus('idle');
    try {
      await api.listPlaces; // noop keep import used
    } catch { /* noop */ }
    try {
      const res = await rawCreatePlace(form);
      if (res.ok) {
        setStatus('ok');
        setMsg('Ariza qabul qilindi! Moderatsiyadan so\'ng joy xaritada paydo bo\'ladi.');
      } else {
        setStatus('err');
        setMsg('Xatolik yuz berdi. Qayta urinib ko\'ring.');
      }
    } catch {
      setStatus('err');
      setMsg('Xatolik yuz berdi. Qayta urinib ko\'ring.');
    }
  };

  const rawCreatePlace = async (f: typeof form) => {
    const token = localStorage.getItem('qs_access');
    const res = await fetch('http://localhost:8001/api/places/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify({ ...f, lat: Number(f.lat), lng: Number(f.lng), working_hours: {}, amenities: ['ac', 'toilet'] }),
    });
    return res;
  };

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="font-heading text-3xl font-bold">Joyingizni qo'shing</h1>
      <p className="text-muted mt-2">
        Joyingiz tinch ishlashga mos bo'lsa — uni platformaga qo'shing. Moderatsiyadan
        keyin minglab foydalanuvchilar ko'radi.
      </p>

      <div className="card mt-8 space-y-4">
        <div>
          <label className="text-sm text-muted">Joy nomi</label>
          <input className="input mt-1" value={form.name} onChange={(e) => set('name', e.target.value)} />
        </div>
        <div>
          <label className="text-sm text-muted">Toifa</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {CATEGORIES.map((c) => (
              <button
                key={c.key}
                onClick={() => set('category_key', c.key)}
                className={`chip ${form.category_key === c.key ? '!border-cyan !text-cyan' : ''}`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted">Tuman</label>
            <input className="input mt-1" value={form.district} onChange={(e) => set('district', e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-muted">Manzil</label>
            <input className="input mt-1" value={form.address} onChange={(e) => set('address', e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted">Kenglik (lat)</label>
            <input className="input mt-1" value={form.lat} onChange={(e) => set('lat', e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-muted">Uzunlik (lng)</label>
            <input className="input mt-1" value={form.lng} onChange={(e) => set('lng', e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted">Wi-Fi</label>
            <select className="input mt-1" value={form.wifi_speed} onChange={(e) => set('wifi_speed', e.target.value)}>
              <option value="none">Yo'q</option><option value="slow">Sekin</option>
              <option value="medium">O'rtacha</option><option value="fast">Tez</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-muted">Shovqin</label>
            <select className="input mt-1" value={form.noise_level} onChange={(e) => set('noise_level', e.target.value)}>
              <option value="very_quiet">Juda tinch</option><option value="quiet">Tinch</option>
              <option value="moderate">O'rtacha</option><option value="noisy">Shovqinli</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted">Narx</label>
            <select className="input mt-1" value={form.price_level} onChange={(e) => set('price_level', e.target.value)}>
              <option value="free">Bepul</option><option value="$">$</option>
              <option value="$$">$$</option><option value="$$$">$$$</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-muted">Rozetka</label>
            <select className="input mt-1" value={form.outlets_level} onChange={(e) => set('outlets_level', e.target.value)}>
              <option value="none">Yo'q</option><option value="few">Kam</option>
              <option value="every_table">Har stolda</option>
            </select>
          </div>
        </div>
        <div>
          <label className="text-sm text-muted">Tavsif</label>
          <textarea
            className="input mt-1"
            rows={3}
            value={form.description}
            onChange={(e) => set('description', e.target.value)}
          />
        </div>

        {status === 'ok' && <p className="text-success text-sm">✓ {msg}</p>}
        {status === 'err' && <p className="text-danger text-sm">{msg}</p>}

        <button onClick={submit} className="btn-primary w-full !py-3">
          {isAuthed() ? 'Yuborish' : 'Avval ro\'yxatdan o\'ting'}
        </button>
      </div>
    </div>
  );
}
