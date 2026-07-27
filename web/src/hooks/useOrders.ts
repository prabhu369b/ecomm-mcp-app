import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { callApi } from '@/utils/api';

export interface OrderItem {
  product_id: string;
  name: string;
  price: number;
  qty: number;
}

export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';

export interface Order {
  id: string;
  items: OrderItem[];
  total: number;
  status: OrderStatus;
  created_at: string;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

export function useOrders(page: number) {
  return useQuery({
    queryKey: ['orders', page],
    queryFn: () => callApi<OrderListResponse>(`/orders?page=${page}&page_size=20`)
  });
}

export function useCheckout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => callApi<Order>('/orders/checkout', { method: 'POST' }),
    onSuccess: () => {
      queryClient.setQueryData(['cart'], { items: [], total: 0 });
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    }
  });
}
