import { Menu } from '@base-ui/react/menu';
import { useAuthStore } from '@/stores/authStore';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { callApi } from '@/utils/api';

export function AccountMenu() {
  const clear = useAuthStore((s) => s.clear);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const { data: user } = useCurrentUser();

  async function handleLogout() {
    if (refreshToken) {
      await callApi('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken })
      }).catch(() => {});
    }
    clear();
    window.location.assign('/app/login');
  }

  const initial = user?.name?.[0]?.toUpperCase() ?? '·';

  return (
    <Menu.Root>
      <Menu.Trigger className="flex size-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring/30">
        {initial}
      </Menu.Trigger>
      <Menu.Portal>
        <Menu.Positioner sideOffset={8} align="end" className="z-50">
          <Menu.Popup className="min-w-48 rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md outline-none">
            {user && (
              <div className="border-b border-border px-2.5 py-2">
                <p className="truncate text-xs font-medium text-foreground">{user.name}</p>
                <p className="truncate text-[0.7rem] text-muted-foreground">{user.email}</p>
              </div>
            )}
            <Menu.Item
              render={<a href="/app/cart" />}
              className="flex cursor-pointer items-center rounded-sm px-2.5 py-1.5 text-xs data-[highlighted]:bg-muted"
            >
              Cart
            </Menu.Item>
            <Menu.Item
              render={<a href="/app/orders" />}
              className="flex cursor-pointer items-center rounded-sm px-2.5 py-1.5 text-xs data-[highlighted]:bg-muted"
            >
              Orders
            </Menu.Item>
            <Menu.Item
              render={<a href="/app/account" />}
              className="flex cursor-pointer items-center rounded-sm px-2.5 py-1.5 text-xs data-[highlighted]:bg-muted"
            >
              Account
            </Menu.Item>
            <Menu.Item
              onClick={handleLogout}
              className="flex cursor-pointer items-center rounded-sm px-2.5 py-1.5 text-xs text-destructive data-[highlighted]:bg-destructive/10"
            >
              Log out
            </Menu.Item>
          </Menu.Popup>
        </Menu.Positioner>
      </Menu.Portal>
    </Menu.Root>
  );
}
