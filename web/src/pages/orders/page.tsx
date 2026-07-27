import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { HugeiconsIcon } from '@hugeicons/react';
import { Package01Icon } from '@hugeicons/core-free-icons';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useOrders, type OrderStatus } from '@/hooks/useOrders';
import { useAuthStore } from '@/stores/authStore';

export const Route = createFileRoute('/orders/')({
  component: OrdersPage
});

const STATUS_STYLES: Record<OrderStatus, string> = {
  pending: 'bg-accent text-accent-foreground',
  paid: 'bg-primary/10 text-primary',
  shipped: 'bg-primary/10 text-primary',
  delivered: 'bg-primary/10 text-primary',
  cancelled: 'bg-destructive/10 text-destructive'
};

function OrdersPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useOrders(page);

  const search = new URLSearchParams(window.location.search);
  const placedId = search.get('placed');

  useEffect(() => {
    if (!accessToken) {
      window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
    }
  }, [accessToken]);

  if (!accessToken) return null;

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 flex items-center gap-2 text-xl font-semibold tracking-tight">
        <HugeiconsIcon icon={Package01Icon} size={20} />
        Your orders
      </h1>

      {placedId && (
        <div className="mb-4 rounded-md border border-primary/30 bg-primary/10 px-3 py-2 text-xs text-primary">
          Order placed successfully.
        </div>
      )}

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {isError && <p className="text-sm text-destructive">Failed to load orders.</p>}
      {data && data.items.length === 0 && (
        <p className="text-sm text-muted-foreground">You haven't placed any orders yet.</p>
      )}

      <div className="flex flex-col gap-3">
        {data?.items.map((order) => (
          <Card
            key={order.id}
            className={order.id === placedId ? 'border-primary/50' : 'border-border/70'}
          >
            <CardContent className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-foreground">Order #{order.id.slice(-8)}</p>
                  <p className="text-[0.7rem] text-muted-foreground">
                    {new Date(order.created_at).toLocaleString()}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-[0.65rem] font-medium capitalize ${STATUS_STYLES[order.status]}`}
                >
                  {order.status}
                </span>
              </div>

              <ul className="flex flex-col gap-1">
                {order.items.map((item) => (
                  <li key={item.product_id} className="flex justify-between text-xs text-muted-foreground">
                    <span>
                      {item.name} × {item.qty}
                    </span>
                    <span>${item.price * item.qty}</span>
                  </li>
                ))}
              </ul>

              <div className="flex items-center justify-between border-t border-border pt-2">
                <span className="text-xs text-muted-foreground">Total</span>
                <span className="text-sm font-semibold text-foreground">${order.total}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {data && data.total > data.page_size && (
        <div className="mt-6 flex items-center justify-center gap-3">
          <Button
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Previous
          </Button>
          <span className="text-xs text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </main>
  );
}
