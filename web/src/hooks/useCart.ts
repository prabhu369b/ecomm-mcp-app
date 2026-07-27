import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { callApi } from '@/utils/api';

export interface CartItem {
  product_id: string;
  name: string;
  price: number;
  qty: number;
  subtotal: number;
}

export interface CartResponse {
  items: CartItem[];
  total: number;
}

const CART_KEY = ['cart'];

export function useCart() {
  return useQuery({
    queryKey: CART_KEY,
    queryFn: () => callApi<CartResponse>('/cart')
  });
}

export function useAddToCart() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, qty }: { productId: string; qty: number }) =>
      callApi<CartResponse>('/cart/items', {
        method: 'POST',
        body: JSON.stringify({ product_id: productId, qty })
      }),
    onSuccess: (data) => queryClient.setQueryData(CART_KEY, data)
  });
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, qty }: { productId: string; qty: number }) =>
      callApi<CartResponse>(`/cart/items/${productId}`, {
        method: 'PATCH',
        body: JSON.stringify({ product_id: productId, qty })
      }),
    onSuccess: (data) => queryClient.setQueryData(CART_KEY, data)
  });
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (productId: string) =>
      callApi<CartResponse>(`/cart/items/${productId}`, { method: 'DELETE' }),
    onSuccess: (data) => queryClient.setQueryData(CART_KEY, data)
  });
}
