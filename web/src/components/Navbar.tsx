import { Link, NavLink } from 'react-router-dom';
import { isAuthed } from '../lib/api';

export default function Navbar() {
  const authed = isAuthed();
  return (
    <header className="sticky top-0 z-50 bg-bg/90 backdrop-blur border-b border-border">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="font-heading font-bold text-xl tracking-tight">
          <span className="text-cyan">Quiet</span>
          <span className="text-violet">Space</span>
          <span className="text-muted text-sm ml-2 hidden sm:inline">Tashkent</span>
        </Link>
        <nav className="flex items-center gap-1 sm:gap-4 text-sm">
          <NavLink to="/" className={({ isActive }) => `px-3 py-2 rounded-pill hover:text-cyan ${isActive ? 'text-cyan' : 'text-muted'}`}>
            Bosh sahifa
          </NavLink>
          <NavLink to="/app" className={({ isActive }) => `px-3 py-2 rounded-pill hover:text-cyan ${isActive ? 'text-cyan' : 'text-muted'}`}>
            🗺 Xarita
          </NavLink>
          <NavLink to="/business" className={({ isActive }) => `px-3 py-2 rounded-pill hover:text-cyan ${isActive ? 'text-cyan' : 'text-muted'}`}>
            Biznes
          </NavLink>
          <NavLink to="/blog" className={({ isActive }) => `px-3 py-2 rounded-pill hover:text-cyan ${isActive ? 'text-cyan' : 'text-muted'}`}>
            Blog
          </NavLink>
          {authed ? (
            <NavLink to="/app/profile" className="btn-ghost !py-1.5">
              Profil
            </NavLink>
          ) : (
            <NavLink to="/login" className="btn-primary !py-1.5">
              Kirish
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}
