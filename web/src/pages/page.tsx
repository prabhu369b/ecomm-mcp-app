import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { HugeiconsIcon } from '@hugeicons/react';
import { Search01Icon } from '@hugeicons/core-free-icons';
import { ProductCard } from '@ecom/ui-kit';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
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
  brand: string | null;
  rating: number | null;
  discount_percentage: number | null;
  thumbnail: string | null;
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

function ProductGridCard({ product }: { product: ProductResponse }) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const addToCart = useAddToCart();

  return (
    <ProductCard
      product={product}
      addToCartPending={addToCart.isPending}
      onAddToCart={() => {
        if (!accessToken) {
          window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
          return;
        }
        addToCart.mutate({ productId: product.id, qty: 1 });
      }}
    />
  );
}

function HomePage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const q = useDebouncedValue(search, 300);

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
    <main className="mx-auto max-w-6xl p-6">
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

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6">
        {data?.items.map((product) => (
          <ProductGridCard key={product.id} product={product} />
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
