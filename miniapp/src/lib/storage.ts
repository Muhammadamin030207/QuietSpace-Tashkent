import type { TokenStore } from '@api';

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

/**
 * JWT saqlash: Telegram WebView xavfsizligi uchun sessionStorage
 * (localStorage emas). Login ok bo'lsa user profil ham saqlanadi.
 */
export const tokenStore: TokenStore & { userJson?: string } = {
  get(): string | null {
    try {
      return sessionStorage.getItem('qs_access');
    } catch {
      return null;
    }
  },
  set(tokens: { access: string; refresh: string }): void {
    try {
      sessionStorage.setItem('qs_access', tokens.access);
      sessionStorage.setItem('qs_refresh', tokens.refresh);
    } catch {
      /* noop */
    }
  },
};

export function getRefresh(): string | null {
  try {
    return sessionStorage.getItem('qs_refresh');
  } catch {
    return null;
  }
}

export function clearSession(): void {
  try {
    sessionStorage.removeItem('qs_access');
    sessionStorage.removeItem('qs_refresh');
  } catch {
    /* noop */
  }
}

export function getApiBaseUrl(): string {
  return BACKEND_URL;
}
