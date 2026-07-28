import type { App } from '@modelcontextprotocol/ext-apps';
import { ProductCard, type ProductCardProduct } from '@ecom/ui-kit';

interface ProductGridProps {
  app: App;
  products: ProductCardProduct[];
}

export function ProductGrid({ app, products }: ProductGridProps) {
  if (products.length === 0) {
    return <p className="p-4 text-sm text-muted-foreground">No products found.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-3 p-3 sm:grid-cols-3">
      {products.map((product) => (
        <ProductCard
          key={product.id}
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
