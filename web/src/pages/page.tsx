import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { HugeiconsIcon } from '@hugeicons/react';
import { Search01Icon, ShoppingCart01Icon } from '@hugeicons/core-free-icons';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { callApi } from '@/utils/api';
import { useAddToCart } from '@/hooks/useCart';
import { useAuthStore } from '@/stores/authStore';

export const Route = createFileRoute('/')({
  component: HomePage
});

interface ProductResponse {
  id: string;
  name: string;
  category_id: string;
  price: number;
  stock: number;
  description: string;
}

interface ProductListResponse {
  items: ProductResponse[];
  total: number;
  page: number;
  page_size: number;
}

const PAGE_SIZE = 20;

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}

function HomePage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const q = useDebouncedValue(search, 300);
  const accessToken = useAuthStore((s) => s.accessToken);
  const addToCart = useAddToCart();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['products', q, page],
    queryFn: () =>
      callApi<ProductListResponse>(
        `/products?q=${encodeURIComponent(q)}&page=${page}&page_size=${PAGE_SIZE}`
      ),
    placeholderData: keepPreviousData
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <main className="mx-auto max-w-5xl p-6">
      <div className="mb-6 flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Products</h1>
        <p className="text-sm text-muted-foreground">Browse the catalog</p>
      </div>

      <div className="relative mb-6 max-w-sm">
        <HugeiconsIcon
          icon={Search01Icon}
          size={14}
          className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          placeholder="Search products…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="h-9 pl-8 text-sm"
        />
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {isError && <p className="text-sm text-destructive">Failed to load products.</p>}

      {data && data.items.length === 0 && (
        <p className="text-sm text-muted-foreground">No products found.</p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.items.map((product) => (
          <Card key={product.id} className="border-border/70">
            <CardContent className="flex flex-col gap-2">
              <div className="flex items-start justify-between gap-2">
                <h2 className="text-sm font-medium text-foreground">{product.name}</h2>
                <span
                  className={
                    product.stock > 0
                      ? 'shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-[0.65rem] font-medium text-primary'
                      : 'shrink-0 rounded-full bg-destructive/10 px-2 py-0.5 text-[0.65rem] font-medium text-destructive'
                  }
                >
                  {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </span>
              </div>
              <p className="line-clamp-2 text-xs text-muted-foreground">{product.description}</p>
              <div className="mt-1 flex items-center justify-between">
                <p className="text-sm font-semibold text-foreground">${product.price}</p>
                <Button
                  size="sm"
                  disabled={product.stock <= 0 || addToCart.isPending}
                  onClick={() => {
                    if (!accessToken) {
                      window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
                      return;
                    }
                    addToCart.mutate({ productId: product.id, qty: 1 });
                  }}
                >
                  <HugeiconsIcon icon={ShoppingCart01Icon} size={13} />
                  Add to cart
                </Button>
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
