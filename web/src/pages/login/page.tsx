import { useState, type FormEvent } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
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
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-b from-muted/40 to-background p-6">
      <Card className="w-full max-w-sm border-border/60 shadow-lg shadow-black/[0.03]">
        <CardHeader>
          <span className="mb-1 inline-flex size-9 items-center justify-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground">
            E
          </span>
          <CardTitle className="text-lg">Sign in to Ecom</CardTitle>
          <CardDescription>Enter your credentials to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
            <Button type="submit" disabled={loading} className="mt-1">
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
