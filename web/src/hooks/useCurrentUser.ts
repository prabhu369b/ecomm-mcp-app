import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { callApi } from '@/utils/api';
import { useAuthStore } from '@/stores/authStore';

export interface CurrentUser {
  user_id: string;
  name: string;
  username: string;
  email: string;
  roles: string[];
  scops: string[];
}

const CURRENT_USER_KEY = ['currentUser'];

export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery({
    queryKey: CURRENT_USER_KEY,
    queryFn: () => callApi<CurrentUser>('/auth/me'),
    enabled: !!accessToken,
    staleTime: 5 * 60_000
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { name?: string; username?: string }) =>
      callApi<CurrentUser>('/auth/me', { method: 'PATCH', body: JSON.stringify(body) }),
    onSuccess: (data) => queryClient.setQueryData(CURRENT_USER_KEY, data)
  });
}
