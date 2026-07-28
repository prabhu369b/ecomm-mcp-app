import { HugeiconsIcon } from '@hugeicons/react';
import { ShoppingCart01Icon } from '@hugeicons/core-free-icons';
import { cn } from '../lib/cn';
import { StarRating } from './StarRating';

export interface ProductCardProduct {
  id: string;
  name: string;
  price: number; // cents
  stock: number;
  rating?: number | null;
  discount_percentage?: number | null;
  thumbnail?: string | null;
}

export interface ProductCardProps {
  product: ProductCardProduct;
  onAddToCart?: () => void;
  addToCartLabel?: string;
  addToCartDisabled?: boolean;
  addToCartPending?: boolean;
  className?: string;
}

function formatPrice(cents: number): string {
  return (cents / 100).toFixed(2);
}

export function ProductCard({
  product,
  onAddToCart,
  addToCartLabel = 'Add to cart',
  addToCartDisabled = false,
  addToCartPending = false,
  className
}: ProductCardProps) {
  const hasDiscount = !!product.discount_percentage && product.discount_percentage > 0;
  const originalPrice = hasDiscount
    ? product.price / (1 - (product.discount_percentage as number) / 100)
    : null;

  return (
    <div
      className={cn(
        'flex flex-col overflow-hidden rounded-lg border border-border/70 bg-card text-card-foreground',
        className
      )}
    >
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

      <div className="flex flex-col gap-1 p-2.5 pb-4">
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

        <button
          type="button"
          disabled={product.stock <= 0 || addToCartDisabled || addToCartPending}
          onClick={onAddToCart}
          className="mt-1 flex h-9 w-full items-center justify-center gap-1 rounded-md bg-primary px-2 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/80 disabled:pointer-events-none disabled:opacity-50"
        >
          <HugeiconsIcon icon={ShoppingCart01Icon} size={13} />
          {addToCartPending ? 'Adding…' : addToCartLabel}
        </button>
      </div>
    </div>
  );
}
