import { useEffect, useState } from 'react';
import type { User } from '@api';
import { api } from '../lib/api';
import { getWebApp } from '../lib/tg';

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch(() => undefined);
  }, []);

  if (!user) return <div className="p-6 text-center text-muted">Yuklanmoqda…</div>;

  const roleLabel: Record<string, string> = {
    guest: 'Mehmon', user: 'Foydalanuvchi', owner: 'Joy egasi',
    moderator: 'Moderator', admin: 'Admin',
  };

  return (
    <div className="p-4">
      <h1 className="font-heading text-xl font-bold mb-4">👤 Profil</h1>
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-pill bg-violet/20 flex items-center justify-center text-2xl">
            {(user.username || '?')[0].toUpperCase()}
          </div>
          <div>
            <p className="font-semibold">
              @{user.username || '—'}
            </p>
            <p className="text-muted text-sm">
              {user.first_name} {user.last_name}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
          <div className="bg-bg2 rounded-card p-3">
            <p className="text-muted text-xs">Rol</p>
            <p>{roleLabel[user.role] ?? user.role}</p>
          </div>
          <div className="bg-bg2 rounded-card p-3">
            <p className="text-muted text-xs">Til</p>
            <p>{user.language.toUpperCase()}</p>
          </div>
        </div>
      </div>
      <p className="text-muted text-xs mt-4 text-center">
        QuietSpace Tashkent v1.0 · {getWebApp() ? 'Telegram Mini App' : 'Web preview'}
      </p>
    </div>
  );
}