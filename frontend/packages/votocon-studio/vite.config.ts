import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5174
  },
  build: {
    outDir: 'dist',
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
