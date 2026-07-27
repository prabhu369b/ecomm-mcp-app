import { HugeiconsIcon } from '@hugeicons/react';
import { Sun02Icon, Moon02Icon } from '@hugeicons/core-free-icons';
import { useThemeStore } from '@/stores/themeStore';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();
  return (
    <button
      aria-label="Toggle theme"
      className="flex size-8 items-center justify-center rounded-md border border-border text-muted-foreground hover:text-foreground"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      <HugeiconsIcon icon={theme === 'dark' ? Sun02Icon : Moon02Icon} size={16} />
    </button>
  );
}
