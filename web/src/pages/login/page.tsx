import { useState, type FormEvent } from 'react';
import { createFileRoute, Link } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { callApi, ApiError } from '@/utils/api';
import { useAuthStore } from '@/stores/authStore';
import type { LoginResponse } from './types';

export const Route = createFileRoute('/login/')({
  component: LoginPage
});

function LoginPage() {
  const setSession = useAuthStore((s) => s.setSession);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const search = new URLSearchParams(window.location.search);
  const next = search.get('next') ?? '/app';

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await callApi<LoginResponse>('/auth/sign-in', {
        method: 'POST',
        body: JSON.stringify({ email, password, device: navigator.userAgent })
      });
      setSession({ accessToken: data.access_token, refreshToken: data.refresh_token });
      window.location.assign(next);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-[calc(100dvh-3.5rem)] items-center justify-center bg-muted/30 p-6">
      <div className="w-full max-w-[380px]">
        <div className="mb-6 flex flex-col items-center gap-3">
          <span className="inline-flex size-10 items-center justify-center rounded-xl bg-primary font-heading text-base font-semibold text-primary-foreground">
            E
          </span>
          <div className="text-center">
            <h1 className="text-lg font-semibold tracking-tight text-foreground">Sign in to Ecom</h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Welcome back — enter your details to continue
            </p>
          </div>
        </div>

        <Card className="border-border/70 py-6 shadow-sm">
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email" className="text-xs font-medium text-foreground">
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  required
                  autoFocus
                  className="h-9 rounded-md text-sm"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="password" className="text-xs font-medium text-foreground">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  required
                  className="h-9 rounded-md text-sm"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && (
                <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={loading}
                size="lg"
                className="mt-1 h-9 w-full rounded-md text-sm"
              >
                {loading ? 'Signing in…' : 'Sign in'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Protected by{' '}
          <Link to="/" className="font-medium text-foreground hover:underline">
            Ecom
          </Link>{' '}
          OAuth 2.1
        </p>
      </div>
    </main>
  );
}
