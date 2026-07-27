import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import type { QueryClient } from '@tanstack/react-query';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { AccountMenu } from '@/components/layout/AccountMenu';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/stores/authStore';

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout
});

function RootLayout() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return (
    <div className="min-h-screen bg-background">
      <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
        <span className="flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="inline-flex size-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
            E
          </span>
          Ecom
        </span>
        <div className="flex items-center gap-3">
          {accessToken ? (
            <AccountMenu />
          ) : (
            <>
              <Button variant="ghost" render={<a href="/app/login" />}>
                Sign in
              </Button>
              <Button render={<a href="/app/login" />}>Sign up</Button>
            </>
          )}
          <ThemeToggle />
        </div>
      </header>
      <Outlet />
    </div>
  );
}
