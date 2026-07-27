import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: HomePage
});

function HomePage() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold tracking-tight">Home</h1>
      <p className="text-sm text-muted-foreground">Vite + React + TanStack ready.</p>
    </main>
  );
}
