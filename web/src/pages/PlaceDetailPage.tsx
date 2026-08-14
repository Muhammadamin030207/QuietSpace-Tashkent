import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import type { Place, Review } from '@api';
import { api, isAuthed } from '../lib/api';
import { useNavigate } from 'react-router-dom';

const NOISE_LABEL: Record<string, string> = {
  very_quiet: '🤫 Juda tinch', quiet: '😌 Tinch', moderate: '🎵 O\'rtacha', noisy: '📢 Shovqinli',
};
const WIFI_LABEL: Record<string, string> = {
  none: 'Yo\'q', slow: '🐢 Sekin', medium: 'O\'rtacha', fast: '⚡ Tez',
};
const OUTLET_LABEL: Record<string, string> = {
  none: 'Yo\'q', few: '🔌 Kam', every_table: '🔌 Har stolda',
};

function ratingDistribution(reviews: Review[]) {
  const buckets = [0, 0, 0, 0, 0];
  reviews.forEach((r) => {
    if (r.rating >= 1 && r.rating <= 5) buckets[r.rating - 1]++;
  });
  const max = Math.max(1, ...buckets);
  return { buckets, max };
}

export default function PlaceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [place, setPlace] = useState<Place | null>(null);
  const [summary, setSummary] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [reviewRating, setReviewRating] = useState(0);
  const [favorite, setFavorite] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);

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
    load().catch(() => navigate('/app'));
  }, [load, navigate]);

  if (!place) {
    return <div className="max-w-3xl mx-auto px-4 py-16 text-muted text-center">Yuklanmoqda…</div>;
  }

  const { buckets, max } = ratingDistribution(reviews);

  const toggleFavorite = async () => {
    if (favorite) {
      await api.removeFavorite(place.id);
      setFavorite(false);
    } else {
      await api.addFavorite(place.id);
      setFavorite(true);
    }
  };

  const submitReview = async () => {
    if (reviewRating === 0) return;
    await api.postReview(place.id, { rating: reviewRating, text: reviewText });
    setReviewText('');
    setReviewRating(0);
    load();
  };

  const report = async (level: 'empty' | 'medium' | 'full') => {
    await api.postOccupancy(place.id, level);
  };

  const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}`;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex gap-6 flex-col sm:flex-row">
        <div className="sm:w-1/2">
          {place.photo ? (
            <img src={place.photo} alt={place.name} className="w-full h-64 object-cover rounded-card" />
          ) : (
            <div className="w-full h-64 rounded-card bg-bg2 flex items-center justify-center text-6xl">
              {place.category.icon}
            </div>
          )}
        </div>
        <div className="sm:w-1/2">
          <div className="flex items-center gap-2">
            <h1 className="font-heading text-2xl font-bold">{place.name}</h1>
            {place.is_verified && <span className="text-cyan">✓</span>}
          </div>
          <p className="text-muted mt-1">{place.category.name_uz} · {place.district}</p>
          <p className="text-muted text-sm mt-1">{place.address}</p>
          <p className="text-warning text-lg mt-3">★ {Number(place.avg_rating).toFixed(2)}</p>

          <div className="grid grid-cols-2 gap-2 mt-4">
            <div className="card !p-3"><p className="text-muted text-xs">Wi-Fi</p><p>{WIFI_LABEL[place.wifi_speed]}</p></div>
            <div className="card !p-3"><p className="text-muted text-xs">Shovqin</p><p>{NOISE_LABEL[place.noise_level]}</p></div>
            <div className="card !p-3"><p className="text-muted text-xs">Rozetka</p><p>{OUTLET_LABEL[place.outlets_level]}</p></div>
            <div className="card !p-3"><p className="text-muted text-xs">Narx</p><p>{place.price_level === 'free' ? '🆓 Bepul' : place.price_level}</p></div>
          </div>

          <div className="flex gap-3 mt-5 flex-wrap">
            <a href={directionsUrl} target="_blank" rel="noreferrer" className="btn-primary">🧭 Yo'nalish</a>
            <button onClick={toggleFavorite} className="btn-ghost">{favorite ? '⭐ Sevimlilarda' : '☆ Sevimli'}</button>
          </div>
          <div className="flex gap-2 mt-3 flex-wrap">
            {([['empty', '🟢 Bo\'sh'], ['medium', '🟡 O\'rtacha'], ['full', '🔴 To\'la']] as const).map(([lvl, label]) => (
              <button key={lvl} onClick={() => report(lvl)} className="chip hover:!border-cyan">{label} — men shu yerdaman</button>
            ))}
          </div>
        </div>
      </div>

      {place.description && <p className="text-muted mt-6">{place.description}</p>}

      {summary && (
        <div className="card mt-6 border-cyan/30">
          <p className="text-xs text-cyan uppercase tracking-wide mb-1">✨ AI xulosa</p>
          <p className="text-sm">{summary}</p>
        </div>
      )}

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="card">
          <h3 className="font-heading font-semibold mb-3">Reyting taqsimoti</h3>
          {[5, 4, 3, 2, 1].map((star) => {
            const count = buckets[star - 1];
            return (
              <div key={star} className="flex items-center gap-2 text-sm mb-1.5">
                <span className="w-8 text-muted">{star}★</span>
                <div className="flex-1 h-2 bg-bg2 rounded-pill overflow-hidden">
                  <div className="h-full bg-cyan rounded-pill" style={{ width: `${(count / max) * 100}%` }} />
                </div>
                <span className="w-6 text-right text-muted text-xs">{count}</span>
              </div>
            );
          })}
        </div>

        <div className="card">
          <h3 className="font-heading font-semibold mb-3">📝 Sharh qoldirish</h3>
          {isAuthed() ? (
            <>
              <div className="flex gap-1 mb-3">
                {[1, 2, 3, 4, 5].map((r) => (
                  <button key={r} onClick={() => setReviewRating(r)} className={`text-2xl ${r <= reviewRating ? '' : 'opacity-30'}`}>⭐</button>
                ))}
              </div>
              <textarea value={reviewText} onChange={(e) => setReviewText(e.target.value)} placeholder="Fikringiz…" rows={3} className="input" />
              <button onClick={submitReview} disabled={reviewRating === 0} className="btn-primary w-full mt-3">Yuborish</button>
            </>
          ) : (
            <p className="text-muted text-sm">
              Sharh qoldirish uchun <a href="#/login" className="text-cyan">kiring</a>.
            </p>
          )}
        </div>
      </div>

      <div className="mt-8">
        <h3 className="font-heading text-lg font-semibold mb-3">Sharhlar ({reviews.length})</h3>
        {reviews.map((r) => (
          <div key={r.id} className="card !p-3 mb-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">@{r.username}</span>
              <span className="text-warning text-xs">★ {r.rating}</span>
            </div>
            {r.text && <p className="text-sm text-muted mt-1">{r.text}</p>}
            {r.ai_summary_tag && <span className="chip !text-[10px] mt-2 inline-block">✨ {r.ai_summary_tag}</span>}
          </div>
        ))}
        {reviews.length === 0 && <p className="text-muted text-sm">Hali sharhlar yo'q.</p>}
      </div>
    </div>
  );
}
