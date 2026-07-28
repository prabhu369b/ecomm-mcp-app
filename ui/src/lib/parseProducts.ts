import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { ProductCardProduct } from '@ecom/ui-kit';

/**
 * Our Python MCP tools (list_products/search_products) return either a bare
 * array of products or a {items, total, page, page_size} page — normalize
 * both into the flat product list the UI renders.
 */
export function parseProducts(result: CallToolResult): ProductCardProduct[] {
  const textBlock = result.content?.find((block) => block.type === 'text');
  if (!textBlock || textBlock.type !== 'text') return [];

  let data: unknown;
  try {
    data = JSON.parse(textBlock.text);
  } catch {
    return [];
  }

  const rawItems = Array.isArray(data)
    ? data
    : Array.isArray((data as { items?: unknown })?.items)
      ? (data as { items: unknown[] }).items
      : [];

  return rawItems.map((raw): ProductCardProduct => {
    const p = raw as Record<string, unknown>;
    return {
      id: String(p.id),
      name: String(p.name),
      price: Number(p.price),
      stock: Number(p.stock),
      rating: typeof p.rating === 'number' ? p.rating : null,
      discount_percentage: typeof p.discount_percentage === 'number' ? p.discount_percentage : null,
      thumbnail: typeof p.thumbnail === 'string' ? p.thumbnail : null
    };
  });
}
