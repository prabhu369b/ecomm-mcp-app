import { HugeiconsIcon } from '@hugeicons/react';
import { StarIcon, StarHalfIcon } from '@hugeicons/core-free-icons';

export function StarRating({ rating, size = 13 }: { rating: number; size?: number }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;

  return (
    <div className="flex items-center gap-0.5" aria-label={`${rating.toFixed(1)} out of 5 stars`}>
      {Array.from({ length: 5 }).map((_, i) => {
        const icon = i < full ? StarIcon : i === full && half ? StarHalfIcon : StarIcon;
        const filled = i < full || (i === full && half);
        return (
          <HugeiconsIcon
            key={i}
            icon={icon}
            size={size}
            className={filled ? 'text-amber-500' : 'text-muted-foreground/40'}
          />
        );
      })}
    </div>
  );
}
