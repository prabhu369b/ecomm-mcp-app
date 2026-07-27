import { useQuery } from '@tanstack/react-query';
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

export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => callApi<CurrentUser>('/auth/me'),
    enabled: !!accessToken,
    staleTime: 5 * 60_000
  });
}
