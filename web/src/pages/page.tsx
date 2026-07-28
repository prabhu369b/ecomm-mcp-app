import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { HugeiconsIcon } from '@hugeicons/react';
import { Search01Icon, ShoppingCart01Icon } from '@hugeicons/core-free-icons';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { StarRating } from '@/components/ui/star-rating';
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

function formatPrice(cents: number): string {
  return (cents / 100).toFixed(2);
}

function ProductCard({ product }: { product: ProductResponse }) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const addToCart = useAddToCart();

  const hasDiscount = !!product.discount_percentage && product.discount_percentage > 0;
  const originalPrice = hasDiscount
    ? product.price / (1 - (product.discount_percentage as number) / 100)
    : null;

  return (
    <Card className="flex flex-col overflow-hidden border-border/70 py-0">
      <div className="relative aspect-square w-full shrink-0 bg-white">
        {product.thumbnail ? (
          <img
            src={product.thumbnail}
            alt={product.name}
            loading="lazy"
            className="size-full object-contain p-2"
          />
        ) : (
          <div className="flex size-full items-center justify-center text-xs text-muted-foreground">
            No image
          </div>
        )}
        {hasDiscount && (
          <span className="absolute left-1.5 top-1.5 rounded-full bg-destructive px-1.5 py-0.5 text-[0.6rem] font-semibold text-destructive-foreground">
            -{Math.round(product.discount_percentage as number)}%
          </span>
        )}
      </div>

      <CardContent className="flex flex-col gap-1 p-2.5 pb-4">
        <h2 className="line-clamp-2 text-xs font-medium leading-snug text-foreground">
          {product.name}
        </h2>

        {product.rating != null && <StarRating rating={product.rating} size={11} />}

        <div className="mt-auto flex items-baseline gap-1.5 pt-1">
          <span className="text-sm font-semibold text-foreground">${formatPrice(product.price)}</span>
          {originalPrice && (
            <span className="text-[0.7rem] text-muted-foreground line-through">
              ${formatPrice(Math.round(originalPrice))}
            </span>
          )}
        </div>

        <Button
          size="default"
          className="mt-1 w-full"
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
      </CardContent>
    </Card>
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
          <ProductCard key={product.id} product={product} />
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
