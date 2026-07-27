import { env } from '@/config/env';
import { useAuthStore } from '@/stores/authStore';

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
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

export async function callApi<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useAuthStore.getState().accessToken;

  const res = await fetch(`${env.VITE_API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(env.VITE_API_KEY && !token ? { Authorization: `Bearer ${env.VITE_API_KEY}` } : {}),
      ...init?.headers
    },
    ...init
  });

  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      (isEnvelope(body) && body.message) || `${res.status} ${res.statusText}`;
    throw new ApiError(message, res.status);
  }

  return (isEnvelope(body) ? body.data : body) as T;
}
