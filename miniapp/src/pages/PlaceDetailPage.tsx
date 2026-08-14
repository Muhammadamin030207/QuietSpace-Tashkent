import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import type { Place, Review } from '@api';
import { api } from '../lib/api';
import { categoryIcon } from '../components/PlaceCard';
import { getWebApp } from '../lib/tg';

const NOISE_LABEL: Record<string, string> = {
  very_quiet: '🤫 Juda tinch',
  quiet: '😌 Tinch',
  moderate: '🎵 O\'rtacha',
  noisy: '📢 Shovqinli',
};
const WIFI_LABEL: Record<string, string> = {
  none: 'Yo\'q', slow: '🐢 Sekin', medium: 'O\'rtacha', fast: '⚡ Tez',
};
const OUTLET_LABEL: Record<string, string> = {
  none: 'Yo\'q', few: '🔌 Kam', every_table: '🔌 Har stolda',
};

export default function PlaceDetailPage() {
  const { id } = useParams();
  const [place, setPlace] = useState<Place | null>(null);
  const [summary, setSummary] = useState<string>('');
  const [reviewText, setReviewText] = useState('');
  const [reviewRating, setReviewRating] = useState(0);
  const [favorite, setFavorite] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    const data = await api.placeDetail(Number(id));
    setPlace(data);
    setFavorite(Boolean(data.is_favorite));
    setReviews(data.reviews ?? []);
    api
      .aiSummary(Number(id))
      .then((s) => s.summary && setSummary(s.summary))
      .catch(() => undefined);
  }, [id]);

  useEffect(() => {
    load().catch(() => undefined);
  }, [load]);

  const reportHere = async () => {
    if (!place) return;
    setBusy(true);
    await api.postOccupancy(place.id, 'medium');
    setBusy(false);
  };

  const toggleFavorite = async () => {
    if (!place) return;
    if (favorite) {
      await api.removeFavorite(place.id);
      setFavorite(false);
    } else {
      await api.addFavorite(place.id);
      setFavorite(true);
    }
  };

  const submitReview = async () => {
    if (!place || reviewRating === 0) return;
    await api.postReview(place.id, { rating: reviewRating, text: reviewText });
    setReviewText('');
    setReviewRating(0);
    load();
  };

  const openDirections = () => {
    if (!place) return;
    const url = `https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}`;
    const tg = getWebApp();
    if (tg?.openTelegramLink) tg.openTelegramLink(url);
    else window.open(url, '_blank');
  };

  const openReviewComposer = useCallback(() => {
    const tg = getWebApp();
    if (tg?.MainButton) {
      tg.MainButton.setText('Yo\'nalish olish');
      tg.MainButton.onClick(openDirections);
      tg.MainButton.show();
    }
  }, []);

  useEffect(() => {
    if (place) openReviewComposer();
  }, [place, openReviewComposer]);

  if (!place) {
    return <div className="p-6 text-muted text-center">Yuklanmoqda…</div>;
  }

  return (
    <div className="p-4 pb-8">
      <div className="relative">
        {place.photo ? (
          <img src={place.photo} alt={place.name} className="w-full h-48 object-cover rounded-card" />
        ) : (
          <div className="w-full h-48 rounded-card bg-bg2 flex items-center justify-center text-6xl">
            {categoryIcon(place.category.key)}
          </div>
        )}
        <button
          onClick={toggleFavorite}
          className="absolute top-3 right-3 bg-bg/80 backdrop-blur rounded-pill p-2.5 text-lg"
        >
          {favorite ? '⭐' : '☆'}
        </button>
      </div>

      <div className="mt-4">
        <div className="flex items-center gap-2">
          <h1 className="font-heading text-2xl font-bold">{place.name}</h1>
          {place.is_verified && <span className="text-cyan text-sm">✓</span>}
        </div>
        <p className="text-muted text-sm mt-1">
          {place.category.icon} {place.category.name_uz} · {place.district}
        </p>
        <p className="text-muted text-xs mt-0.5">{place.address}</p>
        <p className="text-warning text-sm mt-2">★ {Number(place.avg_rating).toFixed(2)}</p>
      </div>

      <div className="grid grid-cols-2 gap-2 mt-4">
        <div className="card !p-3">
          <p className="text-muted text-xs">Wi-Fi</p>
          <p className="text-sm">{WIFI_LABEL[place.wifi_speed]}</p>
        </div>
        <div className="card !p-3">
          <p className="text-muted text-xs">Shovqin</p>
          <p className="text-sm">{NOISE_LABEL[place.noise_level]}</p>
        </div>
        <div className="card !p-3">
          <p className="text-muted text-xs">Rozetka</p>
          <p className="text-sm">{OUTLET_LABEL[place.outlets_level]}</p>
        </div>
        <div className="card !p-3">
          <p className="text-muted text-xs">Narx</p>
          <p className="text-sm">{place.price_level === 'free' ? '🆓 Bepul' : place.price_level}</p>
        </div>
      </div>

      {place.description && <p className="text-sm text-muted mt-4">{place.description}</p>}

      {summary && (
        <div className="card mt-4 border-cyan/30">
          <p className="text-xs text-cyan uppercase tracking-wide mb-1">✨ AI xulosa</p>
          <p className="text-sm">{summary}</p>
        </div>
      )}

      <div className="flex gap-3 mt-5">
        <button onClick={reportHere} className="btn-ghost flex-1" disabled={busy}>
          ✅ Men shu yerdaman
        </button>
        <button onClick={openDirections} className="btn-primary flex-1">
          🧭 Yo'nalish
        </button>
      </div>

      <div className="card mt-5">
        <h3 className="font-heading font-semibold mb-3">📝 Sharh qoldirish</h3>
        <div className="flex gap-1.5 mb-3">
          {[1, 2, 3, 4, 5].map((r) => (
            <button
              key={r}
              onClick={() => setReviewRating(r)}
              className={`text-2xl ${r <= reviewRating ? '' : 'opacity-30'}`}
            >
              ⭐
            </button>
          ))}
        </div>
        <textarea
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          placeholder="Joy haqida fikringiz…"
          rows={3}
          className="input !rounded-card"
        />
        <button onClick={submitReview} className="btn-primary w-full mt-3" disabled={reviewRating === 0}>
          Yuborish
        </button>
      </div>

      <div className="mt-5">
        <h3 className="font-heading font-semibold mb-3">Sharhlar ({reviews.length})</h3>
        {reviews.map((r) => (
          <div key={r.id} className="card !p-3 mb-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">@{r.username}</span>
              <span className="text-warning text-xs">★ {r.rating}</span>
            </div>
            {r.text && <p className="text-sm text-muted mt-1">{r.text}</p>}
            {r.ai_summary_tag && (
              <span className="chip !text-[10px] mt-2 inline-block">✨ {r.ai_summary_tag}</span>
            )}
          </div>
        ))}
        {reviews.length === 0 && <p className="text-muted text-sm">Hali sharhlar yo'q.</p>}
      </div>
    </div>
  );
}
