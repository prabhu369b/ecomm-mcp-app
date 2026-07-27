import { useThemeStore } from '@/stores/themeStore';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();
  return (
    <button
      aria-label="Toggle theme"
      className="rounded-md border border-border px-3 py-1.5 text-sm"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? 'Light' : 'Dark'}
    </button>
  );
}
