export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  language_code?: string;
}

export interface User {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  telegram_id?: number | null;
  telegram_username?: string;
  language: 'uz' | 'ru' | 'en';
  role: string;
}

export interface Category {
  key: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  icon: string;
}

export interface Place {
  id: number;
  name: string;
  category: Category;
  photo?: string | null;
  district: string;
  address: string;
  lat: number;
  lng: number;
  wifi_speed: 'none' | 'slow' | 'medium' | 'fast';
  noise_level: 'very_quiet' | 'quiet' | 'moderate' | 'noisy';
  price_level: 'free' | '$' | '$$' | '$$$';
  outlets_level: 'none' | 'few' | 'every_table';
  avg_rating: number;
  is_verified: boolean;
  distance_km?: number | null;
  occupancy?: { level: 'empty' | 'medium' | 'full' | null; is_stale: boolean; reported_at?: string } | null;
  description?: string;
  working_hours?: Record<string, string>;
  amenities?: string[];
  photos?: { id: number; image: string }[];
  reviews?: Review[];
  is_favorite?: boolean;
}

export interface Review {
  id: number;
  place: number;
  user_id: number;
  username: string;
  rating: number;
  wifi_rating?: number | null;
  noise_rating?: number | null;
  comfort_rating?: number | null;
  text: string;
  ai_flagged: boolean;
  ai_summary_tag: string;
  created_at: string;
}

export interface AIResult {
  reply: string;
  place_ids: number[];
  places: AIPlace[];
  conversation_id?: string | null;
}

export interface AIPlace {
  id: number;
  name: string;
  category: string;
  district: string;
  address: string;
  wifi?: string;
  noise?: string;
  outlets?: string;
  price?: string;
  rating: number;
  is_favorite?: boolean;
  photo?: string | null;
  reason?: string;
}

export interface Stats {
  places_count: number;
  reviews_count: number;
  categories: Category[];
  districts: string[];
}

export type TokenStore = {
  get(): string | null;
  set(tokens: { access: string; refresh: string }): void;
};

export class APIClient {
  private baseUrl: string;
  private tokens: TokenStore;

  constructor(baseUrl: string, tokens: TokenStore) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.tokens = tokens;
  }

  private async request<T>(path: string, options: RequestInit = {}, auth = true): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };
    if (auth) {
      const token = this.tokens.get();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${this.baseUrl}${path}`, { ...options, headers });

    if (res.status === 401 && auth) {
      const token = this.tokens.get();
      if (token) {
        try {
          const refresh = localStorage.getItem('qs_refresh');
          if (refresh) {
            const r = await fetch(`${this.baseUrl}/api/auth/token/refresh/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh }),
            });
            if (r.ok) {
              const data = await r.json();
              this.tokens.set(data);
              return this.request<T>(path, options, auth);
            }
          }
        } catch {
          /* fallthrough */
        }
      }
    }
    if (!res.ok) {
      const body = await res.text();
      throw new Error(body || `HTTP ${res.status}`);
    }
    return res.json() as Promise<T>;
  }

  // ---- Auth ----
  telegramAuth(initData: string): Promise<{ access: string; refresh: string; user: User }> {
    return this.request('/api/auth/telegram/', {
      method: 'POST',
      body: JSON.stringify({ init_data: initData }),
    }, false);
  }

  telegramIdAuth(telegram_id: number, username = ''): Promise<{ access: string; refresh: string; user: User }> {
    return this.request('/api/auth/telegram-id/', {
      method: 'POST',
      body: JSON.stringify({ telegram_id, username }),
    }, false);
  }

  register(data: Record<string, string>): Promise<{ access: string; refresh: string; user: User }> {
    return this.request('/api/auth/register/', { method: 'POST', body: JSON.stringify(data) }, false);
  }

  login(username: string, password: string): Promise<{ access: string; refresh: string; user: User }> {
    return this.request('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }, false);
  }

  me(): Promise<User> {
    return this.request('/api/auth/me/');
  }

  updateMe(data: Partial<User>): Promise<User> {
    return this.request('/api/auth/me/', { method: 'PATCH', body: JSON.stringify(data) });
  }

  // ---- Places ----
  listPlaces(params: Record<string, string | number> = {}): Promise<{ count: number; results: Place[] }> {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/places/${qs ? `?${qs}` : ''}`);
  }

  nearby(lat: number, lng: number, radiusKm = 5): Promise<{ count: number; results: Place[] }> {
    return this.request(`/api/places/nearby/?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`);
  }

  placeDetail(id: number): Promise<Place> {
    return this.request(`/api/places/${id}/`);
  }

  aiSummary(id: number): Promise<{ summary?: string; status: string }> {
    return this.request(`/api/places/${id}/ai-summary/`);
  }

  postReview(id: number, body: { rating: number; text?: string }): Promise<Review> {
    return this.request(`/api/places/${id}/reviews/`, { method: 'POST', body: JSON.stringify(body) });
  }

  postOccupancy(id: number, level: 'empty' | 'medium' | 'full'): Promise<unknown> {
    return this.request(`/api/places/${id}/occupancy/`, { method: 'POST', body: JSON.stringify({ level }) });
  }

  // ---- Favorites ----
  favorites(): Promise<{ id: number; place: Place }[]> {
    return this.request('/api/favorites/');
  }

  addFavorite(placeId: number): Promise<unknown> {
    return this.request('/api/favorites/', { method: 'POST', body: JSON.stringify({ place_id: placeId }) });
  }

  removeFavorite(placeId: number): Promise<unknown> {
    return this.request(`/api/favorites/${placeId}/`, { method: 'DELETE' });
  }

  // ---- AI ----
  aiChat(message: string, opts: { userLat?: number; userLng?: number; channel?: string; conversationId?: string } = {}): Promise<AIResult> {
    return this.request('/api/ai/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_lat: opts.userLat,
        user_lng: opts.userLng,
        channel: opts.channel || 'miniapp',
        conversation_id: opts.conversationId,
      }),
    });
  }

  aiRecommend(opts: { userLat?: number; userLng?: number } = {}): Promise<{ places: AIPlace[] }> {
    return this.request('/api/ai/recommend/', {
      method: 'POST',
      body: JSON.stringify(opts),
    });
  }

  // ---- Stats ----
  stats(): Promise<Stats> {
    return this.request('/api/stats/');
  }
}

export function createClient(baseUrl: string, tokenStore: TokenStore): APIClient {
  return new APIClient(baseUrl, tokenStore);
}
