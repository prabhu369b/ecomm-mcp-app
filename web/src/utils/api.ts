import { env } from '@/config/env';
import { useAuthStore } from '@/stores/authStore';

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

interface RefreshResponse {
  access_token: string;
  refresh_token: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function isEnvelope(body: unknown): body is ApiEnvelope<unknown> {
  return !!body && typeof body === 'object' && 'success' in body && 'data' in body;
}

const NO_REFRESH_PATHS = ['/auth/refresh', '/auth/sign-in'];

let refreshInFlight: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = useAuthStore.getState().refreshToken;
  if (!refreshToken) return null;

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const res = await fetch(`${env.VITE_API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken })
        });
        if (!res.ok) {
          useAuthStore.getState().clear();
          return null;
        }
        const body = await res.json().catch(() => null);
        const data = (isEnvelope(body) ? body.data : body) as RefreshResponse;
        useAuthStore.getState().setSession({
          accessToken: data.access_token,
          refreshToken: data.refresh_token
        });
        return data.access_token;
      } catch {
        useAuthStore.getState().clear();
        return null;
      } finally {
        refreshInFlight = null;
      }
    })();
  }

  return refreshInFlight;
}

async function request(path: string, init: RequestInit | undefined, token: string | null): Promise<Response> {
  return fetch(`${env.VITE_API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(env.VITE_API_KEY && !token ? { Authorization: `Bearer ${env.VITE_API_KEY}` } : {}),
      ...init?.headers
    },
    ...init
  });
}

export async function callApi<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useAuthStore.getState().accessToken;

  let res = await request(path, init, token);

  if (res.status === 401 && token && !NO_REFRESH_PATHS.includes(path)) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      res = await request(path, init, newToken);
    }
  }

  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      (isEnvelope(body) && body.message) || `${res.status} ${res.statusText}`;
    throw new ApiError(message, res.status);
  }

  return (isEnvelope(body) ? body.data : body) as T;
}
