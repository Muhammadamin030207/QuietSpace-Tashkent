import { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import type { User } from '@api';
import BottomNav from './components/BottomNav';
import { ensureLogin, initTelegramUI } from './lib/tg';
import ChatPage from './pages/ChatPage';
import FavoritesPage from './pages/FavoritesPage';
import MapPage from './pages/MapPage';
import PlaceDetailPage from './pages/PlaceDetailPage';
import ProfilePage from './pages/ProfilePage';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    initTelegramUI();
    ensureLogin()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-bg">
        <div className="text-cyan animate-pulse font-heading text-lg">QuietSpace…</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-bg gap-4 px-8 text-center">
        <div className="text-3xl">🔒</div>
        <div className="text-muted">
          Kirish xatosi. Iltimos, bot orqali qayta oching yoki /start bosing.
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-bg">
      <div className="flex-1 overflow-y-auto pb-16">
        <Routes>
          <Route path="/" element={<MapPage />} />
          <Route path="/place/:id" element={<PlaceDetailPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <BottomNav />
    </div>
  );
}