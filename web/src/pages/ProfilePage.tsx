import { useEffect, useState } from 'react';
import type { User } from '@api';
import { api, clearSession } from '../lib/api';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [favorites, setFavorites] = useState<{ id: number; place: { id: number; name: string; district: string; avg_rating: number } }[]>([]);

  useEffect(() => {
    api.me().then(setUser).catch(() => undefined);
    api.favorites().then(setFavorites).catch(() => undefined);
  }, []);

  if (!user) return <div className="max-w-3xl mx-auto px-4 py-16 text-center text-muted">Yuklanmoqda…</div>;

  const logout = () => {
    clearSession();
    navigate('/');
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="font-heading text-2xl font-bold">👤 Profil</h1>
      <div className="card mt-6">
        <p className="font-semibold text-lg">@{user.username}</p>
        <p className="text-muted text-sm">{user.first_name} {user.last_name}</p>
        {user.phone && <p className="text-muted text-sm mt-1">📱 {user.phone}</p>}
        <div className="flex gap-3 mt-4">
          <button onClick={logout} className="btn-ghost">Chiqish</button>
        </div>
      </div>

      <h2 className="font-heading text-xl font-semibold mt-8 mb-3">⭐ Sevimlilar ({favorites.length})</h2>
      <div className="space-y-2">
        {favorites.map((f) => (
          <a key={f.id} href={`#/app/places/${f.place.id}`} className="card block !p-3 hover:border-cyan/50">
            {f.place.name} <span className="text-muted text-sm">· {f.place.district} · ★ {Number(f.place.avg_rating).toFixed(1)}</span>
          </a>
        ))}
        {favorites.length === 0 && <p className="text-muted text-sm">Sevimlilar bo'sh.</p>}
      </div>
    </div>
  );
}
