import type { App } from '@modelcontextprotocol/ext-apps';
import { ProductCard, type ProductCardProduct } from '@ecom/ui-kit';

interface ProductGridProps {
  app: App;
  products: ProductCardProduct[];
}

const MAX_VISIBLE = 10;

export function ProductGrid({ app, products }: ProductGridProps) {
  if (products.length === 0) {
    return <p className="p-4 text-sm text-muted-foreground">No products found.</p>;
  }

  const visible = products.slice(0, MAX_VISIBLE);

  return (
    <div className="flex gap-3 overflow-x-auto p-3">
      {visible.map((product) => (
        <ProductCard
          key={product.id}
          className="w-36 shrink-0"
          product={product}
          onAddToCart={() => {
            app
              .callServerTool({ name: 'add_to_cart', arguments: { product_id: product.id, qty: 1 } })
              .catch(console.error);
          }}
        />
      ))}
    </div>
  );
}
