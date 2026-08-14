import { Link, useLocation } from 'react-router-dom';

const items = [
  { to: '/', label: 'Xarita', icon: '🗺️' },
  { to: '/chat', label: 'AI', icon: '🤖' },
  { to: '/favorites', label: 'Sevimli', icon: '⭐' },
  { to: '/profile', label: 'Profil', icon: '👤' },
];

export default function BottomNav() {
  const { pathname } = useLocation();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card/95 backdrop-blur border-t border-border flex justify-around py-2 z-50">
      {items.map((it) => {
        const active =
          it.to === '/' ? pathname === '/' : pathname.startsWith(it.to);
        return (
          <Link
            key={it.to}
            to={it.to}
            className={`flex flex-col items-center text-[11px] gap-0.5 px-3 py-1 rounded-card ${
              active ? 'text-cyan' : 'text-muted'
            }`}
          >
            <span className="text-lg">{it.icon}</span>
            {it.label}
          </Link>
        );
      })}
    </nav>
  );
}