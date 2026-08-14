import type { Place } from '@api';
import { Link } from 'react-router-dom';

const CATEGORY_ICON: Record<string, string> = {
  cafe: '☕',
  library: '📚',
  coworking: '💼',
  free_zone: '🆓',
};

const CATEGORY_COLOR: Record<string, string> = {
  coworking: '#8B5CF6',
  library: '#18E5F0',
  cafe: '#F5B841',
  free_zone: '#39FF88',
};

const NOISE: Record<string, string> = {
  very_quiet: '🤫',
  quiet: '😌',
  moderate: '🎵',
  noisy: '📢',
};

export function categoryIcon(key: string): string {
  return CATEGORY_ICON[key] ?? '📍';
}

export function categoryColor(key: string): string {
  return CATEGORY_COLOR[key] ?? '#8891A8';
}

export function occupancyLabel(level?: string | null, stale?: boolean): string {
  if (!level || stale) return '—';
  if (level === 'empty') return '🟢 Bo\'sh';
  if (level === 'medium') return '🟡 O\'rtacha';
  return '🔴 To\'la';
}

export default function PlaceCard({ place }: { place: Place }) {
  return (
    <Link
      to={`/place/${place.id}`}
      className="card block w-full hover:border-cyan/60 transition-colors"
    >
      <div className="flex gap-3">
        {place.photo ? (
          <img
            src={place.photo}
            alt={place.name}
            className="w-20 h-20 rounded-card object-cover flex-shrink-0 bg-bg2"
          />
        ) : (
          <div
            className="w-20 h-20 rounded-card flex items-center justify-center text-3xl flex-shrink-0"
            style={{ backgroundColor: `${categoryColor(place.category.key)}22` }}
          >
            {categoryIcon(place.category.key)}
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-heading font-semibold truncate">{place.name}</h3>
            {place.is_verified && <span className="text-cyan text-xs">✓</span>}
          </div>
          <p className="text-muted text-xs truncate">
            {place.district} · {place.category.name_uz}
          </p>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <span className="text-warning text-xs">★ {Number(place.avg_rating).toFixed(1)}</span>
            <span className="text-xs">{NOISE[place.noise_level] ?? ''}</span>
            <span className="text-xs">⚡{place.wifi_speed === 'fast' ? ' tez' : ''}</span>
            {place.distance_km != null && (
              <span className="text-xs text-muted">{place.distance_km} km</span>
            )}
          </div>
          <div className="mt-1 text-xs">
            {occupancyLabel(place.occupancy?.level, place.occupancy?.is_stale)}
          </div>
        </div>
      </div>
    </Link>
  );
}
