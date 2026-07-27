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
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <span className="text-sm font-medium">App</span>
        <ThemeToggle />
      </header>
      <Outlet />
    </div>
  );
}
