import type { TelegramUser, User } from '@api';
import { api } from './api';
import { clearSession, tokenStore } from './storage';

type WebApp = {
  initData: string;
  initDataUnsafe: { user?: TelegramUser };
  ready: () => void;
  expand: () => void;
  setHeaderColor: (color: string) => void;
  setBackgroundColor: (color: string) => void;
  MainButton: { show: () => void; hide: () => void; setText: (t: string) => void; onClick: (fn: () => void) => void; offClick: (fn: () => void) => void };
  themeParams?: Record<string, string>;
  colorScheme?: 'light' | 'dark';
  openTelegramLink?: (url: string) => void;
};

declare global {
  interface Window {
    Telegram?: { WebApp?: WebApp };
  }
}

export function getWebApp(): WebApp | null {
  return window.Telegram?.WebApp ?? null;
}

export function initTelegramUI(): void {
  const tg = getWebApp();
  if (!tg) return;
  tg.ready();
  tg.expand();
  // Dark cyberpunk palitra — Telegram rejimidan qat'i nazar majburiy
  tg.setHeaderColor('#0B0F1A');
  tg.setBackgroundColor('#0B0F1A');
}

export function isTelegramContext(): boolean {
  return Boolean(getWebApp()?.initData);
}

/**
 * Asosiy auth oqimi:
 *  1. Telegram WebView ichida -> initData /api/auth/telegram/ ga yuboriladi
 *  2. Brauzer dev rejimida -> demo telegram id bilan /api/auth/telegram-id/
 */
export async function login(): Promise<User> {
  const tg = getWebApp();

  if (tg?.initData) {
    const result = await api.telegramAuth(tg.initData);
    tokenStore.set(result);
    return result.user;
  }

  // Dev fallback (Telegram emas)
  const devId = Number(import.meta.env.VITE_DEV_TG_ID || '111111');
  const result = await api.telegramIdAuth(devId, 'dev_user');
  tokenStore.set(result);
  return result.user;
}

export async function ensureLogin(): Promise<User | null> {
  if (tokenStore.get()) {
    try {
      return await api.me();
    } catch {
      clearSession();
    }
  }
  try {
    return await login();
  } catch (err) {
    console.error('login failed', err);
    return null;
  }
}

export function getUserLanguage(): 'uz' | 'ru' | 'en' {
  const lang = getWebApp()?.initDataUnsafe?.user?.language_code;
  if (lang === 'ru') return 'ru';
  if (lang === 'en') return 'en';
  return 'uz';
}
