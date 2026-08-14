import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@packages': path.resolve(__dirname, "../packages"),
      '@api': path.resolve(__dirname, '../packages/api-client/src/index.ts'),
    },
  },
  server: {
    port: 5174,
    fs: { allow: ['..'] },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});