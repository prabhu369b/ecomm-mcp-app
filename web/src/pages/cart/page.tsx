import { useEffect } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useCart, useUpdateCartItem, useRemoveCartItem } from '@/hooks/useCart';
import { useAuthStore } from '@/stores/authStore';

export const Route = createFileRoute('/cart/')({
  component: CartPage
});

function CartPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const { data, isLoading, isError } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();

  useEffect(() => {
    if (!accessToken) {
      window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
    }
  }, [accessToken]);

  if (!accessToken) return null;

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 text-xl font-semibold tracking-tight">Your cart</h1>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {isError && <p className="text-sm text-destructive">Failed to load cart.</p>}

      {data && data.items.length === 0 && (
        <p className="text-sm text-muted-foreground">Your cart is empty.</p>
      )}

      {data && data.items.length > 0 && (
        <>
          <Card className="border-border/70">
            <CardContent className="flex flex-col divide-y divide-border">
              {data.items.map((item) => (
                <div key={item.product_id} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{item.name}</p>
                    <p className="text-xs text-muted-foreground">${item.price} each</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="icon-sm"
                      variant="outline"
                      disabled={updateItem.isPending}
                      onClick={() =>
                        updateItem.mutate({ productId: item.product_id, qty: item.qty - 1 })
                      }
                    >
                      −
                    </Button>
                    <span className="w-6 text-center text-sm">{item.qty}</span>
                    <Button
                      size="icon-sm"
                      variant="outline"
                      disabled={updateItem.isPending}
                      onClick={() =>
                        updateItem.mutate({ productId: item.product_id, qty: item.qty + 1 })
                      }
                    >
                      +
                    </Button>
                  </div>
                  <p className="w-16 text-right text-sm font-semibold text-foreground">
                    ${item.subtotal}
                  </p>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    disabled={removeItem.isPending}
                    onClick={() => removeItem.mutate(item.product_id)}
                    aria-label="Remove item"
                  >
                    ×
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="mt-6 flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Total</span>
            <span className="text-lg font-semibold text-foreground">${data.total}</span>
          </div>

          <Button className="mt-4 w-full" size="lg" disabled title="Checkout coming soon">
            Checkout
          </Button>
        </>
      )}
    </main>
  );
}
