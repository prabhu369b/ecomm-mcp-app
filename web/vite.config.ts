import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { tanstackRouter } from '@tanstack/router-plugin/vite';

export default defineConfig({
  plugins: [
    tanstackRouter({
      target: 'react',
      autoCodeSplitting: true,
      routesDirectory: './src/pages',
      generatedRouteTree: './src/routeTree.gen.ts',
      routeToken: 'layout',
      indexToken: 'page',
      routeFileIgnorePrefix: '-',
      routeFileIgnorePattern:
        '(^|/)(components|hooks|utils|stores|store|queries|mutations|schemas|api|mocks|types|constants|context|contexts|lib|tests|__tests__|stories)(/|$)|(^|/)(components|hooks|utils|stores|queries|mutations|schemas|api|mocks|types|constants|contexts|lib)\\.(ts|tsx)$|\\.test\\.(ts|tsx)$|\\.spec\\.(ts|tsx)$|\\.stories\\.(ts|tsx)$'
    }),
    react(),
    tailwindcss()
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') }
  },
  base: '/app/',
  server: {
    port: 3000,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/oauth': 'http://localhost:8000',
      '/products': 'http://localhost:8000',
      '/v2': 'http://localhost:8000',
      '/cart': 'http://localhost:8000',
      '/orders': 'http://localhost:8000'
    }
  }
});
