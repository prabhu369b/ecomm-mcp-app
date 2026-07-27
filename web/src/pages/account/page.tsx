import { useEffect, useState, type FormEvent } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { HugeiconsIcon } from '@hugeicons/react';
import { UserAccountIcon, LaptopIcon, Logout01Icon, Delete02Icon } from '@hugeicons/core-free-icons';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useCurrentUser, useUpdateProfile } from '@/hooks/useCurrentUser';
import { useSessions, useRevokeSession, useRevokeAllSessions } from '@/hooks/useSessions';
import { useAuthStore } from '@/stores/authStore';
import { ApiError } from '@/utils/api';

export const Route = createFileRoute('/account/')({
  component: AccountPage
});

function AccountPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const clear = useAuthStore((s) => s.clear);

  useEffect(() => {
    if (!accessToken) {
      window.location.assign(`/app/login?next=${encodeURIComponent(window.location.href)}`);
    }
  }, [accessToken]);

  if (!accessToken) return null;

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 flex items-center gap-2 text-xl font-semibold tracking-tight">
        <HugeiconsIcon icon={UserAccountIcon} size={20} />
        Account
      </h1>

      <div className="flex flex-col gap-6">
        <ProfileSection />
        <DevicesSection onSignedOutEverywhere={() => { clear(); window.location.assign('/app/login'); }} />
      </div>
    </main>
  );
}

function ProfileSection() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setName(user.name);
      setUsername(user.username);
    }
  }, [user]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaved(false);
    try {
      await updateProfile.mutateAsync({ name, username });
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Update failed');
    }
  }

  return (
    <Card className="border-border/70">
      <CardHeader>
        <CardTitle>Profile</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {user && (
          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email" className="text-xs font-medium">Email</Label>
              <Input id="email" value={user.email} disabled className="h-9 text-sm" />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="name" className="text-xs font-medium">Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="h-9 text-sm"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="username" className="text-xs font-medium">Username</Label>
              <Input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="h-9 text-sm"
              />
            </div>

            {error && <p className="text-xs text-destructive">{error}</p>}
            {saved && !error && <p className="text-xs text-primary">Saved.</p>}

            <Button type="submit" disabled={updateProfile.isPending} className="self-start">
              {updateProfile.isPending ? 'Saving…' : 'Save changes'}
            </Button>
          </form>
        )}
      </CardContent>
    </Card>
  );
}

function DevicesSection({ onSignedOutEverywhere }: { onSignedOutEverywhere: () => void }) {
  const { data: sessions, isLoading, isError } = useSessions();
  const revokeSession = useRevokeSession();
  const revokeAll = useRevokeAllSessions();

  async function handleSignOutOthers() {
    await revokeAll.mutateAsync(true);
  }

  async function handleSignOutEverywhere() {
    await revokeAll.mutateAsync(false);
    onSignedOutEverywhere();
  }

  return (
    <Card className="border-border/70">
      <CardHeader>
        <CardTitle>Devices</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {isError && <p className="text-sm text-destructive">Failed to load devices.</p>}

        <div className="flex flex-col divide-y divide-border">
          {sessions?.map((session) => (
            <div key={session.session_id} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
              <HugeiconsIcon icon={LaptopIcon} size={18} className="shrink-0 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm text-foreground">
                  {session.device}
                  {session.current && (
                    <span className="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-[0.65rem] font-medium text-primary">
                      This device
                    </span>
                  )}
                </p>
                <p className="text-[0.7rem] text-muted-foreground">
                  {session.ip_address} · last active {new Date(session.last_used_at).toLocaleString()}
                </p>
              </div>
              {!session.current && (
                <Button
                  size="icon-sm"
                  variant="ghost"
                  disabled={revokeSession.isPending}
                  aria-label="Sign out device"
                  onClick={() => revokeSession.mutate(session.session_id)}
                >
                  <HugeiconsIcon icon={Delete02Icon} size={14} />
                </Button>
              )}
            </div>
          ))}
        </div>

        <div className="mt-2 flex gap-2 border-t border-border pt-4">
          <Button
            variant="outline"
            size="sm"
            disabled={revokeAll.isPending}
            onClick={handleSignOutOthers}
          >
            Sign out other devices
          </Button>
          <Button
            variant="destructive"
            size="sm"
            disabled={revokeAll.isPending}
            onClick={handleSignOutEverywhere}
          >
            <HugeiconsIcon icon={Logout01Icon} size={14} />
            Sign out everywhere
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
