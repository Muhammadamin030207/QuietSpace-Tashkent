import { useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Category, Place } from '@api';
import { api } from '../lib/api';
import PlaceCard, { categoryColor } from '../components/PlaceCard';

const TASHKENT: [number, number] = [41.311081, 69.279737];

function UserMarker({ position }: { position: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(position, 14);
  }, [position, map]);
  return (
    <Marker position={position} icon={userIcon}>
      <Popup>📍 Siz shu yerdasiz</Popup>
    </Marker>
  );
}

const userIcon = L.divIcon({
  className: '',
  html: '<div style="width:14px;height:14px;background:#18E5F0;border:3px solid #0B0F1A;border-radius:50%;box-shadow:0 0 12px rgba(24,229,240,0.8)"></div>',
  iconSize: [14, 14],
});

function placeIcon(category: string, selected: boolean) {
  return L.divIcon({
    className: '',
    html: `<div style="width:${selected ? 18 : 14}px;height:${selected ? 18 : 14}px;background:${categoryColor(category)};border:2px solid #0B0F1A;border-radius:50%;box-shadow:0 0 ${selected ? 16 : 8}px ${categoryColor(category)}"></div>`,
    iconSize: [selected ? 18 : 14, selected ? 18 : 14],
  });
}

interface Filters {
  category?: string;
  wifi?: string;
  noise?: string;
  price?: string;
  outlets?: string;
}

export default function MapPage() {
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Filters>({});
  const [sheetOpen, setSheetOpen] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [userPos, setUserPos] = useState<[number, number] | null>(null);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setUserPos([pos.coords.latitude, pos.coords.longitude]),
      () => setUserPos(TASHKENT),
      { timeout: 6000 },
    );
    api
      .stats()
      .then((s) => setCategories(s.categories))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const load = async () => {
      try {
        let data;
        if (userPos) {
          data = await api.nearby(userPos[0], userPos[1], 20);
        } else {
          data = await api.listPlaces({ page_size: 100, ...filters });
        }
        if (!cancelled) setPlaces(data.results);
      } catch {
        if (!cancelled) setPlaces([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [userPos]);

  const applyFilters = async (f: Filters) => {
    setFilters(f);
    setSheetOpen(false);
    setLoading(true);
    try {
      const data = await api.listPlaces({ page_size: 100, ...f });
      setPlaces(data.results);
    } catch {
      /* noop */
    } finally {
      setLoading(false);
    }
  };

  const filteredPlaces = useMemo(
    () => places.filter((p) => !filters.category || p.category.key === filters.category),
    [places, filters],
  );

  return (
    <div className="relative h-full">
      <MapContainer
        center={userPos ?? TASHKENT}
        zoom={13}
        className="h-full w-full"
        style={{ background: '#12172A' }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; OpenStreetMap &copy; CARTO"
        />
        {userPos && <UserMarker position={userPos} />}
        {filteredPlaces.map((p) => (
          <Marker
            key={p.id}
            position={[p.lat, p.lng]}
            icon={placeIcon(p.category.key, false)}
          >
            <Popup>
              <b>{p.name}</b>
              <br />
              ★ {Number(p.avg_rating).toFixed(1)} · {p.district}
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="absolute top-3 left-3 right-3 z-[1000]">
        <button
          onClick={() => setSheetOpen(true)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          🎛 Filtrlar
          {(filters.category || filters.noise) && <span className="bg-bg text-cyan rounded-pill px-2 text-xs">●</span>}
        </button>
      </div>

      <div className="absolute left-3 right-3 bottom-16 z-[1000] flex gap-2 overflow-x-auto pb-1">
        {filteredPlaces.slice(0, 6).map((p) => (
          <div key={p.id} className="shrink-0 w-56">
            <PlaceCard place={p} />
          </div>
        ))}
      </div>

      {loading && (
        <div className="absolute inset-0 z-[999] flex items-center justify-center bg-bg/60">
          <div className="text-cyan animate-pulse">Yuklanmoqda…</div>
        </div>
      )}

      {sheetOpen && (
        <FilterSheet
          categories={categories}
          current={filters}
          onApply={applyFilters}
          onClose={() => setSheetOpen(false)}
        />
      )}
    </div>
  );
}

function FilterSheet({
  categories,
  current,
  onApply,
  onClose,
}: {
  categories: Category[];
  current: Filters;
  onApply: (f: Filters) => void;
  onClose: () => void;
}) {
  const [f, setF] = useState<Filters>(current);
  const chip = (key: keyof Filters) =>
    `chip ${f[key] ? '!border-cyan !text-cyan' : ''}`;

  return (
    <div className="fixed inset-0 z-[2000] bg-black/60" onClick={onClose}>
      <div
        className="absolute bottom-0 left-0 right-0 bg-bg2 rounded-t-card p-5 max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-heading text-lg mb-4">🎛 Filtrlar</h2>

        <p className="text-muted text-sm mb-2">Toifa</p>
        <div className="flex flex-wrap gap-2 mb-4">
          <button className={chip('category')} onClick={() => setF({ ...f, category: undefined })}>
            Hammasi
          </button>
          {categories.map((c) => (
            <button
              key={c.key}
              className={chip('category')}
              onClick={() => setF({ ...f, category: c.key })}
            >
              {c.icon} {c.name_uz}
            </button>
          ))}
        </div>

        <p className="text-muted text-sm mb-2">Wi-Fi</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[['fast', '⚡ Tez'], ['medium', '🫡 O\'rtacha'], ['slow', '🐢 Sekin']].map(([v, l]) => (
            <button
              key={v}
              className={chip('wifi')}
              onClick={() => setF({ ...f, wifi: f.wifi === v ? undefined : v })}
            >
              {l}
            </button>
          ))}
        </div>

        <p className="text-muted text-sm mb-2">Shovqin</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[['very_quiet', '🤫 Juda tinch'], ['quiet', '😌 Tinch'], ['moderate', '🎵 O\'rtacha']].map(([v, l]) => (
            <button
              key={v}
              className={chip('noise')}
              onClick={() => setF({ ...f, noise: f.noise === v ? undefined : v })}
            >
              {l}
            </button>
          ))}
        </div>

        <p className="text-muted text-sm mb-2">Narx</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {[['free', '🆓 Bepul'], ['$', '$'], ['$$', '$$']].map(([v, l]) => (
            <button
              key={v}
              className={chip('price')}
              onClick={() => setF({ ...f, price: f.price === v ? undefined : v })}
            >
              {l}
            </button>
          ))}
        </div>

        <div className="flex gap-3 mt-4">
          <button className="btn-ghost flex-1" onClick={() => onApply({})}>
            Tozalash
          </button>
          <button className="btn-primary flex-1" onClick={() => onApply(f)}>
            Qo'llash
          </button>
        </div>
      </div>
    </div>
  );
}
