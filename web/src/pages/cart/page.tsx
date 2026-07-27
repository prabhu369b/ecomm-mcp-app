import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { HugeiconsIcon } from '@hugeicons/react';
import { MinusSignIcon, PlusSignIcon, Delete02Icon, ShoppingCart01Icon } from '@hugeicons/core-free-icons';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useCart, useUpdateCartItem, useRemoveCartItem } from '@/hooks/useCart';
import { useCheckout } from '@/hooks/useOrders';
import { useAuthStore } from '@/stores/authStore';
import { ApiError } from '@/utils/api';

export const Route = createFileRoute('/cart/')({
  component: CartPage
});

function CartPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const { data, isLoading, isError } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();
  const checkout = useCheckout();
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) {
      window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
    }
  }, [accessToken]);

  if (!accessToken) return null;

  async function handleCheckout() {
    setCheckoutError(null);
    try {
      const order = await checkout.mutateAsync();
      window.location.assign(`/app/orders?placed=${order.id}`);
    } catch (err) {
      setCheckoutError(err instanceof ApiError ? err.message : 'Checkout failed');
    }
  }

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 flex items-center gap-2 text-xl font-semibold tracking-tight">
        <HugeiconsIcon icon={ShoppingCart01Icon} size={20} />
        Your cart
      </h1>

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
                      <HugeiconsIcon icon={MinusSignIcon} size={12} />
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
                      <HugeiconsIcon icon={PlusSignIcon} size={12} />
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
                    <HugeiconsIcon icon={Delete02Icon} size={14} />
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="mt-6 flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Total</span>
            <span className="text-lg font-semibold text-foreground">${data.total}</span>
          </div>

          {checkoutError && (
            <p className="mt-2 text-xs text-destructive">{checkoutError}</p>
          )}

          <Button
            className="mt-4 w-full"
            size="lg"
            disabled={checkout.isPending}
            onClick={handleCheckout}
          >
            {checkout.isPending ? 'Placing order…' : 'Checkout'}
          </Button>
        </>
      )}
    </main>
  );
}
