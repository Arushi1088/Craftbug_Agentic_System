
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '',
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    allowedHosts: ['*.trycloudflare.com', 'leasing-gba-om-prior.trycloudflare.com'],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  preview: {
    port: 4173,
    host: true,
    allowedHosts: ['*.trycloudflare.com', 'leasing-gba-om-prior.trycloudflare.com'],
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
