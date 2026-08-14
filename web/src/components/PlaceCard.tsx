import type { Place } from '@api';
import { Link } from 'react-router-dom';

const NOISE: Record<string, string> = {
  very_quiet: '🤫', quiet: '😌', moderate: '🎵', noisy: '📢',
};

export function occupancyLabel(level?: string | null, stale?: boolean): string {
  if (!level || stale) return '— noma\'lum';
  if (level === 'empty') return '🟢 Bo\'sh';
  if (level === 'medium') return '🟡 O\'rtacha';
  return '🔴 To\'la';
}

export default function PlaceCard({ place }: { place: Place }) {
  return (
    <Link
      to={`/app/places/${place.id}`}
      className="card block hover:border-cyan/50 transition-colors"
    >
      <div className="flex gap-3">
        {place.photo ? (
          <img src={place.photo} alt={place.name} className="w-16 h-16 rounded-card object-cover bg-bg2 flex-shrink-0" />
        ) : (
          <div className="w-16 h-16 rounded-card bg-bg2 flex items-center justify-center text-2xl flex-shrink-0">
            {place.category.icon}
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-heading font-semibold truncate">{place.name}</h3>
            {place.is_verified && <span className="text-cyan text-xs">✓</span>}
          </div>
          <p className="text-muted text-xs">{place.district} · {place.category.name_uz}</p>
          <div className="flex items-center gap-2 mt-1 text-xs flex-wrap">
            <span className="text-warning">★ {Number(place.avg_rating).toFixed(1)}</span>
            <span>{NOISE[place.noise_level] ?? ''}</span>
            <span className="text-muted">{occupancyLabel(place.occupancy?.level, place.occupancy?.is_stale)}</span>
            {place.distance_km != null && <span className="text-muted">{place.distance_km} km</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}