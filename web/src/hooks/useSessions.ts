import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { callApi } from '@/utils/api';

export interface Session {
  session_id: string;
  device: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  last_used_at: string;
  current: boolean;
}

const SESSIONS_KEY = ['sessions'];

export function useSessions() {
  return useQuery({
    queryKey: SESSIONS_KEY,
    queryFn: () => callApi<Session[]>('/auth/sessions')
  });
}

export function useRevokeSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) =>
      callApi<void>(`/auth/sessions/${sessionId}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SESSIONS_KEY })
  });
}

export function useRevokeAllSessions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (keepCurrent: boolean) =>
      callApi<{ revoked: number }>(`/auth/sessions?keep_current=${keepCurrent}`, {
        method: 'DELETE'
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SESSIONS_KEY })
  });
}
