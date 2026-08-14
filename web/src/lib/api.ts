import { createClient, type TokenStore } from '@api';

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const tokenStore: TokenStore = {
  get(): string | null {
    try {
      return localStorage.getItem('qs_access');
    } catch {
      return null;
    }
  },
  set(tokens: { access: string; refresh: string }): void {
    try {
      localStorage.setItem('qs_access', tokens.access);
      localStorage.setItem('qs_refresh', tokens.refresh);
    } catch {
      /* noop */
    }
  },
};

export function getRefresh(): string | null {
  try {
    return localStorage.getItem('qs_refresh');
  } catch {
    return null;
  }
}

export function clearSession(): void {
  try {
    localStorage.removeItem('qs_access');
    localStorage.removeItem('qs_refresh');
  } catch {
    /* noop */
  }
}

export const api = createClient(BACKEND_URL, tokenStore);

export function isAuthed(): boolean {
  return Boolean(tokenStore.get());
}
