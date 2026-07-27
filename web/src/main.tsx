import { StrictMode } from 'react';
import { createRoot, hydrateRoot } from 'react-dom/client';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import './styles/index.css';
// Import the generated route tree
import { routeTree } from '@/routeTree.gen';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';

// Create a new router instance
const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreload: 'intent',
  basepath: '/app'
});

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

// Render the app — hydrate when the page was prerendered at build time
const rootElement = document.getElementById('root')!;
const app = (
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>
);
if (rootElement.innerHTML) {
  // let loaders finish so the first client render matches the static HTML
  router.load().then(() => hydrateRoot(rootElement, app));
} else {
  createRoot(rootElement).render(app);
}
