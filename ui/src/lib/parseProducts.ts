import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { ProductCardProduct } from '@ecom/ui-kit';

function toProduct(raw: unknown): ProductCardProduct | null {
  if (typeof raw !== 'object' || raw === null) return null;
  const p = raw as Record<string, unknown>;
  if (typeof p.id === 'undefined' || typeof p.name === 'undefined') return null;

  return {
    id: String(p.id),
    name: String(p.name),
    price: Number(p.price),
    stock: Number(p.stock),
    rating: typeof p.rating === 'number' ? p.rating : null,
    discount_percentage: typeof p.discount_percentage === 'number' ? p.discount_percentage : null,
    thumbnail: typeof p.thumbnail === 'string' ? p.thumbnail : null
  };
}

/**
 * Normalizes our Python MCP tool results into a flat product list.
 *
 * FastMCP has no single fixed shape here: a tool returning `list[dict]`
 * (list_products) emits one separate TextContent block per item, while a
 * tool returning a page object (search_products: {items, total, ...})
 * emits a single TextContent block with that whole object as JSON. Handle
 * both — parse every text block, and for each parsed value: use it as an
 * array of products, pull `.items` out of it, or treat it as one product.
 */
export function parseProducts(result: CallToolResult): ProductCardProduct[] {
  const products: ProductCardProduct[] = [];

  for (const block of result.content ?? []) {
    if (block.type !== 'text') continue;

    let data: unknown;
    try {
      data = JSON.parse(block.text);
    } catch {
      continue;
    }

    if (Array.isArray(data)) {
      for (const raw of data) {
        const product = toProduct(raw);
        if (product) products.push(product);
      }
      continue;
    }

    if (data && typeof data === 'object' && Array.isArray((data as { items?: unknown }).items)) {
      for (const raw of (data as { items: unknown[] }).items) {
        const product = toProduct(raw);
        if (product) products.push(product);
      }
      continue;
    }

    const single = toProduct(data);
    if (single) products.push(single);
  }

  return products;
}
