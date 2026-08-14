import { createClient } from '@api';
import { getApiBaseUrl, tokenStore } from './storage';

export const api = createClient(getApiBaseUrl(), tokenStore);
