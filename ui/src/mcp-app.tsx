/**
 * @file MCP App entry point — the connection shell. Per-view rendering
 * lives in ./components (ProductGrid, using the shared @ecom/ui-kit
 * ProductCard also used by the web storefront).
 */
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { ProductGrid } from "./components/ProductGrid";
import { parseProducts } from "./lib/parseProducts";

function EcomApp() {
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);

  const { app, error } = useApp({
    appInfo: { name: "Ecom MCP App", version: "0.1.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.ontoolinput = async (input) => {
        console.info("Received tool call input:", input);
      };

      app.ontoolresult = async (result) => {
        console.info("Received tool call result:", result);
        setToolResult(result);
      };

      app.ontoolcancelled = (params) => {
        console.info("Tool call cancelled:", params.reason);
      };

      app.onerror = console.error;

      app.onteardown = async () => {
        return {};
      };
    }
  });

  if (error) return <div><strong>ERROR:</strong> {error.message}</div>;
  if (!app) return <div>Connecting…</div>;

  const products = toolResult ? parseProducts(toolResult) : [];

  return <ProductGrid app={app} products={products} />;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <EcomApp />
  </StrictMode>
);
