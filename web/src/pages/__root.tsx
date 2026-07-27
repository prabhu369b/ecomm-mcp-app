import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import type { QueryClient } from '@tanstack/react-query';
import { ThemeToggle } from '@/components/layout/ThemeToggle';

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout
});

function RootLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3">
        <span className="flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="inline-flex size-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
            E
          </span>
          Ecom
        </span>
        <ThemeToggle />
      </header>
      <Outlet />
    </div>
  );
}
