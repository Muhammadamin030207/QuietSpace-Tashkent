import { useCallback, useEffect, useState } from 'react';
import type { Place } from '@api';
import { api } from '../lib/api';
import PlaceCard from '../components/PlaceCard';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.favorites();
      setFavorites(data.map((f) => f.place));
    } catch {
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="p-4">
      <h1 className="font-heading text-xl font-bold mb-4">⭐ Sevimlilar</h1>
      {loading && <p className="text-muted text-sm">Yuklanmoqda…</p>}
      {!loading && favorites.length === 0 && (
        <p className="text-muted text-sm">Sevimlilar bo'sh. Joylarni ⭐ belgilang!</p>
      )}
      <div className="space-y-3">
        {favorites.map((p) => (
          <PlaceCard key={p.id} place={p} />
        ))}
      </div>
    </div>
  );
}
