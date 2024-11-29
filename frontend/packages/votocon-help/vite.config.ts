import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5176
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
