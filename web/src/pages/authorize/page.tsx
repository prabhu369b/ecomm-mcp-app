import { useEffect, useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { callApi, ApiError } from '@/utils/api';
import { useAuthStore } from '@/stores/authStore';
import type { AuthorizationResult, ConsentApprovalResult } from './types';

export const Route = createFileRoute('/authorize/')({
  component: AuthorizePage
});

function goToLogin() {
  const next = encodeURIComponent(window.location.href);
  window.location.assign(`/app/login?next=${next}`);
}

function AuthorizePage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const clear = useAuthStore((s) => s.clear);
  const [result, setResult] = useState<AuthorizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deciding, setDeciding] = useState(false);
  const [decision, setDecision] = useState<'allowed' | 'denied' | null>(null);

  useEffect(() => {
    if (!accessToken) {
      goToLogin();
      return;
    }

    const query = window.location.search;
    callApi<AuthorizationResult>(`/oauth/authorize${query}`)
      .then((data) => {
        if (data.action === 'login') {
          clear();
          goToLogin();
          return;
        }
        setResult(data);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Something went wrong'));
  }, [accessToken, clear]);

  async function decide(approved: boolean) {
    if (!result?.request_id) return;
    setDeciding(true);
    setError(null);
    try {
      const { redirect_uri } = await callApi<ConsentApprovalResult>('/oauth/authorize/consent', {
        method: 'POST',
        body: JSON.stringify({ request_id: result.request_id, approved })
      });
      setDecision(approved ? 'allowed' : 'denied');
      window.location.assign(redirect_uri);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong');
    } finally {
      setDeciding(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Authorize access</CardTitle>
          {result?.client_name && (
            <CardDescription>
              <strong>{result.client_name}</strong> wants to access your account
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {error && <p className="text-xs text-destructive">{error}</p>}
          {!error && !result && !decision && (
            <p className="text-xs text-muted-foreground">Checking request…</p>
          )}
          {decision && (
            <p className="text-xs text-muted-foreground">
              {decision === 'allowed' ? 'Access granted.' : 'Access denied.'} You may close this window.
            </p>
          )}
          {result && !decision && (
            <ul className="flex flex-col gap-1 text-xs text-muted-foreground">
              {result.scopes.map((scope) => (
                <li key={scope}>• {scope}</li>
              ))}
            </ul>
          )}
        </CardContent>
        {result && !decision && (
          <CardFooter className="justify-end gap-2">
            <Button variant="outline" disabled={deciding} onClick={() => decide(false)}>
              Deny
            </Button>
            <Button disabled={deciding} onClick={() => decide(true)}>
              Allow
            </Button>
          </CardFooter>
        )}
      </Card>
    </main>
  );
}
