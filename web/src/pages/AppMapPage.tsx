import { useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Place } from '@api';
import { api } from '../lib/api';
import PlaceCard from '../components/PlaceCard';

const TASHKENT: [number, number] = [41.311081, 69.279737];

function iconFor(category: string) {
  const color: Record<string, string> = {
    coworking: '#8B5CF6', library: '#18E5F0', cafe: '#F5B841', free_zone: '#39FF88',
  };
  return L.divIcon({
    className: '',
    html: `<div style="width:14px;height:14px;background:${color[category] ?? '#8891A8'};border:2px solid #0B0F1A;border-radius:50%;box-shadow:0 0 10px ${color[category] ?? '#8891A8'}"></div>`,
    iconSize: [14, 14],
  });
}

interface Filters {
  category?: string;
  wifi?: string;
  noise?: string;
  price?: string;
  outlets?: string;
}

export default function AppMapPage() {
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Filters>({});
  const [q, setQ] = useState('');

  const load = async (f: Filters) => {
    setLoading(true);
    try {
      const data = await api.listPlaces({ page_size: 100, ...f });
      setPlaces(data.results);
    } catch {
      setPlaces([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load({});
  }, []);

  const filtered = useMemo(
    () =>
      places.filter(
        (p) =>
          !q ||
          p.name.toLowerCase().includes(q.toLowerCase()) ||
          p.district.toLowerCase().includes(q.toLowerCase()),
      ),
    [places, q],
  );

  const setFilter = (k: keyof Filters, v?: string) => {
    const next = { ...filters, [k]: v };
    if (!v) delete next[k];
    setFilters(next);
    load(next);
  };

  return (
    <div className="grid lg:grid-cols-[380px_1fr] h-[calc(100vh-64px)]">
      <aside className="border-r border-border bg-bg2/30 p-4 overflow-y-auto">
        <h2 className="font-heading text-lg font-bold mb-3">🗺 Joylar</h2>

        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Qidirish…"
          className="input mb-4"
        />

        <p className="text-muted text-xs mb-2">Toifa</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            ['cafe', '☕ Kafe'], ['library', '📚 Kutubxona'],
            ['coworking', '💼 Kovorking'], ['free_zone', '🆓 Bepul'],
          ].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setFilter('category', filters.category === k ? undefined : k)}
              className={`chip ${filters.category === k ? '!border-cyan !text-cyan' : ''}`}
            >
              {l}
            </button>
          ))}
        </div>

        <p className="text-muted text-xs mb-2">Shovqin</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            ['very_quiet', '🤫 Juda tinch'], ['quiet', '😌 Tinch'], ['moderate', '🎵 O\'rtacha'],
          ].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setFilter('noise', filters.noise === k ? undefined : k)}
              className={`chip ${filters.noise === k ? '!border-cyan !text-cyan' : ''}`}
            >
              {l}
            </button>
          ))}
        </div>

        <p className="text-muted text-xs mb-2">Wi-Fi</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[['fast', '⚡ Tez'], ['medium', 'O\'rtacha']].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setFilter('wifi', filters.wifi === k ? undefined : k)}
              className={`chip ${filters.wifi === k ? '!border-cyan !text-cyan' : ''}`}
            >
              {l}
            </button>
          ))}
        </div>

        <p className="text-muted text-xs mb-2">Narx</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[['free', '🆓 Bepul'], ['$', '$'], ['$$', '$$']].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setFilter('price', filters.price === k ? undefined : k)}
              className={`chip ${filters.price === k ? '!border-cyan !text-cyan' : ''}`}
            >
              {l}
            </button>
          ))}
        </div>

        <div className="space-y-3 mt-4">
          {loading && <p className="text-muted text-sm">Yuklanmoqda…</p>}
          {!loading && filtered.length === 0 && (
            <p className="text-muted text-sm">Hech narsa topilmadi.</p>
          )}
          {filtered.slice(0, 15).map((p) => (
            <PlaceCard key={p.id} place={p} />
          ))}
        </div>
      </aside>

      <div className="relative">
        <MapContainer
          center={TASHKENT}
          zoom={12}
          className="h-full w-full"
          style={{ background: '#12172A' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution="&copy; OpenStreetMap &copy; CARTO"
          />
          {filtered.map((p) => (
            <Marker key={p.id} position={[p.lat, p.lng]} icon={iconFor(p.category.key)}>
              <Popup>
                <b>{p.name}</b>
                <br />
                ★ {Number(p.avg_rating).toFixed(1)} · {p.district}
                <br />
                <a href={`#/app/places/${p.id}`} style={{ color: '#18E5F0' }}>
                  Batafsil →
                </a>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
